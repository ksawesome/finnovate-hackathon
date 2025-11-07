<#
.SYNOPSIS
  Render SVG diagrams to PNG with multiple fallbacks (Inkscape, ImageMagick, rsvg, Edge/Chrome headless).

.USAGE
  powershell -ExecutionPolicy Bypass -File .\scripts\render-diagrams.ps1 -InputSvg docs/architecture-detailed.svg -OutputPng docs/architecture-detailed.png -Width 1800 -Height 1200

.NOTES
  Works best when Inkscape or ImageMagick is installed. On Windows, Microsoft Edge headless can be used as a last resort.
#>

param(
    [string]$InputSvg = "docs/architecture-detailed.svg",
    [string]$OutputPng = "docs/architecture-detailed.png",
    [int]$Width = 1800,
    [int]$Height = 1200
)

function Test-Cmd($name) { [bool](Get-Command $name -ErrorAction SilentlyContinue) }

function Resolve-AbsPath([string]$p) {
    if ([System.IO.Path]::IsPathRooted($p)) { return $p }
    return (Resolve-Path $p).Path
}

function Find-FirstExistingPath([string[]]$candidates) {
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

if (-not (Test-Path $InputSvg)) {
    Write-Host "[err] Input SVG not found: $InputSvg" -ForegroundColor Red
    exit 1
}

$absIn = Resolve-AbsPath $InputSvg
$absOut = Resolve-AbsPath $OutputPng 2>$null
if (-not $absOut) { $absOut = (Join-Path (Split-Path $absIn -Parent) (([IO.Path]::GetFileNameWithoutExtension($absIn)) + '.png')) }

Write-Host "[*] Rendering SVG -> PNG" -ForegroundColor Cyan
Write-Host "    In : $absIn"
Write-Host "    Out: $absOut ($Width x $Height)"

$succeeded = $false

# 1) Inkscape
if (-not $succeeded -and (Test-Cmd 'inkscape')) {
    Write-Host "[*] Trying Inkscape..."
    & inkscape "$absIn" --export-type=png --export-filename="$absOut" -w $Width -h $Height
    if ($LASTEXITCODE -eq 0 -and (Test-Path $absOut)) { $succeeded = $true }
}

# 2) ImageMagick
if (-not $succeeded -and (Test-Cmd 'magick')) {
    Write-Host "[*] Trying ImageMagick (magick)..."
    & magick convert "$absIn" -resize "${Width}x${Height}" "$absOut"
    if ($LASTEXITCODE -eq 0 -and (Test-Path $absOut)) { $succeeded = $true }
}

# 3) rsvg-convert
if (-not $succeeded -and (Test-Cmd 'rsvg-convert')) {
    Write-Host "[*] Trying rsvg-convert..."
    & rsvg-convert -w $Width -h $Height -o "$absOut" "$absIn"
    if ($LASTEXITCODE -eq 0 -and (Test-Path $absOut)) { $succeeded = $true }
}

# 4) Microsoft Edge headless (screenshot)
if (-not $succeeded) {
    $edgeExe = $null
    if (Test-Cmd 'msedge') { $edgeExe = 'msedge' }
    if (-not $edgeExe) {
        $edgeExe = Find-FirstExistingPath @(
            "$Env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
            "$Env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe"
        )
    }
    if ($edgeExe) {
        Write-Host "[*] Trying Microsoft Edge headless ($edgeExe)..."
        $uri = "file:///" + ($absIn -replace "\\", "/")
        # Try direct SVG first, then fallback to temp HTML wrapper
        & "$edgeExe" --headless=chrome --disable-gpu --screenshot="$absOut" --window-size=${Width},${Height} "$uri"
        if (-not (Test-Path $absOut)) {
            $tmpHtml = [IO.Path]::ChangeExtension($absOut, ".tmp.edge.html")
            $html = @"
<!doctype html>
<html>
<head><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:white}</style></head>
<body>
  <img src="$uri" width="$Width" height="$Height" style="display:block"/>
</body>
</html>
"@
            Set-Content -Path $tmpHtml -Value $html -Encoding UTF8
            $htmlUri = "file:///" + ($tmpHtml -replace "\\", "/")
            & "$edgeExe" --headless=chrome --disable-gpu --screenshot="$absOut" --window-size=${Width},${Height} "$htmlUri"
            Remove-Item -ErrorAction SilentlyContinue $tmpHtml
        }
        if ($LASTEXITCODE -eq 0 -and (Test-Path $absOut)) { $succeeded = $true }
    }
}

# 5) Google Chrome headless (screenshot)
if (-not $succeeded) {
    $chromeExe = $null
    if (Test-Cmd 'chrome') { $chromeExe = 'chrome' }
    elseif (Test-Cmd 'chrome.exe') { $chromeExe = 'chrome.exe' }
    if (-not $chromeExe) {
        $chromeExe = Find-FirstExistingPath @(
            "$Env:ProgramFiles\Google\Chrome\Application\chrome.exe",
            "$Env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe"
        )
    }
    if ($chromeExe) {
        Write-Host "[*] Trying Chrome headless ($chromeExe)..."
        $uri = "file:///" + ($absIn -replace "\\", "/")
        # Try direct SVG first, then fallback to temp HTML wrapper
        & "$chromeExe" --headless=new --disable-gpu --screenshot="$absOut" --window-size=${Width},${Height} "$uri"
        if (-not (Test-Path $absOut)) {
            $tmpHtml = [IO.Path]::ChangeExtension($absOut, ".tmp.chrome.html")
            $html = @"
<!doctype html>
<html>
<head><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:white}</style></head>
<body>
  <img src="$uri" width="$Width" height="$Height" style="display:block"/>
  
</body>
</html>
"@
            Set-Content -Path $tmpHtml -Value $html -Encoding UTF8
            $htmlUri = "file:///" + ($tmpHtml -replace "\\", "/")
            & "$chromeExe" --headless=new --disable-gpu --screenshot="$absOut" --window-size=${Width},${Height} "$htmlUri"
            Remove-Item -ErrorAction SilentlyContinue $tmpHtml
        }
        if ($LASTEXITCODE -eq 0 -and (Test-Path $absOut)) { $succeeded = $true }
    }
}

if ($succeeded) {
    $size = (Get-Item $absOut).Length
    Write-Host "[ok] Rendered: $absOut ($([Math]::Round($size/1KB,1)) KB)" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "[!] Could not render PNG automatically. Please install one of: Inkscape, ImageMagick, rsvg, or ensure Edge/Chrome is available on PATH." -ForegroundColor Yellow
    exit 1
}
