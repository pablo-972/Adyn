import argparse

from cli.arguments import (
    add_component_arguments,
    add_config_argument,
    add_devices_arguments,
    add_scan_arguments,
    add_up_arguments,
)


BANNER = r"""
     _       _
    / \   __| |_   _ _ __
   / _ \ / _` | | | | '_ \
  / ___ \ (_| | |_| | | | |
 /_/   \_\__,_|\__, |_| |_|
               |___/
"""


def build_parser() -> argparse.ArgumentParser:
    parser = _BannerParser(
        prog="adyn",
        description="Android dynamic analysis lab.",
    )

    add_config_argument(parser)
    _add_commands(parser)

    return parser



class _BannerParser(argparse.ArgumentParser):
    """Shows the banner above the help of `adyn`."""

    def format_help(self) -> str:
        return f"{BANNER}\n{super().format_help()}"


def _add_commands(parser: argparse.ArgumentParser) -> None:
    # The commands get a plain parser: the banner is only for `adyn --help`.
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        parser_class=argparse.ArgumentParser,
    )

    subparsers.add_parser("setup", help="Download system images and create the emulators")
    up = subparsers.add_parser("up", help="Boot devices, start Burp, Frida and MobSF")
    down = subparsers.add_parser("down", help="Undo `up`")
    start = subparsers.add_parser("start", help="Start the emulators, Burp, Frida or MobSF")
    stop = subparsers.add_parser("stop", help="Stop the emulators, Burp, Frida or MobSF")
    scan = subparsers.add_parser("scan", help="Static analysis with MobSF")

    add_up_arguments(up)
    add_devices_arguments(down)
    add_component_arguments(start)
    add_component_arguments(stop)
    add_scan_arguments(scan)
