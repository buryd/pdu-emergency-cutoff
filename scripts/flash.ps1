# Flash firmware to Raspberry Pi Pico using mpremote
# Usage: .\scripts\flash.ps1 -Port COM3

param(
    [Parameter(Mandatory = $true)]
    [string]$Port
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "Copying config.py and main.py to Pico on $Port ..."
mpremote connect $Port cp "$root\firmware\config.py" :config.py
mpremote connect $Port cp "$root\firmware\main.py" :main.py
mpremote connect $Port reset
Write-Host "Done. Soft-reset issued."
