@echo off
echo ========================================
echo   IMPORT PRODUITS - Meuble de France
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Installation des dependances de scraping...
cd backend
call venv\Scripts\activate.bat
python -m pip install beautifulsoup4 lxml --quiet

if errorlevel 1 (
    echo ❌ Erreur installation dependances
    pause
    exit /b 1
)

echo ✅ Dependances installees
echo.

echo [2/3] Lancement du scraping...
echo 🔍 Recuperation des produits depuis mobilierdefrance.com
echo ⏱️  Cela peut prendre 1-2 minutes...
echo.

cd ..
python scripts\scraper_mobilier_france.py

if errorlevel 1 (
    echo.
    echo ⚠️  Le scraping a rencontre des problemes
    echo.
    echo 💡 SOLUTIONS ALTERNATIVES:
    echo.
    echo 1. IMPORT MANUEL:
    echo    - Exportez vos produits en CSV
    echo    - Placez le fichier dans: backend\data\produits.csv
    echo    - Relancez ce script
    echo.
    echo 2. API INTEGRATION:
    echo    - Si vous avez une API produits
    echo    - Contactez votre equipe technique
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Verification du catalogue...

if exist "backend\data\catalog.json" (
    echo ✅ Catalogue genere avec succes!
    echo.
    echo 📊 Consultez: backend\data\catalog.json
    echo.
) else (
    echo ❌ Catalogue non genere
)

echo ========================================
echo   PROCHAINES ETAPES
echo ========================================
echo.
echo 1. Verifiez le catalogue: backend\data\catalog.json
echo 2. Relancez le chatbot: START_ALL.bat
echo 3. Testez avec une vraie reference
echo.
pause
