@echo off
cd /d "%~dp0"
echo.
echo  MLB Research local server
echo  =======================
echo.
if not exist "preview\data\research-2026-06-22.json" (
    echo  Fetching research data...
    python fetch-research-slate.py --date 2026-06-22
    echo.
)
echo  Starting server...
echo  Open: http://localhost:8080/research/index.html?date=2026-06-22
echo.
start "" "http://localhost:8080/research/index.html?date=2026-06-22"
python serve-research.py
