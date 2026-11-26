from dataclasses import MISSING, Field, fields
from pathlib import Path
from typing import Any

from core.exceptions import ConfigError


RawTable = dict[str, Any]


def get_table(data: RawTable, key: str) -> RawTable:
    """The `[key]` table of `data`, or an empty one when it is missing."""
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ConfigError(f"invalid section [{key}]: it must be a table")

    return value


def get_table_list(data: RawTable, key: str) -> list[RawTable]:
    """The `[[key]]` tables of `data`, or none when they are missing."""
    value = data.get(key, [])
    if isinstance(value, list):
        if all(isinstance(item, dict) for item in value):
            return value

    raise ConfigError(f"invalid {key}: write them as [[{key}]] blocks")


def parse_fields(cls: type[Any], raw: RawTable, *, where: str) -> RawTable:
    """Check the keys and value types of `raw` against a dataclass."""
    spec = {field.name: field for field in fields(cls)}
    reject_unknown(raw, set(spec), where=where)
    _reject_missing(raw, spec, where=where)

    return {
        key: _parse_value(spec[key].default, value, where=f"{where}.{key}")
        for key, value in raw.items()
    }


def reject_unknown(raw: RawTable, allowed: set[str], *, where: str) -> None:
    unknown = set(raw) - allowed
    if not unknown:
        return

    raise ConfigError(
        f"unknown key(s) in {where}: {', '.join(sorted(unknown))}; "
        f"allowed: {', '.join(sorted(allowed))}"
    )



def _parse_value(default: Any, value: Any, *, where: str) -> Any:
    # Paths, and fields without a default or defaulting to None, are written
    # as strings.
    is_path = isinstance(default, Path)
    is_text = default is None or default is MISSING or is_path
    expected = str if is_text else type(default)

    if type(value) is not expected:
        raise ConfigError(
            f"invalid value for {where}: "
            f"expected {expected.__name__}, got {value!r}"
        )

    return Path(str(value)).expanduser() if is_path else value


def _reject_missing(
    raw: RawTable,
    spec: dict[str, Field[Any]],
    *,
    where: str,
) -> None:
    required = [
        name for name, field in spec.items() if field.default is MISSING
    ]
    missing = [name for name in required if name not in raw]

    if missing:
        raise ConfigError(f"missing key(s) in {where}: {', '.join(missing)}")
