#!/usr/bin/env bash
# Removes what setup/init.sh and adyn created on Linux: the emulators,
# .adyn (Burp, frida-server builds, logs), .venv and MobSF in Docker.
# Asks before removing the Android SDK, which Android Studio may share.
# Keeps adyn.toml, reports/ and the system packages.
set -euo pipefail

SDK="${ANDROID_HOME:-$HOME/Android/Sdk}"
AVD_HOME="${ANDROID_AVD_HOME:-$HOME/.android/avd}"
WORK=".adyn"
MOBSF_CONTAINER="adyn-mobsf"
MOBSF_IMAGE="opensecurity/mobile-security-framework-mobsf:latest"


main() {
    cd "$(dirname "$0")/.."

    if ! confirm "Remove the adyn emulators, .adyn, .venv and MobSF?"; then
        exit 0
    fi

    stop_lab
    remove_emulators
    remove_mobsf
    remove_work_folder
    remove_venv
    remove_android_sdk
    print_what_stays
}


stop_lab() {
    step "Stopping the lab"

    if [ ! -x .venv/bin/python ] || [ ! -f adyn.toml ]; then
        return
    fi

    .venv/bin/python main.py down || true
}

remove_emulators() {
    step "Emulators in $AVD_HOME"
    rm -rf "$AVD_HOME"/adyn-*.avd "$AVD_HOME"/adyn-*.ini
}

remove_mobsf() {
    step "MobSF container and image"

    if ! has_command docker; then
        return
    fi

    docker rm --force "$MOBSF_CONTAINER" >/dev/null 2>&1 || true
    docker rmi "$MOBSF_IMAGE" >/dev/null 2>&1 || true
}

remove_work_folder() {
    step "Work folder $WORK"
    rm -rf "$WORK"
}

remove_venv() {
    step "Python virtualenv (.venv)"
    rm -rf .venv
}

remove_android_sdk() {
    if [ ! -d "$SDK" ]; then
        return
    fi

    if confirm "Also remove the Android SDK in $SDK? Android Studio may use it."; then
        step "Android SDK in $SDK"
        rm -rf "$SDK"
    fi
}

print_what_stays() {
    step "Done. Kept:"
    echo "  adyn.toml and reports/   your configuration and MobSF reports"
    echo "  Java 21, curl, unzip, python3-venv   remove them with apt if nothing else needs them"
}


confirm() {
    local answer
    read -r -p "$1 [y/N] " answer
    [[ "$answer" =~ ^[yY] ]]
}

has_command() {
    command -v "$1" >/dev/null
}

step() {
    printf '\n==> %s\n' "$*"
}


main "$@"
