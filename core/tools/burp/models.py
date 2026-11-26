from dataclasses import dataclass
from pathlib import Path

from config.burp import (
    BURP_JAR_PATH,
    DEFAULT_BURP_PORT,
    DEFAULT_BURP_STARTUP_TIMEOUT,
    DEFAULT_JAVA,
)
from core.utils.tables import RawTable, parse_fields


@dataclass(frozen=True)
class BurpOptions:
    jar: Path = BURP_JAR_PATH
    port: int = DEFAULT_BURP_PORT
    java: str = DEFAULT_JAVA
    startup_timeout: int = DEFAULT_BURP_STARTUP_TIMEOUT

    @classmethod
    def from_dict(cls, raw: RawTable) -> "BurpOptions":
        return cls(**parse_fields(cls, raw, where="burp"))
