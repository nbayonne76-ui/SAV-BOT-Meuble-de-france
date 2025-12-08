@echo off
echo ========================================
echo   DEMARRAGE FRONTEND - Meuble de France
echo ========================================
echo.

cd /d "%~dp0frontend"

echo [1/2] Verification Node modules...
if not exist "node_modules\" (
    echo Installation dependencies...
    call npm install
)

echo [2/2] Demarrage serveur frontend...
echo.
echo ✅ Frontend disponible sur: http://localhost:5173
echo 🔗 Se connecte au backend: http://localhost:8000
echo.
echo Le navigateur va s'ouvrir automatiquement...
echo Appuyez sur Ctrl+C pour arreter
echo.

call npm run dev

pause
