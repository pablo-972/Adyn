# Command Line

Adyn is used from the command line, inside its virtual environment. This page
lists every command, its arguments and what it prints.


## Commands

| Command | Purpose |
| --- | --- |
| `setup` | Installs the system images and creates the emulators |
| `up` | Brings up the whole lab: devices, Burp, Frida and MobSF |
| `down` | Stops everything `up` started |
| `start` | Starts the emulators, Burp, Frida or MobSF |
| `stop` | Stops the emulators, Burp, Frida or MobSF |
| `scan` | Runs a static analysis with MobSF |

Every command accepts `--help`. `python main.py --help` shows the banner and
the list of commands.

The option shared by all of them goes before the command:

| Option | Default | Purpose |
| --- | --- | --- |
| `-c`, `--config` | `adyn.toml` | Configuration file of the lab |

```bash
python main.py -c other-lab.toml up
```


## setup

```text
python main.py setup
```

Installs the system images of every emulator in `adyn.toml` and creates the
AVDs that do not exist yet. Run it once, and again after adding an emulator.

```text
installing system images: system-images;android-34;google_apis;x86_64, system-images;android-34;google_apis_playstore;x86_64
rooted: created AVD adyn-rooted
stock: AVD adyn-stock already exists
```


## up

```text
python main.py up [DEVICES...] [--no-burp] [--no-frida] [--no-mobsf]
```

| Argument | Default | Purpose |
| --- | --- | --- |
| `DEVICES` | Every device | Names of the devices to bring up |
| `--no-burp` | | Do not start Burp, nor set the proxy and the CA |
| `--no-frida` | | Do not start frida-server |
| `--no-mobsf` | | Do not start MobSF |

Brings up the whole lab. It boots the emulators that are not running, waits
for them, routes every running device through Burp, starts frida-server on
the rooted ones and starts MobSF:

```text
rooted: booting adyn-rooted (emulator-5554)
stock: booting adyn-stock (emulator-5556)
rooted: waiting for boot...
stock: waiting for boot...
burp: started (pid 48213); on first run accept the license in its window
burp: listening on 127.0.0.1:8080
emulator-5554: proxy -> Burp, CA installed in the system store
emulator-5556: proxy -> Burp. CA copied to /sdcard/Download/burp-ca.crt; install it from Settings > Security > Install a certificate > CA certificate
frida: downloading frida-server 17.2.1 (x86_64)
emulator-5554: frida-server 17.2.1 running
stock: not rooted, no frida-server (use frida-gadget)
mobsf: listening on http://127.0.0.1:8000/
```

Use device names and the `--no-` options to bring up only part of the lab:

```bash
python main.py up rooted --no-mobsf
```

If MobSF cannot start, for example because Docker is not installed, `up`
warns and the rest of the lab keeps working.

Physical devices are not booted: connect them before running `up`. A device
that is not running is skipped with `not running, skipped`.


## down

```text
python main.py down [DEVICES...]
```

| Argument | Default | Purpose |
| --- | --- | --- |
| `DEVICES` | Every device | Names of the devices to bring down |

Stops frida-server, removes the proxy and stops the emulators. Physical
devices stay on.

Without device names, Burp and MobSF are stopped too. With device names, they
keep running for the other devices.


## start and stop

```text
python main.py start COMPONENT [DEVICES...]
```

```text
python main.py stop COMPONENT [DEVICES...]
```

| Argument | Default | Purpose |
| --- | --- | --- |
| `COMPONENT` | Required | `android`, `burp`, `frida` or `mobsf` |
| `DEVICES` | Every device | Names of the devices, for `android`, `burp` and `frida` |

| Command | What it does |
| --- | --- |
| `start android` | Boots the emulators only, without Burp or Frida. Asks which ones if no name is given |
| `stop android` | Removes the proxy of the running emulators and stops them |
| `start burp` | Starts Burp if needed and routes the running devices through it |
| `stop burp` | Removes the proxy. Without device names, closes Burp too |
| `start frida` | Starts frida-server on the running rooted devices |
| `stop frida` | Stops frida-server on the running rooted devices |
| `start mobsf` | Starts the MobSF container |
| `stop mobsf` | Stops the MobSF container |


### Choosing the Devices

`start android` brings up the devices one by one. Without device names, and
with more than one emulator, it asks which ones to boot:

```text
Which devices?
  1) rooted     emulator, rooted
  2) stock      emulator
Choose (e.g. 1 or 1,3; a = all): 1
```

Without a terminal, for example from a script, it cannot ask and stops with
an error: give the device names instead.


## scan

```text
python main.py scan APP [-o FOLDER]
```

| Argument | Default | Purpose |
| --- | --- | --- |
| `APP` | Required | App to analyze, such as an `.apk` or `.ipa` |
| `-o`, `--output` | `reports/` | Folder where the reports are saved |

Starts MobSF if it is not running, uploads the app, runs the static analysis
and saves the reports:

```text
mobsf: starting the container (the first time Docker downloads the image, about 1.5 GB)
mobsf: listening on http://127.0.0.1:8000/
mobsf: uploading shop.apk
mobsf: analyzing shop.apk...
mobsf: report saved to /home/analyst/adyn/reports/shop.json
mobsf: report saved to /home/analyst/adyn/reports/shop.pdf
```

MobSF keeps running afterwards, so the next scan starts faster. See
[Static Analysis](../static-analysis/README.md).


## Exit Codes

| Code | Meaning |
| --- | --- |
| `0` | The command finished |
| `1` | The command failed. The message starts with `error:` |
| `2` | Invalid arguments |
| `130` | Stopped with Ctrl+C |


## Related Pages

- [Configuration](configuration.md)
- [The Lab](../lab/README.md)
