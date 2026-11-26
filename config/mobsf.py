from config.paths import ROOT_PATH, WORK_PATH


# Paths
MOBSF_API_KEY_PATH = WORK_PATH / "mobsf-api-key"
MOBSF_REPORTS_PATH = ROOT_PATH / "reports"

# Docker
MOBSF_IMAGE = "opensecurity/mobile-security-framework-mobsf:latest"
MOBSF_CONTAINER = "adyn-mobsf"
# Port MobSF listens on inside the container.
MOBSF_CONTAINER_PORT = 8000

# Defaults of the [mobsf] section of adyn.toml
DEFAULT_MOBSF_PORT = 8000
DEFAULT_MOBSF_STARTUP_TIMEOUT = 180

# API
MOBSF_API_KEY_BYTES = 32
MOBSF_UPLOAD_PATH = "/api/v1/upload"
MOBSF_SCAN_PATH = "/api/v1/scan"
MOBSF_PDF_PATH = "/api/v1/download_pdf"
# How much of an error answer goes into the error message.
MOBSF_ERROR_PREVIEW_CHARS = 200

# Timeouts (seconds)
MOBSF_CONNECT_TIMEOUT = 2
MOBSF_DOCKER_TIMEOUT = 60
# Docker pulls the image (about 1.5 GB) on the first start.
MOBSF_PULL_TIMEOUT = 1800
MOBSF_UPLOAD_TIMEOUT = 300
# A large app can take several minutes to analyze.
MOBSF_SCAN_TIMEOUT = 1800

# Polling (seconds)
MOBSF_POLL_INTERVAL = 2
