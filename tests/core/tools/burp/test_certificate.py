import datetime as dt
import shutil
import subprocess
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID

from core.tools.burp.certificate import calculate_subject_hash_old


def self_signed_certificate(common_name: str) -> x509.Certificate:
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = dt.datetime.now(dt.UTC)
    return (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(1)
        .not_valid_before(now)
        .not_valid_after(now + dt.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )


@pytest.mark.skipif(shutil.which("openssl") is None, reason="needs openssl")
def test_subject_hash_matches_openssl(tmp_path: Path) -> None:
    cert = self_signed_certificate("adyn test CA")
    pem = tmp_path / "ca.pem"
    pem.write_bytes(cert.public_bytes(Encoding.PEM))
    expected = subprocess.run(
        ["openssl", "x509", "-subject_hash_old", "-noout", "-in", str(pem)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert calculate_subject_hash_old(cert) == expected
