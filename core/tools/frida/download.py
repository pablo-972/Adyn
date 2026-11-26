import lzma
import urllib.request
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from config.frida import (
    FRIDA_ABI_TO_ARCH,
    FRIDA_CACHE_PATH,
    FRIDA_DOWNLOAD_TIMEOUT,
    FRIDA_SERVER_URL,
)
from core.exceptions import ToolError
from core.utils.files import save_bytes
from core.utils.logger import get_logger


logger = get_logger(__name__)


def get_client_version() -> str:
    try:
        return version("frida")
    except PackageNotFoundError as exc:
        raise ToolError("frida is not installed (run setup/init.sh)") from exc


def download_server(abi: str) -> Path:
    """Download (once) the frida-server for this ABI and return its path."""
    if abi not in FRIDA_ABI_TO_ARCH:
        raise ToolError(f"no frida-server build for ABI {abi!r}")

    frida_version = get_client_version()
    arch = FRIDA_ABI_TO_ARCH[abi]
    binary = FRIDA_CACHE_PATH / f"frida-server-{frida_version}-android-{arch}"

    if binary.exists():
        return binary

    logger.info(f"frida: downloading frida-server {frida_version} ({arch})")
    url = FRIDA_SERVER_URL.format(version=frida_version, arch=arch)
    save_bytes(binary, _download_xz(url))

    return binary



def _download_xz(url: str) -> bytes:
    try:
        with urllib.request.urlopen(
            url,
            timeout=FRIDA_DOWNLOAD_TIMEOUT,
        ) as response:
            return lzma.decompress(response.read())
    except (OSError, lzma.LZMAError) as exc:
        raise ToolError(f"could not download frida-server: {url}") from exc
