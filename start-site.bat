@echo off
REM Double-click this file to start Campus Customs.
REM It opens two windows (backend + frontend). Keep them open while you use
REM the site. To stop the site, close both windows.

REM Make sure Node.js is findable even in windows opened before it was installed.
set "PATH=C:\Program Files\nodejs;%PATH%"

start "Campus Customs - backend (port 8000)" /D "%~dp0backend" cmd /k .venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
start "Campus Customs - frontend (port 5173)" /D "%~dp0frontend" cmd /k npm run dev

echo Starting servers... the site will open in your browser in a few seconds.
timeout /t 6 /nobreak >nul
start "" http://localhost:5173
