$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location $Root
try {
  node scripts\capture-screenshots.js
}
finally {
  Pop-Location
}
