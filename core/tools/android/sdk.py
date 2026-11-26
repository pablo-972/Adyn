import subprocess
from pathlib import Path

from config.android import AVD_NO_CUSTOM_PROFILE, SDK_LICENSE_ANSWERS
from config.paths import LOG_PATH
from core.exceptions import ToolError
from core.tools.android.adb import Adb
from core.tools.android.models import Device
from core.utils.system import resolve_executable, spawn


class Sdk:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.env = {
            "ANDROID_HOME": str(root),
            "ANDROID_SDK_ROOT": str(root),
        }

        tools = root / "cmdline-tools" / "latest" / "bin"
        self.sdkmanager = resolve_executable(
            tools,
            "sdkmanager",
            windows_extension=".bat",
        )
        self.avdmanager = resolve_executable(
            tools,
            "avdmanager",
            windows_extension=".bat",
        )
        self.adb = resolve_executable(root / "platform-tools", "adb")
        self.emulator = resolve_executable(root / "emulator", "emulator")


    def create_adb(self, device: Device) -> Adb:
        self._require(self.adb)
        return Adb(self.adb, device.adb_serial)

    def install_images(self, images: list[str]) -> None:
        self._require(self.sdkmanager)

        try:
            subprocess.run(
                [str(self.sdkmanager), f"--sdk_root={self.root}", *images],
                input=SDK_LICENSE_ANSWERS,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise ToolError(
                f"sdkmanager failed with exit code {exc.returncode}"
            ) from exc

    def list_avds(self) -> set[str]:
        self._require(self.emulator)

        process = subprocess.run(
            [str(self.emulator), "-list-avds"],
            capture_output=True,
            text=True,
            check=False,
        )

        # The emulator may print log lines too; AVD names never contain spaces.
        lines = (line.strip() for line in process.stdout.splitlines())
        return {line for line in lines if line and " " not in line}

    def create_avd(self, device: Device) -> None:
        self._require(self.avdmanager)

        process = subprocess.run(
            self._build_create_avd_args(device),
            input=AVD_NO_CUSTOM_PROFILE,
            capture_output=True,
            text=True,
            check=False,
        )

        if process.returncode != 0:
            output = process.stdout + process.stderr
            raise ToolError(f"could not create AVD {device.avd}:\n{output}")

    def start_emulator(self, device: Device) -> None:
        self._require(self.emulator)

        args = self._build_emulator_args(device)
        spawn(args, LOG_PATH / f"{device.name}.log", env=self.env)


    def _build_create_avd_args(self, device: Device) -> list[str]:
        return [
            str(self.avdmanager),
            "create",
            "avd",
            "--force",
            "--name",
            device.avd,
            "--package",
            str(device.image),
            "--device",
            device.profile,
        ]

    def _build_emulator_args(self, device: Device) -> list[str]:
        args = [
            str(self.emulator),
            "-avd",
            device.avd,
            "-port",
            str(device.port),
            "-memory",
            str(device.ram),
            "-cores",
            str(device.cores),
            "-gpu",
            device.gpu,
            "-no-boot-anim",
        ]

        if device.headless:
            args += ["-no-window", "-no-audio"]

        return args

    @staticmethod
    def _require(tool: Path) -> None:
        if not tool.exists():
            raise ToolError(
                f"Android SDK tool not found: {tool} (run setup/init.sh)"
            )
