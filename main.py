import sys

from cli.parser import build_parser
from cli.picker import choose_devices
from config.settings import EXIT_INTERRUPTED
from core.exceptions import AdynError
from core.orchestrator.commands import run
from core.orchestrator.models import AdynRequest


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        request = AdynRequest.from_args(args)
        run(request, choose=choose_devices)
    except AdynError as exc:
        sys.exit(f"error: {exc}")
    except KeyboardInterrupt:
        sys.exit(EXIT_INTERRUPTED)


if __name__ == "__main__":
    main()
