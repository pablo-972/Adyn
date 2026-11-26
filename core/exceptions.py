class AdynError(Exception):
    """Base exception for adyn."""


class ConfigError(AdynError):
    """Invalid adyn.toml or unknown device."""


class SelectionError(AdynError):
    """The devices to use could not be chosen."""


class ToolError(AdynError):
    """Android SDK, adb, Burp, Frida, Docker or MobSF error."""
