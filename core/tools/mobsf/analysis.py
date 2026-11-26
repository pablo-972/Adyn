import json
from pathlib import Path
from typing import Any

import requests

from config.mobsf import (
    MOBSF_ERROR_PREVIEW_CHARS,
    MOBSF_PDF_PATH,
    MOBSF_SCAN_PATH,
    MOBSF_SCAN_TIMEOUT,
    MOBSF_UPLOAD_PATH,
    MOBSF_UPLOAD_TIMEOUT,
)
from core.exceptions import ToolError
from core.tools.mobsf.container import get_api_key, get_url
from core.tools.mobsf.models import MobsfOptions
from core.utils.files import save_bytes
from core.utils.logger import get_logger


logger = get_logger(__name__)

Form = dict[str, Any]


def analyze(options: MobsfOptions, app: Path, *, output: Path) -> list[Path]:
    """Run MobSF's static analysis on an app and save its JSON and PDF."""
    if not app.is_file():
        raise ToolError(f"app not found: {app}")

    with _create_session() as session:
        upload = _upload(session, options, app)
        report = _scan(session, options, upload, app=app)
        pdf = _download_pdf(session, options, upload["hash"])

    return _save_reports(app, report, pdf, output=output)



def _create_session() -> requests.Session:
    session = requests.Session()
    # Talk to MobSF directly: HTTP_PROXY may point to Burp.
    session.trust_env = False
    session.headers["Authorization"] = get_api_key()

    return session


def _upload(
    session: requests.Session,
    options: MobsfOptions,
    app: Path,
) -> Form:
    logger.info(f"mobsf: uploading {app.name}")

    with app.open("rb") as file:
        response = _post(
            session,
            options,
            MOBSF_UPLOAD_PATH,
            files={"file": (app.name, file, "application/octet-stream")},
            timeout=MOBSF_UPLOAD_TIMEOUT,
        )

    upload = _read_json(response)
    if "hash" not in upload:
        raise ToolError(f"unexpected MobSF upload answer: {upload!r}")

    return upload


def _scan(
    session: requests.Session,
    options: MobsfOptions,
    upload: Form,
    *,
    app: Path,
) -> Form:
    logger.info(f"mobsf: analyzing {app.name}...")

    response = _post(
        session,
        options,
        MOBSF_SCAN_PATH,
        data=upload,
        timeout=MOBSF_SCAN_TIMEOUT,
    )

    return _read_json(response)


def _download_pdf(
    session: requests.Session,
    options: MobsfOptions,
    file_hash: str,
) -> bytes:
    response = _post(
        session,
        options,
        MOBSF_PDF_PATH,
        data={"hash": file_hash},
        timeout=MOBSF_SCAN_TIMEOUT,
    )

    return response.content


def _post(
    session: requests.Session,
    options: MobsfOptions,
    path: str,
    *,
    timeout: float,
    data: Form | None = None,
    files: Form | None = None,
) -> requests.Response:
    url = get_url(options, path)

    try:
        response = session.post(url, data=data, files=files, timeout=timeout)
    except requests.RequestException as exc:
        raise ToolError(f"could not reach MobSF: {url}") from exc

    if response.status_code != requests.codes.ok:
        preview = response.text[:MOBSF_ERROR_PREVIEW_CHARS]
        raise ToolError(
            f"MobSF answered {response.status_code} on {path}: {preview}"
        )

    return response


def _read_json(response: requests.Response) -> Form:
    try:
        data = response.json()
    except ValueError as exc:
        raise ToolError(f"invalid JSON from MobSF: {response.url}") from exc

    if not isinstance(data, dict):
        raise ToolError(f"unexpected JSON from MobSF: {response.url}")

    return data


def _save_reports(
    app: Path,
    report: Form,
    pdf: bytes,
    *,
    output: Path,
) -> list[Path]:
    json_path = output / f"{app.stem}.json"
    pdf_path = output / f"{app.stem}.pdf"

    save_bytes(json_path, json.dumps(report, indent=2).encode())
    save_bytes(pdf_path, pdf)

    return [json_path, pdf_path]
