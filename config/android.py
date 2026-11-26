from pathlib import Path


# SDK, where Android Studio and setup/init.sh install it
LINUX_SDK_PATH = Path.home() / "Android" / "Sdk"
MACOS_SDK_PATH = Path.home() / "Library" / "Android" / "sdk"
# Inside %LOCALAPPDATA%.
WINDOWS_SDK_SUBPATH = Path("Android") / "Sdk"

# Answers to the SDK tools
# Accepts every license sdkmanager asks about.
SDK_LICENSE_ANSWERS = "y\n" * 20
# Answer to the "custom hardware profile?" question of avdmanager.
AVD_NO_CUSTOM_PROFILE = "no\n"

# Emulators
AVD_PREFIX = "adyn-"
DEFAULT_DEVICE_PROFILE = "pixel_6"
# Memory in MB and CPU cores. Less makes Android 14 show "isn't responding".
DEFAULT_DEVICE_RAM = 4096
DEFAULT_DEVICE_CORES = 4
DEFAULT_DEVICE_GPU = "auto"
# Modes of the emulator's -gpu option.
GPU_MODES = ("auto", "host", "swiftshader_indirect")
FIRST_EMULATOR_PORT = 5554
# Each emulator uses a console port and the next one for adb.
EMULATOR_PORT_STEP = 2

# Timeouts (seconds)
ADB_COMMAND_TIMEOUT = 120
ADB_STATE_TIMEOUT = 10
BOOT_TIMEOUT = 300

# Polling (seconds)
BOOT_POLL_INTERVAL = 2
# adbd restarts as root after `adb root`.
ROOT_RETRIES = 10
ROOT_RETRY_INTERVAL = 1
