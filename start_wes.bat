@echo off
setlocal enabledelayedexpansion

REM Weather Enrichment Service launcher for Windows.
REM It starts the whole stack with Docker Compose and opens the frontend.

cd /d "%~dp0"

set FRONTEND_URL=http://localhost:4200
set BACKEND_HEALTH_URL=http://localhost:8000/health
set COMPOSE_CMD=

echo.
echo ========================================
echo  Weather Enrichment Service launcher
echo ========================================
echo.

where docker >nul 2>nul
if errorlevel 1 (
  echo ERROR: Docker was not found.
  echo Install Docker Desktop first, then run this file again.
  pause
  exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
  echo ERROR: Docker is installed, but Docker Desktop / Docker daemon is not running.
  echo Start Docker Desktop first, wait until it is ready, then run this file again.
  pause
  exit /b 1
)

docker compose version >nul 2>nul
if not errorlevel 1 (
  set COMPOSE_CMD=docker compose
) else (
  where docker-compose >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Docker Compose was not found.
    echo Install Docker Desktop with Docker Compose support.
    pause
    exit /b 1
  )
  set COMPOSE_CMD=docker-compose
)

if not exist .env (
  if exist .env.example (
    copy .env.example .env >nul
    echo Created .env from .env.example
  )
)

echo Starting containers from:
echo %cd%
echo.
%COMPOSE_CMD% up -d --build
if errorlevel 1 (
  echo.
  echo ERROR: Docker Compose failed to start the application.
  pause
  exit /b 1
)

echo.
echo Waiting for backend health check at %BACKEND_HEALTH_URL% ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "for ($i=0; $i -lt 60; $i++) { try { $r = Invoke-WebRequest -UseBasicParsing '%BACKEND_HEALTH_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch { Start-Sleep -Seconds 2 } }; exit 1"
if errorlevel 1 (
  echo Backend did not answer yet. Containers may still be starting.
) else (
  echo Backend is ready.
)

echo.
echo Application is running.
echo Frontend:    %FRONTEND_URL%
echo API docs:    http://localhost:8000/docs
echo Health:      %BACKEND_HEALTH_URL%
echo.

start "" "%FRONTEND_URL%"

echo Useful commands from this folder:
echo   docker compose ps
echo   docker compose logs -f backend
echo   docker compose logs -f celery_worker
echo   docker compose down
echo.
echo The app will keep running in Docker after this window closes.
pause
