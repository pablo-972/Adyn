from pathlib import Path


# Filenames
CONFIG_FILENAME = "adyn.toml"
EXAMPLE_CONFIG_FILENAME = "adyn.example.toml"

# Project
ROOT_PATH = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_PATH / CONFIG_FILENAME

# Work folder: downloads, logs and state, kept inside the project
WORK_PATH = ROOT_PATH / ".adyn"
LOG_PATH = WORK_PATH / "logs"

# Device
DEVICE_TMP_PATH = "/data/local/tmp"
