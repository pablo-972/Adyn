# Frida

Adyn runs frida-server on every rooted device, with the same version as the
Frida client installed in `.venv`. This page explains how it is downloaded and
started.


## Version and Download

frida-server must have the same version as the client, or they cannot talk.
Adyn reads the version of the `frida` package and downloads the matching build
from the Frida releases on GitHub:

| Device ABI | Build |
| --- | --- |
| `arm64-v8a` | `arm64` |
| `armeabi-v7a` | `arm` |
| `x86_64` | `x86_64` |
| `x86` | `x86` |

Each build is downloaded once and kept in `.adyn/frida/`:

```text
.adyn/frida/
    frida-server-17.2.1-android-x86_64
    frida-server-17.2.1-android-arm64
```

After updating `frida-tools`, the next `up` downloads the new version.


## Starting frida-server

On each rooted device, `up` and `start frida`:

1. Stop any frida-server that is already running.
2. Push the build to `/data/local/tmp/frida-server`.
3. Start it as root, as a daemon.
4. Wait until it is running.

```text
emulator-5554: frida-server 17.2.1 running
```

Once it runs, the usual Frida tools work from the computer:

```bash
frida-ps -U
```


## Stock Devices

frida-server needs root, so it is not started on stock devices. Use
frida-gadget inside the app instead:

```text
stock: not rooted, no frida-server (use frida-gadget)
```


## Related Pages

- [Devices](devices.md)
- [Troubleshooting](../troubleshooting/README.md#frida)
