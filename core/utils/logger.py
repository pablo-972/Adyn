import logging
import sys

from config.settings import LOG_FORMAT, LOGGER_NAME


def get_logger(name: str) -> logging.Logger:
    root = logging.getLogger(LOGGER_NAME)
    if not root.handlers:
        _configure(root)

    return root.getChild(name)



def _configure(root: logging.Logger) -> None:
    """Plain messages on stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    root.addHandler(handler)
    root.setLevel(logging.INFO)
