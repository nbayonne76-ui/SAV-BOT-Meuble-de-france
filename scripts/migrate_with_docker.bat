@echo off
REM Run this after starting docker-compose
docker-compose exec backend alembic upgrade head
if %errorlevel% neq 0 (
  echo Migrations failed.
  exit /b %errorlevel%
)

echo Migrations applied successfully.
