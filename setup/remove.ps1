# Removes what setup\init.ps1 and adyn created on Windows: the emulators,
# .adyn (Burp, frida-server builds, logs), .venv and MobSF in Docker.
# Asks before removing the Android SDK, which Android Studio may share.
# Keeps adyn.toml, reports\ and the programs installed with winget.
# Run:  powershell -ExecutionPolicy Bypass -File setup\remove.ps1
$ErrorActionPreference = "Stop"

$Sdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { "$env:LOCALAPPDATA\Android\Sdk" }
$AvdHome = if ($env:ANDROID_AVD_HOME) { $env:ANDROID_AVD_HOME } else { "$HOME\.android\avd" }
$Work = ".adyn"
$MobsfContainer = "adyn-mobsf"
$MobsfImage = "opensecurity/mobile-security-framework-mobsf:latest"


function Main {
    Set-Location (Split-Path $PSScriptRoot)

    if (-not (Confirm-Step "Remove the adyn emulators, .adyn, .venv and MobSF?")) {
        return
    }

    Stop-Lab
    Remove-Emulators
    Remove-Mobsf
    Remove-WorkFolder
    Remove-Venv
    Remove-AndroidSdk
    Write-WhatStays
}


function Stop-Lab {
    Write-Step "Stopping the lab"

    if (-not (Test-Path .venv\Scripts\python.exe) -or -not (Test-Path adyn.toml)) {
        return
    }

    # A failed `down` must not stop the removal.
    $ErrorActionPreference = "Continue"
    .venv\Scripts\python main.py down
}

function Remove-Emulators {
    Write-Step "Emulators in $AvdHome"

    Remove-Path "$AvdHome\adyn-*.avd"
    Remove-Path "$AvdHome\adyn-*.ini"
}

function Remove-Mobsf {
    Write-Step "MobSF container and image"

    if (-not (Test-Command docker)) {
        return
    }

    # Docker fails when there is nothing to remove, and that is fine.
    $ErrorActionPreference = "Continue"
    docker rm --force $MobsfContainer *> $null
    docker rmi $MobsfImage *> $null
}

function Remove-WorkFolder {
    Write-Step "Work folder $Work"
    Remove-Path $Work
}

function Remove-Venv {
    Write-Step "Python virtualenv (.venv)"
    Remove-Path .venv
}

function Remove-AndroidSdk {
    if (-not (Test-Path $Sdk)) {
        return
    }

    if (Confirm-Step "Also remove the Android SDK in $Sdk? Android Studio may use it.") {
        Write-Step "Android SDK in $Sdk"
        Remove-Path $Sdk
    }
}

function Write-WhatStays {
    Write-Step "Done. Kept:"
    Write-Host "  adyn.toml and reports\   your configuration and MobSF reports"
    Write-Host "  Java 21 and Python   remove them with winget if nothing else needs them"
}


function Confirm-Step($Question) {
    $Answer = Read-Host "$Question [y/N]"
    return $Answer -match "^[yY]"
}

function Remove-Path($Path) {
    if (Test-Path $Path) {
        Remove-Item $Path -Recurse -Force
    }
}

function Test-Command($Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Write-Step($Message) {
    Write-Host "`n==> $Message"
}


Main
