import hashlib

from cryptography import x509

from config.burp import BURP_CA_DER_PATH, BURP_CA_DOWNLOAD_TIMEOUT
from config.settings import LOCALHOST
from core.exceptions import ToolError
from core.tools.burp.models import BurpOptions
from core.tools.burp.process import is_running
from core.utils.files import save_bytes
from core.utils.network import open_direct


def fetch_ca_certificate(options: BurpOptions) -> x509.Certificate:
    """Burp's CA, downloaded from the running proxy (cached in .adyn)."""
    if is_running(options):
        _download_ca(options)

    if not BURP_CA_DER_PATH.exists():
        raise ToolError(
            f"Burp CA not found: {BURP_CA_DER_PATH} (start Burp first)"
        )

    return x509.load_der_x509_certificate(BURP_CA_DER_PATH.read_bytes())


def calculate_subject_hash_old(cert: x509.Certificate) -> str:
    """Same as `openssl x509 -subject_hash_old`: the name Android expects."""
    subject = cert.subject.public_bytes()
    digest = hashlib.md5(subject, usedforsecurity=False).digest()

    return f"{int.from_bytes(digest[:4], 'little'):08x}"



def _download_ca(options: BurpOptions) -> None:
    url = f"http://{LOCALHOST}:{options.port}/cert"

    try:
        with open_direct(url, timeout=BURP_CA_DOWNLOAD_TIMEOUT) as response:
            save_bytes(BURP_CA_DER_PATH, response.read())
    except OSError as exc:
        raise ToolError(f"could not download the Burp CA: {url}") from exc
