#Requires -Version 5.1
<#
.SYNOPSIS
  Initialize git in this folder and print exact commands to connect GitHub Pages.

.PARAMETER GitHubUser
  Your GitHub username (e.g. allmi).

.PARAMETER RepoName
  New empty repo name on GitHub (default: mlb-hr-cheatsheet).
#>
param(
    [Parameter(Mandatory = $true)]
    [string] $GitHubUser,
    [string] $RepoName = "mlb-hr-cheatsheet"
)

$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
Set-Location $here

function Resolve-GitExe {
    $cmd = Get-Command git -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) { return $cmd.Source }
    foreach ($candidate in @(
            "${env:ProgramFiles}\Git\bin\git.exe",
            "${env:ProgramFiles(x86)}\Git\bin\git.exe",
            "${env:LOCALAPPDATA}\Programs\Git\bin\git.exe"
        )) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) { return $candidate }
    }
    return $null
}

$gitExe = Resolve-GitExe
if (-not $gitExe) {
    Write-Host "Git not found (PATH or standard install locations). Install Git for Windows:" -ForegroundColor Yellow
    Write-Host "  https://git-scm.com/download/win" -ForegroundColor Cyan
    exit 1
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Using Git at: $gitExe (add Git\bin to PATH so `"git`" works everywhere)" -ForegroundColor DarkGray
}

if (-not (Test-Path (Join-Path $here "index.html"))) {
    Write-Host "Missing index.html in $here — run your cheat sheet build first." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path (Join-Path $here ".git"))) {
    & $gitExe init
}

# Local identity only for this repo (override with your own if you prefer)
$email = (& $gitExe config user.email 2>$null)
if (-not $email) {
    & $gitExe config user.email "cheatsheet@local"
    & $gitExe config user.name "MLB HR Cheatsheet"
}

& $gitExe add index.html README.md .gitignore setup-github-pages.ps1
& $gitExe status
$status = & $gitExe status --porcelain
if ($status) {
    & $gitExe commit -m "Initial MLB HR cheat sheet for GitHub Pages"
}

& $gitExe branch -M main 2>$null

$remoteUrl = "https://github.com/$GitHubUser/$RepoName.git"
Write-Host ""
Write-Host "=== Next: create empty repo on GitHub ===" -ForegroundColor Green
Write-Host "  https://github.com/new?name=$RepoName (empty repo, no README)"
Write-Host ""
Write-Host "=== Then run (first time only) ===" -ForegroundColor Green
Write-Host "  & `"$gitExe`" remote remove origin 2>`$null"
Write-Host "  & `"$gitExe`" remote add origin $remoteUrl"
Write-Host "  & `"$gitExe`" push -u origin main"
Write-Host ""
Write-Host "=== Enable Pages ===" -ForegroundColor Green
Write-Host "  Repo → Settings → Pages → Branch main, folder / (root)"
Write-Host ""
Write-Host "Your site will be:" -ForegroundColor Cyan
Write-Host "  https://$GitHubUser.github.io/$RepoName/" -ForegroundColor Cyan
