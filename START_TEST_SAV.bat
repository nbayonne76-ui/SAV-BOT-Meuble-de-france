@echo off
echo ================================================
echo    TEST SYSTEME SAV - MEUBLE DE FRANCE
echo ================================================
echo.

echo [1/3] Verification des fichiers...
if exist "backend\app\services\tone_analyzer.py" (
    echo   [OK] tone_analyzer.py
) else (
    echo   [ERREUR] tone_analyzer.py manquant
    pause
    exit /b 1
)

if exist "backend\app\services\client_summary_generator.py" (
    echo   [OK] client_summary_generator.py
) else (
    echo   [ERREUR] client_summary_generator.py manquant
    pause
    exit /b 1
)

if exist "backend\app\services\sav_workflow_engine.py" (
    echo   [OK] sav_workflow_engine.py
) else (
    echo   [ERREUR] sav_workflow_engine.py manquant
    pause
    exit /b 1
)

if exist "backend\app\api\endpoints\sav.py" (
    echo   [OK] sav.py (API endpoint)
) else (
    echo   [ERREUR] sav.py manquant
    pause
    exit /b 1
)

echo.
echo [2/3] Tous les fichiers SAV sont presents !
echo.
echo [3/3] Demarrage du backend...
echo.
echo ================================================
echo BACKEND en cours de demarrage sur http://localhost:8000
echo Documentation API: http://localhost:8000/docs
echo ================================================
echo.
echo ASTUCE: Ouvrez un autre terminal et lancez:
echo   cd frontend
echo   npm start
echo.
echo Pour tester l'API SAV, consultez TEST_SAV_GUIDE.md
echo ================================================
echo.

cd backend
python -m app.main
