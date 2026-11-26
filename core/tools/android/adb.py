import shlex
import subprocess
import time
from pathlib import Path

from config.android import (
    ADB_COMMAND_TIMEOUT,
    ADB_STATE_TIMEOUT,
    BOOT_POLL_INTERVAL,
    BOOT_TIMEOUT,
    ROOT_RETRIES,
    ROOT_RETRY_INTERVAL,
)
from core.exceptions import ToolError


class Adb:
    def __init__(self, executable: Path, serial: str) -> None:
        self.executable = executable
        self.serial = serial
        self._needs_su = False


    def run(
        self,
        *args: str,
        check: bool = True,
        timeout: float = ADB_COMMAND_TIMEOUT,
    ) -> str:
        """Run an adb command for this device and return its output."""
        process = self._execute(list(args), timeout=timeout)
        output = (process.stdout + process.stderr).strip()

        if check and process.returncode != 0:
            command = " ".join(args)
            raise ToolError(
                f"'adb {command}' failed on {self.serial}: {output}"
            )

        return output

    def shell(self, command: str, *, check: bool = True) -> str:
        return self.run("shell", command, check=check)

    def push(self, local: Path, remote: str) -> None:
        self.run("push", str(local), remote)

    def is_online(self) -> bool:
        state = self.run("get-state", check=False, timeout=ADB_STATE_TIMEOUT)
        return state == "device"

    def wait_until_booted(self, timeout: float = BOOT_TIMEOUT) -> None:
        deadline = time.monotonic() + timeout
        self.run("wait-for-device", timeout=timeout)

        while not self._is_booted():
            if time.monotonic() > deadline:
                raise ToolError(
                    f"{self.serial} did not finish booting in {timeout:.0f}s"
                )

            time.sleep(BOOT_POLL_INTERVAL)

    def become_root(self) -> bool:
        """Get root for sudo(): `adb root` on emulators, `su` on phones."""
        if self._is_root():
            return True

        return self._try_adb_root() or self._try_su()

    def sudo(self, command: str, *, check: bool = True) -> str:
        """Run a shell command as root (call become_root() first)."""
        if self._needs_su:
            command = f"su -c {shlex.quote(command)}"

        return self.shell(command, check=check)


    def _execute(
        self,
        args: list[str],
        *,
        timeout: float,
    ) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                [str(self.executable), "-s", self.serial, *args],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise ToolError(f"adb not found: {self.executable}") from exc
        except subprocess.TimeoutExpired as exc:
            message = f"'adb {args[0]}' timed out on {self.serial}"
            raise ToolError(message) from exc

    def _try_adb_root(self) -> bool:
        """Emulators with a google_apis image restart adbd as root."""
        if "cannot run as root" in self.run("root", check=False):
            return False

        for _ in range(ROOT_RETRIES):
            self.run("wait-for-device", check=False, timeout=ADB_STATE_TIMEOUT)
            if self._is_root():
                return True

            time.sleep(ROOT_RETRY_INTERVAL)

        return False

    def _try_su(self) -> bool:
        """Rooted phones (Magisk) give root through su."""
        if self.shell("su -c 'id -u'", check=False) != "0":
            return False

        self._needs_su = True
        return True

    def _is_booted(self) -> bool:
        return self.shell("getprop sys.boot_completed", check=False) == "1"

    def _is_root(self) -> bool:
        return self.shell("id -u", check=False) == "0"
