from pathlib import Path

import pytest

from config.paths import EXAMPLE_CONFIG_FILENAME, ROOT_PATH
from core.exceptions import ConfigError
from core.orchestrator.loader import load_config


def write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "adyn.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_example_config_has_a_rooted_and_a_stock_emulator() -> None:
    config = load_config(ROOT_PATH / EXAMPLE_CONFIG_FILENAME)
    rooted, stock = config.devices
    assert rooted.rooted and rooted.adb_serial == "emulator-5554"
    assert not stock.rooted and stock.adb_serial == "emulator-5556"
    assert config.burp.port == 8080


def test_missing_config_file_is_reported(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="config file not found"):
        load_config(tmp_path / "adyn.toml")


def test_invalid_toml_is_reported(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="invalid TOML file"):
        load_config(write_config(tmp_path, "not = = toml"))
