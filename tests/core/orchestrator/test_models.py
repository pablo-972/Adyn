import tomllib
from pathlib import Path

import pytest

from core.exceptions import ConfigError
from core.orchestrator.models import AdynConfig


SDK = Path("/sdk")


def parse_config(text: str) -> AdynConfig:
    return AdynConfig.from_dict(tomllib.loads(text), default_sdk=SDK)


def test_automatic_ports_skip_the_ones_set_by_hand() -> None:
    config = parse_config(
        """
[[devices]]
name = "a"
image = "x"

[[devices]]
name = "b"
image = "x"
port = 5554

[[devices]]
name = "phone"
serial = "ABC"
"""
    )
    assert [device.adb_serial for device in config.devices] == [
        "emulator-5556",
        "emulator-5554",
        "ABC",
    ]


def test_default_sdk_is_used_when_android_sdk_is_not_set() -> None:
    assert parse_config("").sdk == SDK


def test_android_sdk_expands_the_home_folder() -> None:
    assert parse_config('[android]\nsdk = "~/sdk"').sdk == Path.home() / "sdk"


def test_select_without_names_returns_every_device() -> None:
    config = parse_config('[[devices]]\nname = "a"\nimage = "x"')
    assert config.select([]) == config.devices


def test_select_rejects_unknown_names() -> None:
    config = parse_config('[[devices]]\nname = "a"\nimage = "x"')
    with pytest.raises(ConfigError, match="unknown device"):
        config.select(["missing"])


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (
            '[[devices]]\nname = "r"\nrooted = true\n'
            'image = "android-34;google_apis_playstore"',
            "cannot be rooted",
        ),
        ('[[devices]]\nname = "x"', "needs 'image'"),
        ('[[devices]]\nname = "x"\nimage = "a"\nserial = "b"', "needs 'image'"),
        (
            '[[devices]]\nname = "a"\nimage = "x"\n'
            '[[devices]]\nname = "a"\nimage = "x"',
            "duplicate",
        ),
        ('[[devices]]\nimage = "x"', "missing key"),
        ("[burp]\nprot = 8080", "unknown key"),
        ("[emulator]\nport = 1", "unknown key"),
        ('[burp]\nport = "8080"', "expected int"),
        ('[mobsf]\nport = "8000"', "expected int"),
        ("[mobsf]\nimage = 'x'", "unknown key"),
        ("[[devices]]\nname = 'x'\nimage = 34", "expected str"),
        ("[[devices]]\nname = 'x'\nimage = 'a'\nram = '4G'", "expected int"),
        ("[[devices]]\nname = 'x'\nimage = 'a'\ngpu = 'fast'", "unknown gpu"),
        ("[android]\nsdk = 1", "expected str"),
        ("burp = 1", "must be a table"),
        ("devices = 1", "\\[\\[devices\\]\\]"),
    ],
)
def test_invalid_config_is_rejected(text: str, message: str) -> None:
    with pytest.raises(ConfigError, match=message):
        parse_config(text)


def test_mobsf_port_can_be_changed() -> None:
    assert parse_config("[mobsf]\nport = 8001").mobsf.port == 8001


def test_emulator_resources_have_defaults_and_can_be_changed() -> None:
    config = parse_config(
        """
[[devices]]
name = "a"
image = "x"

[[devices]]
name = "b"
image = "x"
ram = 6144
cores = 6
gpu = "host"
"""
    )
    default, custom = config.devices
    assert (default.ram, default.cores, default.gpu) == (4096, 4, "auto")
    assert (custom.ram, custom.cores, custom.gpu) == (6144, 6, "host")
