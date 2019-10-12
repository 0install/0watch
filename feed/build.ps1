Param ($Version = "1.0.0-pre", [switch]$GitHubRelease)
$ErrorActionPreference = "Stop"
pushd $PSScriptRoot

# Ensure 0install is in PATH
if (!(Get-Command 0install -ErrorAction SilentlyContinue)) {
    echo "Downloading 0install"
    mkdir -Force "$env:TEMP\zero-install" | Out-Null
    Invoke-WebRequest "https://0install.de/files/0install.exe" -OutFile "$env:TEMP\zero-install\0install.exe"
    $env:PATH = "$env:TEMP\zero-install;$env:PATH"
}

# Build feed and archive
$stability = if($Version.Contains('-')) {'developer'} else {'stable'}
cmd /c "0install run --batch http://0install.net/tools/0template.xml 0watch.xml.template version=$Version stability=$stability 2>&1" # Redirect stderr to stdout
if ($LASTEXITCODE -ne 0) {throw "Exit Code: $LASTEXITCODE"}

# Patch archive URL to point to GitHub Release
if ($GitHubRelease) {
    $path = Resolve-Path "0watch-$Version.xml"
    [xml]$xml = Get-Content $path
    $xml.interface.group.implementation.archive.href = "https://github.com/0install/0watch/releases/download/$Version/$($xml.interface.group.implementation.archive.href)"
    $xml.Save($path)
}

popd
