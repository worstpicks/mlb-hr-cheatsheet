# Start a new MLB HR cheat sheet slate: import today's Downloads CSVs, then show what landed in data/.
param(
    [string]$Date = "",
    [switch]$DryRun
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$argsList = @("import-sheet-csvs.py")
if ($Date) { $argsList += @("--date", $Date) }
if ($DryRun) { $argsList += "--dry-run" }

python @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  python recheck-straight.py --import"
    Write-Host "  python build-sheet-2026-XX-XX.py"
    Write-Host "  python patch-XXXX-preview.py"
}
