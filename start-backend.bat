@echo off
echo ========================================
echo   DEMARRAGE BACKEND - Meuble de France
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/3] Activation environnement virtuel...
call venv\Scripts\activate.bat

echo [2/3] Verification dependencies...
pip list | find "fastapi" >nul
if errorlevel 1 (
    echo Installation dependencies...
    pip install -r requirements.txt
)

echo [3/3] Demarrage serveur backend...
echo.
echo ✅ Backend disponible sur: http://localhost:8000
echo 📚 Documentation API: http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

python -m app.main

pause
