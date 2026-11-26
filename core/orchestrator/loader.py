import tomllib
from pathlib import Path

from config.paths import CONFIG_FILENAME, EXAMPLE_CONFIG_FILENAME
from core.exceptions import ConfigError
from core.orchestrator.models import AdynConfig
from core.utils.system import resolve_default_sdk
from core.utils.tables import RawTable


def load_config(path: Path) -> AdynConfig:
    text = _read_config(path)
    data = _parse_toml(text, path=path)

    return AdynConfig.from_dict(data, default_sdk=resolve_default_sdk())



def _read_config(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(
            f"config file not found: {path} "
            f"(copy {EXAMPLE_CONFIG_FILENAME} to {CONFIG_FILENAME})"
        ) from exc


def _parse_toml(text: str, *, path: Path) -> RawTable:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid TOML file: {path}: {exc}") from exc
