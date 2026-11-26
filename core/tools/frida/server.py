import shlex
import time
from pathlib import PurePosixPath

from config.frida import (
    FRIDA_SERVER_DEVICE_PATH,
    FRIDA_START_POLL_INTERVAL,
    FRIDA_START_RETRIES,
)
from core.exceptions import ToolError
from core.tools.android.adb import Adb
from core.tools.frida.download import download_server, get_client_version
from core.utils.logger import get_logger


logger = get_logger(__name__)

_QUOTED_SERVER_PATH = shlex.quote(FRIDA_SERVER_DEVICE_PATH)
_SERVER_NAME = PurePosixPath(FRIDA_SERVER_DEVICE_PATH).name


def start(adb: Adb) -> None:
    """Push the frida-server that matches the client and run it as root."""
    stop(adb)
    _push_server(adb)

    # -D: run as a daemon.
    adb.sudo(f"{_QUOTED_SERVER_PATH} -D")
    _wait_until_running(adb)

    version = get_client_version()
    logger.info(f"{adb.serial}: frida-server {version} running")


def stop(adb: Adb) -> None:
    adb.sudo(f"pkill -f {_QUOTED_SERVER_PATH}", check=False)


def is_running(adb: Adb) -> bool:
    return bool(adb.sudo(f"pidof {_SERVER_NAME}", check=False))



def _push_server(adb: Adb) -> None:
    abi = adb.shell("getprop ro.product.cpu.abi")
    adb.push(download_server(abi), FRIDA_SERVER_DEVICE_PATH)
    adb.sudo(f"chmod 755 {_QUOTED_SERVER_PATH}")


def _wait_until_running(adb: Adb) -> None:
    for _ in range(FRIDA_START_RETRIES):
        if is_running(adb):
            return

        time.sleep(FRIDA_START_POLL_INTERVAL)

    raise ToolError(f"frida-server did not start on {adb.serial}")
