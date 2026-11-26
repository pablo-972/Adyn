"""The operating system: SDK location, executables and background processes.

All the platform-specific code of adyn lives here.
"""

import contextlib
import os
import signal
import subprocess
import sys
from pathlib import Path

from config.android import LINUX_SDK_PATH, MACOS_SDK_PATH, WINDOWS_SDK_SUBPATH
from config.env import get_optional_env


IS_WINDOWS = sys.platform == "win32"


def resolve_default_sdk() -> Path:
    """$ANDROID_HOME, or where Android Studio and setup/init.sh put it."""
    sdk = get_optional_env("ANDROID_HOME")
    sdk = sdk or get_optional_env("ANDROID_SDK_ROOT")

    if sdk is not None:
        return Path(sdk)

    if IS_WINDOWS:
        local_app_data = get_optional_env("LOCALAPPDATA")
        base = Path(local_app_data) if local_app_data else Path.home()
        return base / WINDOWS_SDK_SUBPATH

    if sys.platform == "darwin":
        return MACOS_SDK_PATH

    return LINUX_SDK_PATH


def resolve_executable(
    directory: Path,
    name: str,
    *,
    windows_extension: str = ".exe",
) -> Path:
    """The program `name` in `directory`, with its Windows extension."""
    return directory / (name + windows_extension if IS_WINDOWS else name)


def spawn(
    args: list[str],
    log: Path,
    *,
    env: dict[str, str] | None = None,
) -> int:
    """Start a process that keeps running after adyn exits. Returns its PID."""
    log.parent.mkdir(parents=True, exist_ok=True)
    full_env = {**os.environ, **env} if env else None

    with open(log, "ab") as output:
        process = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=output,
            env=full_env,
            creationflags=_get_detached_flags(),
            start_new_session=not IS_WINDOWS,
        )

    return process.pid


def kill(pid: int) -> None:
    """Terminate a process started with spawn() and its children."""
    if sys.platform == "win32":
        command = ["taskkill", "/PID", str(pid), "/T", "/F"]
        subprocess.run(command, capture_output=True, check=False)
        return

    with contextlib.suppress(ProcessLookupError):
        os.killpg(pid, signal.SIGTERM)



def _get_detached_flags() -> int:
    """Windows flags so the process outlives adyn. Elsewhere, none."""
    # Written as `sys.platform` so type checkers accept the Windows-only flags.
    if sys.platform == "win32":
        return subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

    return 0
