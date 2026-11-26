#!/usr/bin/env bash
# Installs everything adyn needs on Linux (Debian/Ubuntu):
#   Java 21, Android SDK (cmdline-tools, platform-tools, emulator),
#   Burp Suite Community, and a Python virtualenv with requirements.txt.
# Safe to re-run: finished steps are skipped.
set -euo pipefail

SDK="${ANDROID_HOME:-$HOME/Android/Sdk}"
SDKMANAGER="$SDK/cmdline-tools/latest/bin/sdkmanager"
BURP_JAR=".adyn/burpsuite_community.jar"
CMDLINE_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip"
BURP_URL="https://portswigger.net/burp/releases/download?product=community&type=Jar"


main() {
    cd "$(dirname "$0")/.."

    install_system_packages
    check_python
    install_android_sdk
    check_kvm
    check_docker
    install_burp
    create_venv
    copy_config
    print_next_steps
}


install_system_packages() {
    step "System packages"

    local packages=()
    has_java21 || packages+=(openjdk-21-jdk)
    has_command curl || packages+=(curl)
    has_command unzip || packages+=(unzip)
    python3 -c 'import ensurepip' 2>/dev/null || packages+=(python3-venv)

    if [ ${#packages[@]} -eq 0 ]; then
        return
    fi

    if ! has_command apt-get; then
        fail "install these with your package manager and re-run: ${packages[*]}"
    fi

    sudo apt-get update
    sudo apt-get install -y "${packages[@]}"
}

check_python() {
    if ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
        fail "Python 3.11+ is required"
    fi
}

install_android_sdk() {
    step "Android SDK in $SDK"

    if [ ! -x "$SDKMANAGER" ]; then
        download_cmdline_tools
    fi

    "$SDKMANAGER" --sdk_root="$SDK" --licenses < <(yes) >/dev/null
    "$SDKMANAGER" --sdk_root="$SDK" platform-tools emulator
}

check_kvm() {
    if [ -w /dev/kvm ]; then
        return
    fi

    echo "warning: no access to /dev/kvm, emulators will be very slow."
    echo "         Enable virtualization in the BIOS and run:"
    echo "         sudo usermod -aG kvm \$USER"
}

check_docker() {
    if has_command docker; then
        return
    fi

    echo "warning: docker not found, \`adyn scan\` (MobSF) will not work."
    echo "         Install it from https://docs.docker.com/engine/install/"
}

install_burp() {
    step "Burp Suite Community"

    if [ ! -f "$BURP_JAR" ]; then
        download "$BURP_URL" "$BURP_JAR"
    fi

    echo "$BURP_JAR"
}

create_venv() {
    step "Python virtualenv (.venv)"

    if [ -d .venv ] && ! is_venv_here; then
        echo "The .venv was created in another folder, rebuilding it"
        rm -rf .venv
    fi

    if [ ! -d .venv ]; then
        python3 -m venv .venv
    fi

    .venv/bin/python -m pip install -q --upgrade pip
    .venv/bin/python -m pip install -q -r requirements.txt
    
    source .venv/bin/activate
}

copy_config() {
    if [ ! -f adyn.toml ]; then
        cp adyn.example.toml adyn.toml
    fi
}

print_next_steps() {
    step "Done. Next:"

    echo "  source .venv/bin/activate"
    echo "  python main.py setup     # create the emulators from adyn.toml"
    echo "  python main.py up        # boot them and start Burp + Frida"
    echo "  python main.py scan app.apk   # static analysis with MobSF"
}



download_cmdline_tools() {
    local tmp
    tmp="$(mktemp -d)"

    curl -fL -o "$tmp/tools.zip" "$CMDLINE_TOOLS_URL"
    unzip -q "$tmp/tools.zip" -d "$tmp"

    mkdir -p "$SDK/cmdline-tools"
    mv "$tmp/cmdline-tools" "$SDK/cmdline-tools/latest"
    rm -rf "$tmp"
}

# Downloads to a .part file first, so a cut download is never used.
download() {
    local url="$1" target="$2"

    mkdir -p "$(dirname "$target")"
    curl -fL -o "$target.part" "$url"
    mv "$target.part" "$target"
}

# A venv only works in the folder where it was created: its scripts point
# to that path. False when the project was moved or renamed.
is_venv_here() {
    grep -qF "$PWD/.venv" .venv/bin/activate 2>/dev/null
}

has_java21() {
    java -version 2>&1 | grep -qE 'version "(2[1-9]|[3-9][0-9])'
}

has_command() {
    command -v "$1" >/dev/null
}

step() {
    printf '\n==> %s\n' "$*"
}

fail() {
    echo "error: $*" >&2
    exit 1
}


main "$@"
