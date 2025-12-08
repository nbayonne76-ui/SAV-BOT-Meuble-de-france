@echo off
echo ========================================
echo   INSTALLATION - Meuble de France
echo ========================================
echo.

echo [1/4] Verification Python et Node.js...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installe!
    echo Installez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js n'est pas installe!
    echo Installez Node.js depuis: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Python detecte:
python --version
echo ✅ Node.js detecte:
node --version
echo.

echo [2/4] Installation Backend Python...
cd /d "%~dp0backend"

if exist "venv\" (
    echo ⚠️  Environnement virtuel existe deja, suppression...
    rmdir /s /q venv
)

echo Creation environnement virtuel...
python -m venv venv

echo Activation environnement...
call venv\Scripts\activate.bat

echo Installation dependances Python...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erreur installation dependances Python
    pause
    exit /b 1
)

echo ✅ Backend installe avec succes!
echo.

echo [3/4] Installation Frontend Node.js...
cd /d "%~dp0frontend"

if exist "node_modules\" (
    echo ⚠️  node_modules existe, nettoyage...
    rmdir /s /q node_modules
)

echo Installation dependances Node.js (cela peut prendre 2-3 minutes)...
call npm install

if errorlevel 1 (
    echo ❌ Erreur installation dependances Node.js
    pause
    exit /b 1
)

echo ✅ Frontend installe avec succes!
echo.

echo [4/4] Verification finale...
cd /d "%~dp0"

if exist "backend\venv\Scripts\python.exe" (
    echo ✅ Backend: OK
) else (
    echo ❌ Backend: ERREUR
)

if exist "frontend\node_modules\" (
    echo ✅ Frontend: OK
) else (
    echo ❌ Frontend: ERREUR
)

echo.
echo ========================================
echo   ✅ INSTALLATION TERMINEE!
echo ========================================
echo.
echo Prochaine etape:
echo 1. Double-cliquez sur START_ALL.bat
echo 2. Attendez 15-30 secondes
echo 3. Ouvrez http://localhost:5173
echo.
pause
