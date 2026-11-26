# Troubleshooting

Known issues and their fixes, grouped by where they happen.


## Categories

- [Installation](#installation)
- [Emulators](#emulators)
- [Burp Suite](#burp-suite)
- [Frida](#frida)
- [MobSF](#mobsf)


## Installation

### The virtual environment does not work

Common symptoms:

- `.venv/bin/pip: cannot execute: required file not found`.
- `frida` or `objection` fail to start from `.venv`.

The project folder was moved or renamed after `.venv` was created. A virtual
environment only works in the folder where it was created. Run the install
script again: it detects it and creates `.venv` again.

```bash
./setup/init.sh
```


### Python is too old

Common symptoms:

- The install script stops with `Python 3.11+ is required`.

Adyn reads `adyn.toml` with `tomllib`, which needs Python 3.11. Install a
newer Python and run the install script again.


## Emulators

### Emulators are very slow

Common symptoms:

- The install script warned `no access to /dev/kvm`.
- `up` stops with `did not finish booting in 300s`.

The emulator is running without hardware virtualization. Enable it in the
BIOS, then:

1. On Linux, run `sudo usermod -aG kvm $USER` and log in again.
2. On Windows, enable **Windows Hypervisor Platform** in **Windows Features**
   and restart.


### Apps keep saying they are not responding

Common symptoms:

- Android shows **System UI isn't responding** or **Pixel Launcher isn't
  responding**, with **Wait** and **Close app**.
- The emulator feels slow even after it has booted.

The emulator has too little memory or CPU, or it draws the screen in
software. Give it more in `adyn.toml` and restart it:

```toml
[[devices]]
name = "rooted"
image = "system-images;android-34;google_apis;x86_64"
ram = 6144
cores = 6
gpu = "host"
```

Running one emulator at a time also helps.


### A rooted emulator gets no root

Common symptoms:

- `marked as rooted but root was denied`.
- The CA is copied to `/sdcard/Download` instead of the system store.

The image does not allow `adb root`. Use a `google_apis` image for rooted
emulators, delete the AVD and run `setup` again:

```bash
avdmanager delete avd -n adyn-rooted
```

```bash
python main.py setup
```


## Burp Suite

### Burp does not start listening

Common symptoms:

- `up` stops with `Burp is not listening on 127.0.0.1:8080 after 180s`.

Burp is waiting for something in its window, usually the license on its first
run, or its proxy listener is on another port. Accept the license, check that
the listener in **Proxy → Proxy settings** matches `port` in `adyn.toml`, and
run `up` again. Burp's output is in `.adyn/logs/burp.log`.


### Burp is not found

Common symptoms:

- `Burp jar not found: /home/analyst/adyn/.adyn/burpsuite_community.jar`.

Run the install script to download it, or set `jar` in the `[burp]` section
of `adyn.toml` to the `.jar` you already have.


### Apps on a stock device show no traffic

Common symptoms:

- Burp shows TLS errors for the app.
- Only the browser traffic can be read.

Apps that target Android 7 or later do not trust CAs from the user store. Use
a rooted device, where the CA goes to the system store, or patch the app to
trust user CAs.


## Frida

### frida-server is not started

Common symptoms:

- `not rooted, no frida-server (use frida-gadget)`.

The device has `rooted = false`, and frida-server needs root. Use a rooted
device, or add frida-gadget to the app.


### No build for the device

Common symptoms:

- `no frida-server build for ABI 'mips'`.

Frida only publishes frida-server for `arm64-v8a`, `armeabi-v7a`, `x86_64` and
`x86`. Use a device or image with one of them.


## MobSF

### Docker is not found

Common symptoms:

- `docker not found: install Docker to use MobSF`.

Install Docker, then run `scan` again. See
[docs.docker.com](https://docs.docker.com/engine/install/).


### Docker refuses to run the container

Common symptoms:

- `'docker run' failed: permission denied while trying to connect to the Docker daemon socket`.

Your user cannot use Docker. On Linux, add it to the `docker` group and log in
again:

```bash
sudo usermod -aG docker $USER
```


### MobSF does not answer

Common symptoms:

- `MobSF is not listening on http://127.0.0.1:8000/ after 180s`.

The container started but MobSF is not ready yet, or it failed. Check its
output, and raise `startup_timeout` in the `[mobsf]` section if it is only
slow:

```bash
docker logs adyn-mobsf
```
