@echo off
echo ========================================
echo   MEUBLE DE FRANCE - CHATBOT
echo   Demarrage complet Backend + Frontend
echo ========================================
echo.

echo [1/4] Verification des repertoires...
if not exist "backend\" (
    echo ❌ ERREUR: Dossier backend introuvable
    pause
    exit /b 1
)

if not exist "frontend\" (
    echo ❌ ERREUR: Dossier frontend introuvable
    pause
    exit /b 1
)

echo ✅ Repertoires OK
echo.

echo [2/4] Verification installation dependances...
if not exist "backend\venv\" (
    echo.
    echo ❌ ERREUR: Environnement virtuel Python non installe!
    echo.
    echo 👉 SOLUTION: Double-cliquez sur INSTALLER.bat d'abord
    echo.
    pause
    exit /b 1
)

if not exist "frontend\node_modules\" (
    echo.
    echo ❌ ERREUR: Dependances Node.js non installees!
    echo.
    echo 👉 SOLUTION: Double-cliquez sur INSTALLER.bat d'abord
    echo.
    pause
    exit /b 1
)

echo ✅ Dependances installees
echo.

echo [3/4] Demarrage BACKEND (port 8000)...
start "Backend - Meuble de France" cmd /k "cd /d "%~dp0backend" && echo Activation environnement virtuel... && venv\Scripts\activate && echo Demarrage serveur FastAPI... && python -m app.main"

echo ⏳ Attente 3 secondes pour laisser le backend demarrer...
timeout /t 3 /nobreak >nul
echo.

echo [4/4] Demarrage FRONTEND (port 5173)...
start "Frontend - Meuble de France" cmd /k "cd /d "%~dp0frontend" && echo Installation dependances si necessaire... && (if not exist "node_modules\" npm install) && echo Demarrage Vite... && npm run dev"

echo.
echo ========================================
echo   ✅ LANCEMENT TERMINE
echo ========================================
echo.
echo 📡 Backend API:  http://localhost:8000
echo 📚 Documentation: http://localhost:8000/docs
echo 🌐 Frontend:     http://localhost:5173
echo.
echo Les 2 fenetres de commande vont s'ouvrir.
echo Attendez que les serveurs demarrent (15-30 secondes).
echo.
echo Pour arreter: Fermez les 2 fenetres ou appuyez Ctrl+C dans chacune.
echo.
pause
