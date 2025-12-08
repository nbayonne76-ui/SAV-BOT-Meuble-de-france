@echo off
echo ====================================
echo RESTART BACKEND - Meuble de France
echo ====================================
echo.

echo [1/3] Arret de tous les serveurs Python sur le port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Arret du processus %%a...
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo [2/3] Attente 3 secondes...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Demarrage du nouveau serveur backend...
cd backend
start "Meuble de France Backend" cmd /k "python -m app.main"

echo.
echo ====================================
echo Backend redemarre avec succes!
echo Backend: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo ====================================
echo.
pause
