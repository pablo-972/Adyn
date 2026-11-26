import os
from pathlib import Path


def save_bytes(path: Path, data: bytes) -> None:
    """Write `data` to a .tmp file next to `path`, then move it over `path`."""
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)
