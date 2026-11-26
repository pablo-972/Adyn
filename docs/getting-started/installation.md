# Installation

This page explains what the install scripts do, what they install and how to
install each dependency by hand if you prefer.


## Install Scripts

Run the script of your system from the project folder.

**Linux (Debian or Ubuntu)**

```bash
./setup/init.sh
```

**Windows (PowerShell)**

```powershell
powershell -ExecutionPolicy Bypass -File setup\init.ps1
```

Both scripts run the same steps, and skip the ones already done, so they can
be run again safely:

| Step | Linux | Windows |
| --- | --- | --- |
| System packages | Java 21, `curl`, `unzip` and `python3-venv` with `apt` | Java 21 and Python with `winget` |
| Python | Checks it is 3.11 or later | Checks it is 3.11 or later |
| Android SDK | cmdline-tools, platform-tools and emulator | The same |
| Virtualization | Warns if `/dev/kvm` cannot be used | Reminds you to enable Windows Hypervisor Platform |
| Docker | Warns if it is missing | Warns if it is missing |
| Burp Suite | Downloads the Community `.jar` to `.adyn/` | The same |
| Virtual environment | Creates `.venv` and installs `requirements.txt` | The same |
| Configuration | Copies `adyn.example.toml` to `adyn.toml` | The same |

If `.venv` was created in another folder, for example before the project was
renamed, the scripts delete it and create it again. A virtual environment only
works in the folder where it was created.


## What Gets Installed

| Dependency | Where | Used for |
| --- | --- | --- |
| Java 21 | System | The Android SDK tools and Burp |
| Android cmdline-tools | `<sdk>/cmdline-tools/latest` | `sdkmanager` and `avdmanager` |
| platform-tools, emulator | `<sdk>/` | `adb` and the emulator |
| Burp Suite Community | `.adyn/burpsuite_community.jar` | The proxy |
| frida-tools, objection | `.venv` | The Frida client |
| cryptography, requests | `.venv` | The Burp CA and the MobSF API |

Everything Adyn downloads or creates goes to `.adyn/`, inside the project
folder. Only the Android SDK and the emulators live outside it, where the
Android tools and Android Studio expect them. See
[Files on your computer](../lab/README.md#files-on-your-computer).

The SDK goes to `$ANDROID_HOME` when it is set. Otherwise it goes to
`~/Android/Sdk` on Linux and `%LOCALAPPDATA%\Android\Sdk` on Windows, the
same folders Android Studio uses, so an existing SDK is reused.

Docker is only checked, not installed: install it yourself if you want to use
MobSF. See [Static Analysis](../static-analysis/README.md).


## Manual Installation

To install a dependency by hand, follow its own instructions:

| Dependency | Manual install |
| --- | --- |
| Java 21 | `apt install openjdk-21-jdk`, or `winget install EclipseAdoptium.Temurin.21.JDK` |
| Android cmdline-tools | Unzip [cmdline-tools](https://developer.android.com/studio#command-line-tools-only) into `<sdk>/cmdline-tools/latest` |
| platform-tools, emulator | `sdkmanager platform-tools emulator` |
| Burp Suite Community | Download the [jar](https://portswigger.net/burp/releases) to `.adyn/burpsuite_community.jar` |
| Python packages | `pip install -r requirements.txt` inside `.venv` |
| Docker | [docs.docker.com](https://docs.docker.com/engine/install/) |


## Virtualization

The emulator needs hardware virtualization to run at a usable speed.

**Linux**

Enable virtualization in the BIOS, then give your user access to KVM and log
in again:

```bash
sudo usermod -aG kvm $USER
```

**Windows**

Enable **Windows Hypervisor Platform** in **Windows Features**, then restart.


## Uninstall

The remove scripts stop the lab and delete what Adyn created.

**Linux**

```bash
./setup/remove.sh
```

**Windows (PowerShell)**

```powershell
powershell -ExecutionPolicy Bypass -File setup\remove.ps1
```

They ask once before starting, and again before deleting the Android SDK:

| Item | Removed |
| --- | --- |
| Emulators `adyn-*` | Yes |
| `.adyn`: Burp, frida-server builds, logs, MobSF API key | Yes |
| `.venv` | Yes |
| MobSF container and image | Yes, if Docker is installed |
| Android SDK | Only if you confirm it, since Android Studio may use it |
| `adyn.toml` and `reports/` | No, they are your configuration and reports |
| Java, Python and the other system packages | No, other programs may need them |


## Related Pages

- [Configuration](configuration.md)
- [Troubleshooting](../troubleshooting/README.md)
