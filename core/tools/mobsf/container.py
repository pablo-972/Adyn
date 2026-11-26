import secrets
import shutil
import subprocess
import time
import urllib.error

from config.mobsf import (
    MOBSF_API_KEY_BYTES,
    MOBSF_API_KEY_PATH,
    MOBSF_CONNECT_TIMEOUT,
    MOBSF_CONTAINER,
    MOBSF_CONTAINER_PORT,
    MOBSF_DOCKER_TIMEOUT,
    MOBSF_IMAGE,
    MOBSF_POLL_INTERVAL,
    MOBSF_PULL_TIMEOUT,
)
from config.settings import LOCALHOST
from core.exceptions import ToolError
from core.tools.mobsf.models import MobsfOptions
from core.utils.files import save_bytes
from core.utils.logger import get_logger
from core.utils.network import open_direct


logger = get_logger(__name__)


def is_running(options: MobsfOptions) -> bool:
    """Whether MobSF answers HTTP on its port."""
    try:
        with open_direct(get_url(options), timeout=MOBSF_CONNECT_TIMEOUT):
            return True
    except urllib.error.HTTPError:
        # Any HTTP answer, even an error, means MobSF is up.
        return True
    except OSError:
        return False


def start(options: MobsfOptions) -> None:
    """Start the MobSF container, unless it already answers, and wait."""
    if is_running(options):
        logger.info(f"mobsf: already listening on {get_url(options)}")
        return

    _run_container(options)
    _wait_until_listening(options)
    logger.info(f"mobsf: listening on {get_url(options)}")


def stop() -> None:
    process = _docker("stop", MOBSF_CONTAINER, check=False)
    if process.returncode != 0:
        logger.info("mobsf: not started by adyn, nothing to stop")
        return

    logger.info("mobsf: stopped")


def get_url(options: MobsfOptions, path: str = "/") -> str:
    return f"http://{LOCALHOST}:{options.port}{path}"


def get_api_key() -> str:
    """The API key adyn gives MobSF, created on first use."""
    if not MOBSF_API_KEY_PATH.exists():
        key = secrets.token_hex(MOBSF_API_KEY_BYTES)
        save_bytes(MOBSF_API_KEY_PATH, key.encode())
        MOBSF_API_KEY_PATH.chmod(0o600)

    return MOBSF_API_KEY_PATH.read_text(encoding="utf-8").strip()



def _run_container(options: MobsfOptions) -> None:
    # A container left over from an earlier run would block the name.
    _docker("rm", "--force", MOBSF_CONTAINER, check=False)

    logger.info(
        "mobsf: starting the container "
        "(the first time Docker downloads the image, about 1.5 GB)"
    )
    _docker(
        "run",
        "--detach",
        "--rm",
        "--name",
        MOBSF_CONTAINER,
        "--publish",
        f"{LOCALHOST}:{options.port}:{MOBSF_CONTAINER_PORT}",
        "--env",
        f"MOBSF_API_KEY={get_api_key()}",
        MOBSF_IMAGE,
        timeout=MOBSF_PULL_TIMEOUT,
    )


def _wait_until_listening(options: MobsfOptions) -> None:
    deadline = time.monotonic() + options.startup_timeout

    while not is_running(options):
        if time.monotonic() > deadline:
            raise ToolError(
                f"MobSF is not listening on {get_url(options)} "
                f"after {options.startup_timeout}s: "
                f"check `docker logs {MOBSF_CONTAINER}`"
            )

        time.sleep(MOBSF_POLL_INTERVAL)


def _docker(
    *args: str,
    check: bool = True,
    timeout: float = MOBSF_DOCKER_TIMEOUT,
) -> subprocess.CompletedProcess[str]:
    docker = shutil.which("docker")
    if docker is None:
        raise ToolError("docker not found: install Docker to use MobSF")

    try:
        process = subprocess.run(
            [docker, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ToolError(f"'docker {args[0]}' timed out") from exc

    if check and process.returncode != 0:
        error = process.stderr.strip()
        raise ToolError(f"'docker {args[0]}' failed: {error}")

    return process
