@echo off
echo ========================================
echo   REDEMARRAGE FORCE DU BACKEND
echo ========================================
echo.

echo [1/4] Arret de tous les processus Python...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1

echo [2/4] Attente 5 secondes...
timeout /t 5 /nobreak

echo [3/4] Nettoyage du cache Python...
cd backend
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

echo [4/4] Demarrage du backend avec la configuration corrigee...
echo.
echo ========================================
echo Backend: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo ========================================
echo.

start "Backend SAV" cmd /k "python -m app.main"

echo.
echo Backend demarre! Attendez 5 secondes puis testez le chatbot.
echo.
timeout /t 5 /nobreak

start http://localhost:5173

pause
