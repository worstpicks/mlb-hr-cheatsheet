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

$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "Git not found in PATH. Install Git for Windows, then re-open PowerShell:" -ForegroundColor Yellow
    Write-Host "  https://git-scm.com/download/win" -ForegroundColor Cyan
    exit 1
}

if (-not (Test-Path (Join-Path $here "index.html"))) {
    Write-Host "Missing index.html in $here — run your cheat sheet build first." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path (Join-Path $here ".git"))) {
    & git init
}

# Local identity only for this repo (override with your own if you prefer)
$email = (& git config user.email 2>$null)
if (-not $email) {
    & git config user.email "cheatsheet@local"
    & git config user.name "MLB HR Cheatsheet"
}

& git add index.html README.md .gitignore setup-github-pages.ps1
& git status
$status = & git status --porcelain
if ($status) {
    & git commit -m "Initial MLB HR cheat sheet for GitHub Pages"
}

& git branch -M main 2>$null

$remoteUrl = "https://github.com/$GitHubUser/$RepoName.git"
Write-Host ""
Write-Host "=== Next: create empty repo on GitHub ===" -ForegroundColor Green
Write-Host "  https://github.com/new?name=$RepoName (empty repo, no README)"
Write-Host ""
Write-Host "=== Then run (first time only) ===" -ForegroundColor Green
Write-Host "  git remote remove origin 2>`$null"
Write-Host "  git remote add origin $remoteUrl"
Write-Host "  git push -u origin main"
Write-Host ""
Write-Host "=== Enable Pages ===" -ForegroundColor Green
Write-Host "  Repo → Settings → Pages → Branch main, folder / (root)"
Write-Host ""
Write-Host "Your site will be:" -ForegroundColor Cyan
Write-Host "  https://$GitHubUser.github.io/$RepoName/" -ForegroundColor Cyan
