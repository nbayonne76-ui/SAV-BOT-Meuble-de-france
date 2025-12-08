@echo off
echo ================================================
echo   DEMARRAGE COMPLET - MEUBLE DE FRANCE SAV
echo ================================================
echo.

echo [1/2] Demarrage du BACKEND...
cd backend
start "Backend SAV - Meuble de France" cmd /k "for /d /r . %%d in (__pycache__) do @if exist \"%%d\" rd /s /q \"%%d\" 2>nul & del /s /q *.pyc >nul 2>&1 & python -m app.main"
cd ..

echo.
echo Attente de 8 secondes pour que le backend demarre...
timeout /t 8 /nobreak

echo.
echo [2/2] Demarrage du FRONTEND...
cd frontend
start "Frontend SAV - Meuble de France" cmd /k "npm run dev"
cd ..

echo.
echo ================================================
echo   DEMARRAGE TERMINE!
echo ================================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Attendez 10 secondes puis ouvrez votre navigateur...
echo.

timeout /t 10 /nobreak
start http://localhost:5173

pause
