@echo off
echo ================================================
echo   BACKEND MEUBLE DE FRANCE - VERSION CORRIGEE
echo ================================================
echo.

cd backend

echo [1/2] Nettoyage du cache Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

echo [2/2] Demarrage du serveur...
echo.
echo ================================================
echo Backend: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo ================================================
echo.

python -m app.main

pause
