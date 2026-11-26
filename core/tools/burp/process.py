import socket
import time

from config.burp import (
    BURP_CONNECT_TIMEOUT,
    BURP_LOG_PATH,
    BURP_PID_PATH,
    BURP_POLL_INTERVAL,
)
from config.settings import LOCALHOST
from core.exceptions import ToolError
from core.tools.burp.models import BurpOptions
from core.utils.logger import get_logger
from core.utils.system import kill, spawn


logger = get_logger(__name__)


def is_running(options: BurpOptions) -> bool:
    address = (LOCALHOST, options.port)

    try:
        with socket.create_connection(address, timeout=BURP_CONNECT_TIMEOUT):
            return True
    except OSError:
        return False


def start(options: BurpOptions) -> None:
    """Start Burp, unless it is already listening, and wait for its proxy."""
    if is_running(options):
        logger.info(f"burp: already listening on {_get_address(options)}")
        return

    _launch(options)
    _wait_until_listening(options)
    logger.info(f"burp: listening on {_get_address(options)}")


def stop() -> None:
    if not BURP_PID_PATH.exists():
        logger.info("burp: not started by adyn, nothing to stop")
        return

    kill(_read_pid())
    BURP_PID_PATH.unlink()
    logger.info("burp: stopped")



def _launch(options: BurpOptions) -> None:
    if not options.jar.exists():
        raise ToolError(
            f"Burp jar not found: {options.jar} "
            "(run setup/init.sh or set burp.jar)"
        )

    pid = spawn([options.java, "-jar", str(options.jar)], BURP_LOG_PATH)
    BURP_PID_PATH.write_text(str(pid), encoding="utf-8")

    logger.info(
        f"burp: started (pid {pid}); "
        "on first run accept the license in its window"
    )


def _wait_until_listening(options: BurpOptions) -> None:
    deadline = time.monotonic() + options.startup_timeout

    while not is_running(options):
        if time.monotonic() > deadline:
            raise ToolError(
                f"Burp is not listening on {_get_address(options)} "
                f"after {options.startup_timeout}s: check its proxy listener"
            )

        time.sleep(BURP_POLL_INTERVAL)


def _read_pid() -> int:
    pid_text = BURP_PID_PATH.read_text(encoding="utf-8")

    try:
        return int(pid_text)
    except ValueError as exc:
        raise ToolError(f"invalid Burp PID file: {BURP_PID_PATH}") from exc


def _get_address(options: BurpOptions) -> str:
    return f"{LOCALHOST}:{options.port}"
