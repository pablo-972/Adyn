# Devices

The lab can mix emulators and physical phones, rooted or not. This page
explains how Adyn creates the emulators, how it reaches each device and how it
gets root.


## Emulators

An emulator is a `[[devices]]` block with an `image`. `setup` installs the
image with `sdkmanager` and creates an AVD for it with `avdmanager`:

| Part | Value |
| --- | --- |
| AVD name | `adyn-<name>` |
| AVD files | `~/.android/avd/adyn-<name>.avd` |
| Hardware profile | `profile`, `pixel_6` by default |
| Memory and cores | `ram` and `cores`, 4096 MB and 4 by default |
| Graphics | `gpu`, `auto` by default |
| Console port | `port`, or the next free one from `5554` |
| `adb` serial | `emulator-<port>` |
| Log | `.adyn/logs/<name>.log` |

`up` starts the emulators that are not running and leaves them running in the
background after Adyn exits. With `headless = true` they start without a
window and without audio.

To boot the emulators alone, without Burp or Frida, use `start android`, and
`stop android` to stop them. Their proxy is removed before they stop, so they
keep their network the next time they boot.

The memory, cores and graphics are given to the emulator each time it starts,
so changing them in `adyn.toml` only needs a restart of the emulator:

| `gpu` | When to use it |
| --- | --- |
| `auto` | The emulator chooses. Always works |
| `host` | Your graphics card. The fastest, if its drivers allow it |
| `swiftshader_indirect` | Software rendering. Slow, but works anywhere, even inside a virtual machine |

An existing AVD is not created again. To create it from scratch, delete it
with `avdmanager delete avd -n adyn-<name>` and run `setup` again.


## Physical Devices

A physical device is a `[[devices]]` block with a `serial`, as shown by
`adb devices`:

```bash
adb devices
```

Adyn does not boot or stop physical devices. Connect the phone with USB
debugging enabled before running `up`.


## Running Devices

Every command that acts on devices first checks which of them are running.
The ones that are not running are skipped:

```text
pixel7: not running, skipped
```


## Root

For a device with `rooted = true`, Adyn tries two ways to get root, once per
command:

| Way | Where it works |
| --- | --- |
| `adb root` | Emulators with a `google_apis` image |
| `su` | Rooted phones, for example with Magisk |

If neither works, the device is treated as a stock device:

```text
pixel7: marked as rooted but root was denied
```

Images with the Play Store cannot be rooted, so `adyn.toml` rejects a rooted
device with a `google_apis_playstore` image.


## Related Pages

- [Configuration](../getting-started/configuration.md)
- [Burp Suite](burp.md)
