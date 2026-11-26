from config.paths import (
    DEVICE_TMP_PATH,
    LOG_PATH,
    ROOT_PATH,
    WORK_PATH,
)


# Paths
BURP_JAR_PATH = WORK_PATH / "burpsuite_community.jar"
BURP_PID_PATH = WORK_PATH / "burp.pid"
BURP_LOG_PATH = LOG_PATH / "burp.log"
BURP_CA_DER_PATH = WORK_PATH / "burp-ca.der"
BURP_CA_PEM_PATH = WORK_PATH / "burp-ca.pem"
INSTALL_CA_SCRIPT_PATH = ROOT_PATH / "core" / "tools" / "burp" / "install_ca.sh"

# Paths on the device
DEVICE_INSTALL_CA_PATH = f"{DEVICE_TMP_PATH}/adyn-install-ca.sh"
DEVICE_USER_CA_PATH = "/sdcard/Download/burp-ca.crt"

# Defaults of the [burp] section of adyn.toml
DEFAULT_BURP_PORT = 8080
DEFAULT_JAVA = "java"
DEFAULT_BURP_STARTUP_TIMEOUT = 180

# Timeouts (seconds)
BURP_CONNECT_TIMEOUT = 1
BURP_CA_DOWNLOAD_TIMEOUT = 10

# Polling (seconds)
BURP_POLL_INTERVAL = 1
