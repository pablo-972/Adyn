from dataclasses import dataclass, replace

from config.android import (
    AVD_PREFIX,
    DEFAULT_DEVICE_CORES,
    DEFAULT_DEVICE_GPU,
    DEFAULT_DEVICE_PROFILE,
    DEFAULT_DEVICE_RAM,
    GPU_MODES,
)
from core.exceptions import ConfigError
from core.utils.tables import RawTable, parse_fields


@dataclass(frozen=True)
class Device:
    name: str
    rooted: bool = False
    image: str | None = None  # emulator: sdkmanager system image
    serial: str | None = None  # physical device: adb serial
    profile: str = DEFAULT_DEVICE_PROFILE
    headless: bool = False
    ram: int = DEFAULT_DEVICE_RAM  # emulator: memory in MB
    cores: int = DEFAULT_DEVICE_CORES  # emulator: CPU cores
    gpu: str = DEFAULT_DEVICE_GPU  # emulator: -gpu mode
    port: int = 0  # emulator console port; assigned automatically when 0

    def __post_init__(self) -> None:
        if (self.image is None) == (self.serial is None):
            raise ConfigError(
                f"device '{self.name}' needs 'image' (emulator) "
                "or 'serial' (physical)"
            )

        if self.rooted and self.image and "playstore" in self.image:
            raise ConfigError(
                f"device '{self.name}' cannot be rooted with a "
                "Play Store image, use a google_apis image"
            )

        if self.gpu not in GPU_MODES:
            raise ConfigError(
                f"device '{self.name}' has an unknown gpu '{self.gpu}'; "
                f"allowed: {', '.join(GPU_MODES)}"
            )


    @classmethod
    def from_dict(cls, raw: RawTable, *, where: str) -> "Device":
        return cls(**parse_fields(cls, raw, where=where))

    @property
    def is_emulator(self) -> bool:
        return self.image is not None

    @property
    def avd(self) -> str:
        return f"{AVD_PREFIX}{self.name}"

    @property
    def adb_serial(self) -> str:
        return self.serial or f"emulator-{self.port}"

    def with_port(self, port: int) -> "Device":
        return replace(self, port=port)
