import argparse
from pathlib import Path

from config.mobsf import MOBSF_REPORTS_PATH
from config.paths import CONFIG_FILENAME, CONFIG_PATH


COMPONENTS = ("android", "burp", "frida", "mobsf")
# What `up` starts besides the devices, each one with a --no-<name> option.
UP_COMPONENTS = ("burp", "frida", "mobsf")


def add_config_argument(parser: argparse.ArgumentParser) -> None:
    """Argument shared by every command."""
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=CONFIG_PATH,
        help=f"Config file (default: {CONFIG_FILENAME})",
    )


def add_devices_arguments(parser: argparse.ArgumentParser) -> None:
    """Arguments of `down`, and part of `up`, `start` and `stop`."""
    parser.add_argument(
        "devices",
        nargs="*",
        help="Device names (default: all)",
    )


def add_up_arguments(parser: argparse.ArgumentParser) -> None:
    """Arguments of `up`."""
    add_devices_arguments(parser)

    for component in UP_COMPONENTS:
        parser.add_argument(
            f"--no-{component}",
            action="store_true",
            help=f"Do not start {component}",
        )


def add_component_arguments(parser: argparse.ArgumentParser) -> None:
    """Arguments of `start` and `stop`."""
    parser.add_argument(
        "component",
        choices=COMPONENTS,
        help="What to start or stop",
    )

    add_devices_arguments(parser)


def add_scan_arguments(parser: argparse.ArgumentParser) -> None:
    """Arguments of `scan`."""
    parser.add_argument(
        "app",
        type=Path,
        help="App to analyze (.apk, .ipa...)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=MOBSF_REPORTS_PATH,
        help="Folder for the reports (default: reports/)",
    )
