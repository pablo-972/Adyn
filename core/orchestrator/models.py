import argparse
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from config.android import EMULATOR_PORT_STEP, FIRST_EMULATOR_PORT
from config.mobsf import MOBSF_REPORTS_PATH
from config.paths import CONFIG_FILENAME
from core.exceptions import ConfigError
from core.tools.android.models import Device
from core.tools.burp.models import BurpOptions
from core.tools.mobsf.models import MobsfOptions
from core.utils.tables import (
    RawTable,
    get_table,
    get_table_list,
    reject_unknown,
)


_CONFIG_SECTIONS = {
    "android",
    "burp",
    "devices",
    "mobsf",
}


class Command(Enum):
    SETUP = "setup"
    UP = "up"
    DOWN = "down"
    START_ANDROID = "start android"
    START_BURP = "start burp"
    START_FRIDA = "start frida"
    START_MOBSF = "start mobsf"
    STOP_ANDROID = "stop android"
    STOP_BURP = "stop burp"
    STOP_FRIDA = "stop frida"
    STOP_MOBSF = "stop mobsf"
    SCAN = "scan"


@dataclass(frozen=True)
class UpOptions:
    """What `up` starts besides the devices."""

    burp: bool = True
    frida: bool = True
    mobsf: bool = True

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "UpOptions":
        return cls(
            burp=not getattr(args, "no_burp", False),
            frida=not getattr(args, "no_frida", False),
            mobsf=not getattr(args, "no_mobsf", False),
        )


@dataclass(frozen=True)
class AdynRequest:
    command: Command
    config_path: Path
    devices: list[str]  # empty: every device
    up: UpOptions = UpOptions()
    app: Path | None = None  # scan: the app to analyze
    output: Path = MOBSF_REPORTS_PATH  # scan: folder for the reports

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "AdynRequest":
        words = (args.command, getattr(args, "component", None))
        command = " ".join(word for word in words if word)

        return cls(
            command=Command(command),
            config_path=args.config,
            devices=getattr(args, "devices", []),
            up=UpOptions.from_args(args),
            app=getattr(args, "app", None),
            output=getattr(args, "output", MOBSF_REPORTS_PATH),
        )


@dataclass(frozen=True)
class AdynConfig:
    sdk: Path
    burp: BurpOptions
    mobsf: MobsfOptions
    devices: list[Device]

    @classmethod
    def from_dict(cls, data: RawTable, *, default_sdk: Path) -> "AdynConfig":
        reject_unknown(data, _CONFIG_SECTIONS, where=CONFIG_FILENAME)

        return cls(
            sdk=_parse_sdk(data, default=default_sdk),
            burp=BurpOptions.from_dict(get_table(data, "burp")),
            mobsf=MobsfOptions.from_dict(get_table(data, "mobsf")),
            devices=_parse_devices(data),
        )

    def select(self, names: list[str]) -> list[Device]:
        """The named devices, or all of them when no name is given."""
        if not names:
            return self.devices

        by_name = {device.name: device for device in self.devices}
        unknown = [name for name in names if name not in by_name]

        if unknown:
            unknown_names = ", ".join(unknown)
            known_names = ", ".join(by_name)
            raise ConfigError(
                f"unknown device(s): {unknown_names}; known: {known_names}"
            )

        return [by_name[name] for name in names]



def _parse_sdk(data: RawTable, *, default: Path) -> Path:
    android = get_table(data, "android")
    reject_unknown(android, {"sdk"}, where="android")

    sdk = android.get("sdk")
    if sdk is not None and not isinstance(sdk, str):
        raise ConfigError(
            f"invalid value for android.sdk: expected str, got {sdk!r}"
        )

    if not sdk:
        return default

    return Path(sdk).expanduser()


def _parse_devices(data: RawTable) -> list[Device]:
    devices = [
        Device.from_dict(raw, where=f"devices[{index}]")
        for index, raw in enumerate(get_table_list(data, "devices"))
    ]
    _reject_duplicate_names(devices)

    return _assign_ports(devices)


def _assign_ports(devices: list[Device]) -> list[Device]:
    """Give each emulator without a port the next free one."""
    used = {device.port for device in devices if device.port}
    port = FIRST_EMULATOR_PORT
    result = []

    for device in devices:
        if not device.is_emulator or device.port:
            result.append(device)
            continue

        while port in used:
            port += EMULATOR_PORT_STEP

        used.add(port)
        result.append(device.with_port(port))

    return result


def _reject_duplicate_names(devices: list[Device]) -> None:
    names = [device.name for device in devices]
    duplicates = {name for name in names if names.count(name) > 1}

    if duplicates:
        duplicate_names = ", ".join(sorted(duplicates))
        raise ConfigError(f"duplicate device name(s): {duplicate_names}")
