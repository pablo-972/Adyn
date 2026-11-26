from collections.abc import Callable

from config.paths import WORK_PATH
from core.exceptions import ToolError
from core.orchestrator.loader import load_config
from core.orchestrator.models import AdynConfig, AdynRequest, Command
from core.tools import burp, frida, mobsf
from core.tools.android.adb import Adb
from core.tools.android.models import Device
from core.tools.android.sdk import Sdk
from core.utils.logger import get_logger


logger = get_logger(__name__)

DeviceChooser = Callable[[list[Device]], list[Device]]


class Orchestrator:
    """Runs each lab command over the selected devices."""

    def __init__(
        self,
        config: AdynConfig,
        request: AdynRequest,
        *,
        choose: DeviceChooser,
    ) -> None:
        WORK_PATH.mkdir(parents=True, exist_ok=True)

        self.config = config
        self.request = request
        self.devices = config.select(request.devices)
        self.sdk = Sdk(config.sdk)
        # Without device names the command acts on the whole lab, so the
        # shared services (Burp, MobSF) are stopped too.
        self.whole_lab = not request.devices
        self.choose = choose

        self._adb: dict[str, Adb] = {}
        self._root_access: dict[str, bool] = {}


    def setup(self) -> None:
        """Install the system images and create the missing emulators."""
        emulators = self._get_emulators(self.config.devices)
        self._install_images(emulators)
        self._create_avds(emulators)

    def up(self) -> None:
        """Boot the emulators, then start Burp, Frida and MobSF."""
        options = self.request.up
        self._boot_emulators(self._get_emulators(self.devices))

        running = self._get_running_devices()
        if options.burp:
            self._attach_burp(running)

        if options.frida:
            self._start_frida(running)

        if options.mobsf:
            self._start_mobsf()

    def down(self) -> None:
        """Stop Frida, remove the proxy, stop the emulators and services."""
        running = self._get_running_devices()
        self._stop_frida(running)
        self._detach_burp(running)
        self._stop_emulators(running)

        if self.whole_lab:
            mobsf.stop()

    def start_android(self) -> None:
        """Boot the emulators only, asking which ones without names."""
        self._boot_emulators(self._choose_emulators())

    def stop_android(self) -> None:
        """Remove the proxy of the emulators and stop them."""
        running = self._get_emulators(self._get_running_devices())

        # The proxy setting survives a reboot: left behind, the emulator would
        # have no network the next time it boots without Burp.
        for device in running:
            burp.disconnect(self._get_adb(device), self.config.burp)

        self._stop_emulators(running)

    def start_burp(self) -> None:
        self._attach_burp(self._get_running_devices())

    def stop_burp(self) -> None:
        self._detach_burp(self._get_running_devices())

    def start_frida(self) -> None:
        self._start_frida(self._get_running_devices())

    def stop_frida(self) -> None:
        self._stop_frida(self._get_running_devices())

    def start_mobsf(self) -> None:
        mobsf.start(self.config.mobsf)

    def stop_mobsf(self) -> None:
        mobsf.stop()

    def scan(self) -> None:
        """Start MobSF, analyze the app and save its reports."""
        app = self.request.app
        if app is None:
            raise ToolError("no app given to scan")

        options = self.config.mobsf
        mobsf.start(options)
        reports = mobsf.analyze(options, app, output=self.request.output)

        for report in reports:
            logger.info(f"mobsf: report saved to {report}")


    def _install_images(self, emulators: list[Device]) -> None:
        images = sorted({str(device.image) for device in emulators})
        if not images:
            return

        logger.info(f"installing system images: {', '.join(images)}")
        self.sdk.install_images(images)

    def _create_avds(self, emulators: list[Device]) -> None:
        existing = self.sdk.list_avds()

        for device in emulators:
            if device.avd in existing:
                logger.info(f"{device.name}: AVD {device.avd} already exists")
                continue

            self.sdk.create_avd(device)
            logger.info(f"{device.name}: created AVD {device.avd}")

    def _choose_emulators(self) -> list[Device]:
        emulators = self._get_emulators(self.devices)
        if self.request.devices or len(emulators) <= 1:
            return emulators

        return self.choose(emulators)

    def _boot_emulators(self, emulators: list[Device]) -> None:
        for device in emulators:
            if self._get_adb(device).is_online():
                continue

            self.sdk.start_emulator(device)
            logger.info(
                f"{device.name}: booting {device.avd} ({device.adb_serial})"
            )

        for device in emulators:
            logger.info(f"{device.name}: waiting for boot...")
            self._get_adb(device).wait_until_booted()

    def _stop_emulators(self, devices: list[Device]) -> None:
        for device in self._get_emulators(devices):
            self._get_adb(device).run("emu", "kill", check=False)
            logger.info(f"{device.name}: emulator stopped")

    def _attach_burp(self, devices: list[Device]) -> None:
        burp.start(self.config.burp)
        cert = burp.fetch_ca_certificate(self.config.burp)

        for device in devices:
            burp.connect(
                self._get_adb(device),
                self.config.burp,
                cert,
                rooted=self._has_root(device),
            )

    def _detach_burp(self, devices: list[Device]) -> None:
        for device in devices:
            burp.disconnect(self._get_adb(device), self.config.burp)

        if self.whole_lab:
            burp.stop()

    def _start_frida(self, devices: list[Device]) -> None:
        for device in devices:
            if self._has_root(device):
                frida.start(self._get_adb(device))
            elif not device.rooted:
                logger.info(
                    f"{device.name}: not rooted, no frida-server "
                    "(use frida-gadget)"
                )

    def _stop_frida(self, devices: list[Device]) -> None:
        for device in devices:
            if not self._has_root(device):
                continue

            frida.stop(self._get_adb(device))
            logger.info(f"{device.name}: frida-server stopped")

    def _start_mobsf(self) -> None:
        # MobSF is the only part that needs Docker: without it, the rest of
        # the lab still works.
        try:
            mobsf.start(self.config.mobsf)
        except ToolError as exc:
            logger.warning(f"mobsf: not started: {exc}")

    def _get_running_devices(self) -> list[Device]:
        running = []

        for device in self.devices:
            if self._get_adb(device).is_online():
                running.append(device)
            else:
                logger.info(f"{device.name}: not running, skipped")

        return running

    @staticmethod
    def _get_emulators(devices: list[Device]) -> list[Device]:
        return [device for device in devices if device.is_emulator]

    def _get_adb(self, device: Device) -> Adb:
        if device.name not in self._adb:
            self._adb[device.name] = self.sdk.create_adb(device)

        return self._adb[device.name]

    def _has_root(self, device: Device) -> bool:
        """Whether the device gives root. Asked once per device."""
        if not device.rooted:
            return False

        if device.name not in self._root_access:
            has_root = self._get_adb(device).become_root()
            if not has_root:
                logger.warning(
                    f"{device.name}: marked as rooted but root was denied"
                )

            self._root_access[device.name] = has_root

        return self._root_access[device.name]


COMMANDS: dict[Command, Callable[[Orchestrator], None]] = {
    Command.SETUP: Orchestrator.setup,
    Command.UP: Orchestrator.up,
    Command.DOWN: Orchestrator.down,
    Command.START_ANDROID: Orchestrator.start_android,
    Command.START_BURP: Orchestrator.start_burp,
    Command.START_FRIDA: Orchestrator.start_frida,
    Command.START_MOBSF: Orchestrator.start_mobsf,
    Command.STOP_ANDROID: Orchestrator.stop_android,
    Command.STOP_BURP: Orchestrator.stop_burp,
    Command.STOP_FRIDA: Orchestrator.stop_frida,
    Command.STOP_MOBSF: Orchestrator.stop_mobsf,
    Command.SCAN: Orchestrator.scan,
}


def run(request: AdynRequest, *, choose: DeviceChooser) -> None:
    config = load_config(request.config_path)
    orchestrator = Orchestrator(config, request, choose=choose)

    COMMANDS[request.command](orchestrator)
