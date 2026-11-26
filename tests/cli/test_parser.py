from pathlib import Path

import pytest

from cli.parser import BANNER, build_parser
from config.mobsf import MOBSF_REPORTS_PATH
from config.paths import CONFIG_PATH
from core.orchestrator.models import AdynRequest, Command


def parse(*argv: str) -> AdynRequest:
    return AdynRequest.from_args(build_parser().parse_args(argv))


@pytest.mark.parametrize(
    ("argv", "command"),
    [
        (["setup"], Command.SETUP),
        (["up"], Command.UP),
        (["down"], Command.DOWN),
        (["start", "android"], Command.START_ANDROID),
        (["stop", "android"], Command.STOP_ANDROID),
        (["start", "burp"], Command.START_BURP),
        (["start", "frida"], Command.START_FRIDA),
        (["stop", "burp"], Command.STOP_BURP),
        (["stop", "frida"], Command.STOP_FRIDA),
        (["start", "mobsf"], Command.START_MOBSF),
        (["stop", "mobsf"], Command.STOP_MOBSF),
        (["scan", "app.apk"], Command.SCAN),
    ],
)
def test_each_command_line_maps_to_its_command(
    argv: list[str],
    command: Command,
) -> None:
    assert parse(*argv).command is command


def test_without_device_names_every_device_is_selected() -> None:
    request = parse("up")
    assert request.devices == []
    assert request.config_path == CONFIG_PATH


def test_setup_takes_no_device_names() -> None:
    assert parse("setup").devices == []


def test_device_names_and_config_are_kept() -> None:
    request = parse("-c", "lab.toml", "stop", "burp", "rooted", "stock")
    assert request.devices == ["rooted", "stock"]
    assert request.config_path == Path("lab.toml")


def test_unknown_component_is_rejected() -> None:
    with pytest.raises(SystemExit):
        parse("start", "objection")


def test_scan_keeps_the_app_and_saves_to_reports_by_default() -> None:
    request = parse("scan", "app.apk")
    assert request.app == Path("app.apk")
    assert request.output == MOBSF_REPORTS_PATH


def test_scan_output_folder_can_be_changed() -> None:
    assert parse("scan", "app.apk", "-o", "out").output == Path("out")


def test_scan_needs_an_app() -> None:
    with pytest.raises(SystemExit):
        parse("scan")


def test_help_starts_with_the_banner() -> None:
    assert build_parser().format_help().startswith(BANNER)


def test_up_starts_everything_by_default() -> None:
    options = parse("up").up
    assert (options.burp, options.frida, options.mobsf) == (True, True, True)


def test_up_can_skip_burp_frida_and_mobsf() -> None:
    options = parse("up", "rooted", "--no-burp", "--no-mobsf").up
    assert (options.burp, options.frida, options.mobsf) == (False, True, False)
