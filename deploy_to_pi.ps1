param(
    [Parameter(Mandatory=$true)]
    [string]$PiHost,

    [string]$PiUser = "pi",
    [string]$RemoteDir = "~/gta6-pipeline"
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Archive = Join-Path $env:TEMP "gta6-pipeline.zip"

Write-Host "Creating project archive..."
if (Test-Path $Archive) {
    Remove-Item $Archive -Force
}

$exclude = @(
    ".venv",
    "__pycache__",
    "*.pyc",
    "audio",
    "output",
    "review",
    "logs",
    "thumbnails"
)

$tempDir = Join-Path $env:TEMP ("gta6-pipeline-copy-" + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $tempDir | Out-Null

try {
    robocopy $ProjectDir $tempDir /E /XD ".venv" "__pycache__" "audio" "output" "review" "logs" "thumbnails" /XF "*.pyc" | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "robocopy failed with exit code $LASTEXITCODE"
    }

    Compress-Archive -Path (Join-Path $tempDir "*") -DestinationPath $Archive -Force

    Write-Host "Creating remote directory..."
    ssh "$PiUser@$PiHost" "mkdir -p $RemoteDir"

    Write-Host "Copying archive to Raspberry Pi..."
    scp $Archive "$PiUser@$PiHost`:$RemoteDir/gta6-pipeline.zip"

    Write-Host "Extracting archive on Raspberry Pi..."
    ssh "$PiUser@$PiHost" "cd $RemoteDir && unzip -o gta6-pipeline.zip && rm gta6-pipeline.zip"

    Write-Host ""
    Write-Host "Done. SSH in and run:"
    Write-Host "  ssh $PiUser@$PiHost"
    Write-Host "  cd $RemoteDir"
    Write-Host "  bash setup.sh"
}
finally {
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    if (Test-Path $Archive) {
        Remove-Item $Archive -Force
    }
}
