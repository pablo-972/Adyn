import io

import pytest

from cli.picker import choose_devices, parse_choice
from core.exceptions import SelectionError
from core.tools.android.models import Device


@pytest.mark.parametrize(
    ("answer", "indexes"),
    [
        ("1", [0]),
        ("1,3", [0, 2]),
        (" 3 , 1 ", [2, 0]),
        ("2,2", [1]),
        ("a", [0, 1, 2]),
        ("ALL", [0, 1, 2]),
    ],
)
def test_choice_gives_the_indexes_of_the_devices(
    answer: str,
    indexes: list[int],
) -> None:
    assert parse_choice(answer, 3) == indexes


@pytest.mark.parametrize("answer", ["", "0", "4", "x", "1,,2"])
def test_invalid_choice_is_rejected(answer: str) -> None:
    with pytest.raises(ValueError):
        parse_choice(answer, 3)


def test_without_a_terminal_the_devices_must_be_named(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("1\n"))
    devices = [Device(name="a", image="x"), Device(name="b", image="x")]

    with pytest.raises(SelectionError):
        choose_devices(devices)
