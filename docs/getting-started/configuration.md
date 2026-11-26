# Configuration

The lab is described in `adyn.toml`, at the root of the project. The install
script creates it from `adyn.example.toml`. This page explains every section
and key.


## Example

A lab with a rooted emulator, a stock emulator and a rooted phone:

```toml
[android]
sdk = "~/Android/Sdk"

[burp]
port = 8080
startup_timeout = 240

[mobsf]
port = 8000

[[devices]]
name = "rooted"
rooted = true
image = "system-images;android-34;google_apis;x86_64"
ram = 6144
gpu = "host"

[[devices]]
name = "stock"
rooted = false
image = "system-images;android-34;google_apis_playstore;x86_64"
headless = true

[[devices]]
name = "pixel7"
serial = "28141FDH2000AB"
rooted = true
```

Every section and key is optional, except the `name` of each device and its
`image` or `serial`. Another file can be used with `-c`, see
[Command line](cli.md).


## android

| Key | Default | Purpose |
| --- | --- | --- |
| `sdk` | See below | Folder of the Android SDK. `~` is expanded |

Without `sdk`, Adyn uses `$ANDROID_HOME`, then `$ANDROID_SDK_ROOT`, then the
folder where Android Studio and the install script put the SDK:

| System | Folder |
| --- | --- |
| Linux | `~/Android/Sdk` |
| macOS | `~/Library/Android/sdk` |
| Windows | `%LOCALAPPDATA%\Android\Sdk` |


## burp

| Key | Default | Purpose |
| --- | --- | --- |
| `jar` | `.adyn/burpsuite_community.jar` | Burp Suite `.jar` to start |
| `port` | `8080` | Port of Burp's proxy listener. It must match the listener in Burp |
| `java` | `java` | Java command used to start Burp |
| `startup_timeout` | `180` | Seconds to wait for the proxy to listen |


## mobsf

| Key | Default | Purpose |
| --- | --- | --- |
| `port` | `8000` | Port where MobSF is published, on `127.0.0.1` |
| `startup_timeout` | `180` | Seconds to wait for MobSF to answer |


## devices

Each `[[devices]]` block is one device. A device with `image` is an emulator,
and one with `serial` is a physical device.

| Key | Default | Purpose |
| --- | --- | --- |
| `name` | Required | Name used in commands and in the AVD name, `adyn-<name>` |
| `image` | | Emulator: system image for `sdkmanager` |
| `serial` | | Physical device: its serial in `adb devices` |
| `rooted` | `false` | Use root: system CA and frida-server |
| `profile` | `pixel_6` | Emulator: hardware profile, see `avdmanager list device` |
| `headless` | `false` | Emulator: no window and no audio |
| `ram` | `4096` | Emulator: memory in MB |
| `cores` | `4` | Emulator: CPU cores |
| `gpu` | `auto` | Emulator: graphics, `auto`, `host` or `swiftshader_indirect` |
| `port` | Automatic | Emulator: console port. `adb` uses the next one |

Emulators without `port` get the first free one from `5554`, in steps of two:
`5554`, `5556`, `5558`. Their `adb` serial is `emulator-<port>`.

Use a `google_apis` image for a rooted emulator, because `adb root` works on
it. A `google_apis_playstore` image is closer to a real phone, but it cannot be
rooted.


## Validation

The file is checked when it is loaded, before anything runs. Each mistake
stops Adyn with a message that says where it is:

| Mistake | Message |
| --- | --- |
| Unknown key | `unknown key(s) in burp: prot; allowed: jar, java, port, startup_timeout` |
| Wrong type | `invalid value for burp.port: expected int, got '8080'` |
| Missing name | `missing key(s) in devices[0]: name` |
| Both or none of `image` and `serial` | `device 'phone' needs 'image' (emulator) or 'serial' (physical)` |
| Rooted Play Store image | `device 'rooted' cannot be rooted with a Play Store image, use a google_apis image` |
| Repeated name | `duplicate device name(s): rooted` |
| Unknown `gpu` | `device 'rooted' has an unknown gpu 'fast'; allowed: auto, host, swiftshader_indirect` |


## Related Pages

- [Devices](../lab/devices.md)
- [Command line](cli.md)
