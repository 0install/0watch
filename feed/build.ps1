Param ($Version = "1.0.0-pre")
$ErrorActionPreference = "Stop"
pushd $PSScriptRoot

# Ensure 0install is in PATH
if (!(Get-Command 0install -ErrorAction SilentlyContinue)) {
    $downloadDir = "$env:LOCALAPPDATA\0install.net\bootstrapper"
    if (!(Test-Path "$downloadDir\0install.exe")) {
        mkdir -Force $downloadDir | Out-Null
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]'Tls11,Tls12'
        Invoke-WebRequest "https://get.0install.net/0install.exe" -OutFile "$downloadDir\0install.exe"
    }
    $env:PATH = "$env:PATH;$downloadDir"
}

# Inspect version number
$stability = if($Version.Contains("-")) {"developer"} else {"stable"}

# Build feed and archive
cmd /c "0install run --batch http://0install.net/tools/0template.xml 0watch.xml.template version=$Version stability=$stability 2>&1" # Redirect stderr to stdout
if ($LASTEXITCODE -ne 0) {throw "Exit Code: $LASTEXITCODE"}

# Patch archive URL to point to GitHub Release
if ($stability -eq "stable") {
    $path = Resolve-Path "0watch-$Version.xml"
    [xml]$xml = Get-Content $path
    $xml.interface.group.implementation.archive.href = "https://github.com/0install/0watch/releases/download/$Version/$($xml.interface.group.implementation.archive.href)"
    $xml.Save($path)
}

popd
