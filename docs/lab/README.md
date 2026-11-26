# The Lab

This section explains what Adyn does on each device: how the devices are
created and reached, how their traffic goes through Burp and how Frida is
started.


## Bringing the Lab Up

`up` runs these steps, in this order:

```mermaid
flowchart LR
    Boot[Boot emulators] --> Wait[Wait for boot]
    Wait --> Running[Running devices]
    Running --> Burp[Start Burp]
    Burp --> Proxy[Proxy and CA]
    Proxy --> Frida[frida-server]
    Frida --> MobSF[MobSF]
```

Each step after the boot can be skipped with `--no-burp`, `--no-frida` or
`--no-mobsf`. `down` undoes them in the opposite order: it stops
frida-server, removes the proxy, stops the emulators and, for the whole lab,
Burp and MobSF.


## What Each Device Gets

| | Rooted device | Stock device |
| --- | --- | --- |
| Proxy | Burp, through `adb reverse` | Burp, through `adb reverse` |
| Burp CA | Installed in the system store | Copied to the device, to install by hand |
| frida-server | Started as root | Not started: use frida-gadget |

A device marked `rooted = true` that does not give root is treated as a stock
device, with a warning.


## Files on Your Computer

Adyn keeps its downloads, logs and state in `.adyn`, inside the project
folder, so nothing is written to your home folder. It is ignored by git:

```text
.adyn/
    burpsuite_community.jar     Burp Suite, downloaded by the install script
    burp.pid                    PID of the Burp started by Adyn
    burp-ca.der                 Burp's CA, as downloaded
    burp-ca.pem                 Burp's CA, as pushed to the devices
    frida/                      frida-server builds, one per version and ABI
    mobsf-api-key               API key of the MobSF container
    logs/
        burp.log                Output of Burp
        <device>.log            Output of each emulator
```


## Documents

- [Devices](devices.md)
- [Burp Suite](burp.md)
- [Frida](frida.md)
