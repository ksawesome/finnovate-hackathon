<#
.SYNOPSIS
  Remove deprecated Mermaid-exported diagram assets to avoid confusion.

.USAGE
  powershell -ExecutionPolicy Bypass -File .\scripts\cleanup-old-diagrams.ps1
#>

$files = @(
    "docs/mermaid-diagram-2025-11-03-130751.svg",
    "docs/mermaid-diagram-2025-11-03-130936.png"
)

foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "[*] Deleting $f"
        Remove-Item -Force $f
    }
    else {
        Write-Host "[skip] Not found: $f"
    }
}

Write-Host "[ok] Cleanup complete."
