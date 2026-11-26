from dataclasses import dataclass

from config.mobsf import DEFAULT_MOBSF_PORT, DEFAULT_MOBSF_STARTUP_TIMEOUT
from core.utils.tables import RawTable, parse_fields


@dataclass(frozen=True)
class MobsfOptions:
    port: int = DEFAULT_MOBSF_PORT
    startup_timeout: int = DEFAULT_MOBSF_STARTUP_TIMEOUT

    @classmethod
    def from_dict(cls, raw: RawTable) -> "MobsfOptions":
        return cls(**parse_fields(cls, raw, where="mobsf"))
