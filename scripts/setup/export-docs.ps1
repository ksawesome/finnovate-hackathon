<#
.SYNOPSIS
  Export key Markdown docs to PDF using Pandoc on Windows PowerShell.

.REQUIRES
  - pandoc (https://pandoc.org/installing.html)
  - Optional: wkhtmltopdf (https://wkhtmltopdf.org/) or a LaTeX engine (xelatex)

.USAGE
  powershell -ExecutionPolicy Bypass -File .\scripts\export-docs.ps1
#>

param(
    [string[]] $Docs = @(
        "docs/Architecture.md",
        "docs/Storage-Architecture.md",
        "docs/Concept-Note.md"
    )
)

function Test-Cmd($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

function Get-PdfEngine() {
    if (Test-Cmd "wkhtmltopdf") { return "wkhtmltopdf" }
    elseif (Test-Cmd "xelatex") { return "xelatex" }
    else { return $null }
}

if (-not (Test-Cmd "pandoc")) {
    Write-Host "[!] pandoc not found. Please install pandoc first:" -ForegroundColor Yellow
    Write-Host "    choco install pandoc   # or download from pandoc.org" -ForegroundColor Yellow
    exit 1
}

$engine = Get-PdfEngine
if ($engine) {
    Write-Host "[*] Using PDF engine: $engine"
}
else {
    Write-Host "[!] No explicit PDF engine found (wkhtmltopdf/xelatex). Pandoc will use defaults, which may require LaTeX." -ForegroundColor Yellow
}

$exitCode = 0
foreach ($md in $Docs) {
    if (-not (Test-Path $md)) {
        Write-Host "[skip] Missing: $md" -ForegroundColor DarkYellow
        continue
    }
    $pdf = [System.IO.Path]::ChangeExtension($md, ".pdf")
    $args = @("-s", $md, "-o", $pdf, "--from", "gfm", "--toc")
    if ($engine) { $args += @("--pdf-engine", $engine) }
    Write-Host "[*] Exporting: $md -> $pdf"
    & pandoc @args
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[err] pandoc failed for $md (exit $LASTEXITCODE)" -ForegroundColor Red
        $exitCode = $LASTEXITCODE
    }
    else {
        Write-Host "[ok] $pdf"
    }
}

exit $exitCode
