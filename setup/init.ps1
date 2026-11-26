# Installs everything adyn needs on Windows:
#   Java 21, Android SDK (cmdline-tools, platform-tools, emulator),
#   Burp Suite Community, and a Python virtualenv with requirements.txt.
# Run:  powershell -ExecutionPolicy Bypass -File setup\init.ps1
# Safe to re-run: finished steps are skipped.
$ErrorActionPreference = "Stop"
# Makes Invoke-WebRequest much faster.
$ProgressPreference = "SilentlyContinue"

$Sdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { "$env:LOCALAPPDATA\Android\Sdk" }
$SdkManager = "$Sdk\cmdline-tools\latest\bin\sdkmanager.bat"
$BurpJar = ".adyn\burpsuite_community.jar"
$CmdlineToolsUrl = "https://dl.google.com/android/repository/commandlinetools-win-13114758_latest.zip"
$BurpUrl = "https://portswigger.net/burp/releases/download?product=community&type=Jar"
$WingetFlags = @("-e", "--accept-source-agreements", "--accept-package-agreements")


function Main {
    Set-Location (Split-Path $PSScriptRoot)

    Install-SystemPackages
    Test-Python
    Install-AndroidSdk
    Write-VirtualizationNote
    Test-Docker
    Install-Burp
    New-Venv
    Copy-Config
    Write-NextSteps
}


function Install-SystemPackages {
    Write-Step "System packages"

    if (-not (Test-Command java)) {
        Install-WingetPackage EclipseAdoptium.Temurin.21.JDK
    }

    if (-not (Test-Command python)) {
        Install-WingetPackage Python.Python.3.12
    }
}

function Test-Python {
    python -c "import sys; sys.exit(sys.version_info < (3, 11))"
    if ($LASTEXITCODE -ne 0) {
        throw "Python 3.11+ is required"
    }
}

function Install-AndroidSdk {
    Write-Step "Android SDK in $Sdk"

    if (-not (Test-Path $SdkManager)) {
        Save-CmdlineTools
    }

    ("y`n" * 50) | & $SdkManager "--sdk_root=$Sdk" --licenses | Out-Null
    & $SdkManager "--sdk_root=$Sdk" platform-tools emulator
}

function Write-VirtualizationNote {
    Write-Host "note: emulators need 'Windows Hypervisor Platform' enabled"
    Write-Host "      (Windows Features)."
}

function Test-Docker {
    if (Test-Command docker) {
        return
    }

    Write-Host "warning: docker not found, ``adyn scan`` (MobSF) will not work."
    Write-Host "         Install Docker Desktop: https://docs.docker.com/desktop/"
}

function Install-Burp {
    Write-Step "Burp Suite Community"

    if (-not (Test-Path $BurpJar)) {
        Save-Download $BurpUrl $BurpJar
    }

    Write-Host $BurpJar
}

function New-Venv {
    Write-Step "Python virtualenv (.venv)"

    if ((Test-Path .venv) -and -not (Test-VenvHere)) {
        Write-Host "The .venv was created in another folder, rebuilding it"
        Remove-Item .venv -Recurse -Force
    }

    if (-not (Test-Path .venv)) {
        python -m venv .venv
    }

    .venv\Scripts\python -m pip install -q --upgrade pip
    .venv\Scripts\python -m pip install -q -r requirements.txt
}

function Copy-Config {
    if (-not (Test-Path adyn.toml)) {
        Copy-Item adyn.example.toml adyn.toml
    }
}

function Write-NextSteps {
    Write-Step "Done. Next:"

    Write-Host "  .venv\Scripts\Activate.ps1"
    Write-Host "  python main.py setup     # create the emulators from adyn.toml"
    Write-Host "  python main.py up        # boot them and start Burp + Frida"
    Write-Host "  python main.py scan app.apk   # static analysis with MobSF"
}



function Save-CmdlineTools {
    $Tmp = Join-Path $env:TEMP "adyn-cmdline-tools"
    Remove-Item $Tmp -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory $Tmp | Out-Null

    Invoke-WebRequest $CmdlineToolsUrl -OutFile "$Tmp\tools.zip"
    Expand-Archive "$Tmp\tools.zip" -DestinationPath $Tmp

    New-Item -ItemType Directory "$Sdk\cmdline-tools" -Force | Out-Null
    Move-Item "$Tmp\cmdline-tools" "$Sdk\cmdline-tools\latest"
    Remove-Item $Tmp -Recurse -Force
}

# Downloads to a .part file first, so a cut download is never used.
function Save-Download($Url, $Target) {
    New-Item -ItemType Directory (Split-Path $Target) -Force | Out-Null
    Invoke-WebRequest $Url -OutFile "$Target.part"
    Move-Item "$Target.part" $Target
}

# A venv only works in the folder where it was created: its scripts point
# to that path. False when the project was moved or renamed.
function Test-VenvHere {
    $Activate = ".venv\Scripts\activate.bat"
    if (-not (Test-Path $Activate)) {
        return $false
    }

    return Select-String -Path $Activate -SimpleMatch "$PWD\.venv" -Quiet
}

function Install-WingetPackage($Id) {
    winget install --id $Id @WingetFlags
    Update-Path
}

# Reloads PATH so programs installed by winget are found right away.
function Update-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}

function Test-Command($Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Write-Step($Message) {
    Write-Host "`n==> $Message"
}


Main
