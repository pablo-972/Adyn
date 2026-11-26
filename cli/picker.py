import sys

from core.exceptions import SelectionError
from core.tools.android.models import Device


ALL_ANSWERS = ("a", "all")


def choose_devices(devices: list[Device]) -> list[Device]:
    """Ask in the terminal which of `devices` to use."""
    if not sys.stdin.isatty():
        raise SelectionError(
            "no terminal to choose the devices: give their names"
        )

    print("Which devices?")
    for number, device in enumerate(devices, start=1):
        print(f"  {number}) {device.name:<10} {_describe(device)}")

    while True:
        answer = input("Choose (e.g. 1 or 1,3; a = all): ")
        try:
            indexes = parse_choice(answer, len(devices))
        except ValueError:
            print("Invalid choice, try again.")
            continue

        return [devices[index] for index in indexes]


def parse_choice(answer: str, count: int) -> list[int]:
    """Indexes chosen in `answer`, such as `1,3` or `a`, out of `count`."""
    answer = answer.strip().lower()
    if answer in ALL_ANSWERS:
        return list(range(count))

    indexes: list[int] = []
    for part in answer.split(","):
        number = int(part)
        if not 1 <= number <= count:
            raise ValueError(f"no device {number}")

        if number - 1 not in indexes:
            indexes.append(number - 1)

    return indexes



def _describe(device: Device) -> str:
    kind = "emulator" if device.is_emulator else "phone"
    return f"{kind}, rooted" if device.rooted else kind
