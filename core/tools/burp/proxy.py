"""Send a device's traffic through Burp and trust its CA there."""

from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding

from config.burp import (
    BURP_CA_PEM_PATH,
    DEVICE_INSTALL_CA_PATH,
    DEVICE_USER_CA_PATH,
    INSTALL_CA_SCRIPT_PATH,
)
from config.paths import DEVICE_TMP_PATH
from config.settings import LOCALHOST
from core.tools.android.adb import Adb
from core.tools.burp.certificate import calculate_subject_hash_old
from core.tools.burp.models import BurpOptions
from core.utils.files import save_bytes
from core.utils.logger import get_logger


logger = get_logger(__name__)


def connect(
    adb: Adb,
    options: BurpOptions,
    cert: x509.Certificate,
    *,
    rooted: bool,
) -> None:
    """Route the device's traffic through Burp and install its CA."""
    _route_traffic(adb, options)
    save_bytes(BURP_CA_PEM_PATH, cert.public_bytes(Encoding.PEM))

    if rooted:
        _install_system_ca(adb, cert)
    else:
        _copy_user_ca(adb)


def disconnect(adb: Adb, options: BurpOptions) -> None:
    adb.shell("settings put global http_proxy :0", check=False)
    adb.run("reverse", "--remove", f"tcp:{options.port}", check=False)
    logger.info(f"{adb.serial}: proxy removed")



def _route_traffic(adb: Adb, options: BurpOptions) -> None:
    # adb reverse makes Burp reachable as 127.0.0.1 on emulators and USB
    # phones alike.
    adb.run("reverse", f"tcp:{options.port}", f"tcp:{options.port}")
    adb.shell(f"settings put global http_proxy {LOCALHOST}:{options.port}")


def _install_system_ca(adb: Adb, cert: x509.Certificate) -> None:
    cert_path = f"{DEVICE_TMP_PATH}/{calculate_subject_hash_old(cert)}.0"
    adb.push(BURP_CA_PEM_PATH, cert_path)
    adb.push(INSTALL_CA_SCRIPT_PATH, DEVICE_INSTALL_CA_PATH)
    adb.sudo(f"sh {DEVICE_INSTALL_CA_PATH} {cert_path}")

    logger.info(
        f"{adb.serial}: proxy -> Burp, CA installed in the system store"
    )


def _copy_user_ca(adb: Adb) -> None:
    """Without root the CA can only be installed by hand on the device."""
    adb.push(BURP_CA_PEM_PATH, DEVICE_USER_CA_PATH)

    logger.info(
        f"{adb.serial}: proxy -> Burp. CA copied to "
        f"{DEVICE_USER_CA_PATH}; install it from Settings > Security > "
        "Install a certificate > CA certificate"
    )
