from config.paths import DEVICE_TMP_PATH, WORK_PATH


# Paths
FRIDA_CACHE_PATH = WORK_PATH / "frida"
FRIDA_SERVER_DEVICE_PATH = f"{DEVICE_TMP_PATH}/frida-server"

# Download
FRIDA_SERVER_URL = (
    "https://github.com/frida/frida/releases/download/"
    "{version}/frida-server-{version}-android-{arch}.xz"
)
FRIDA_ABI_TO_ARCH = {
    "arm64-v8a": "arm64",
    "armeabi-v7a": "arm",
    "x86_64": "x86_64",
    "x86": "x86",
}

# Timeouts (seconds)
FRIDA_DOWNLOAD_TIMEOUT = 300

# Polling (seconds)
FRIDA_START_RETRIES = 10
FRIDA_START_POLL_INTERVAL = 0.5
