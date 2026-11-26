#!/system/bin/sh
# Adds a CA to the system trust store without remounting /system: a tmpfs with the
# stock CAs plus ours is mounted over the cacerts directory. On Android 14+ the CAs
# come from the Conscrypt APEX, so the tmpfs is also bind-mounted there inside the
# Zygote and every running app. It lasts until reboot; `up` re-applies it.
# Usage: install_ca.sh <certificate named after its subject hash>

set -e
CERT="$1"
SYS=/system/etc/security/cacerts
APEX=/apex/com.android.conscrypt/cacerts
TMP=/data/local/tmp/adyn-cacerts

if ! grep -q " $SYS tmpfs " /proc/mounts; then
    rm -rf "$TMP" && mkdir -p -m 700 "$TMP"
    if [ -d "$APEX" ]; then cp "$APEX"/* "$TMP"/; else cp "$SYS"/* "$TMP"/; fi
    mount -t tmpfs tmpfs "$SYS"
    cp "$TMP"/* "$SYS"/ && rm -rf "$TMP"
    NEW_MOUNT=1
fi

cp "$CERT" "$SYS"/
chown root:root "$SYS"/* && chmod 644 "$SYS"/*
chcon u:object_r:system_file:s0 "$SYS"/*

if [ -n "$NEW_MOUNT" ] && [ -d "$APEX" ]; then
    ZYGOTES="$(pidof zygote || true) $(pidof zygote64 || true)"
    for pid in $ZYGOTES; do
        nsenter --mount="/proc/$pid/ns/mnt" -- /bin/mount --bind "$SYS" "$APEX"
    done
    for pid in $(echo "$ZYGOTES" | xargs -n1 ps -o PID -P | grep -v PID || true); do
        nsenter --mount="/proc/$pid/ns/mnt" -- /bin/mount --bind "$SYS" "$APEX" 2>/dev/null &
    done
    wait
fi
