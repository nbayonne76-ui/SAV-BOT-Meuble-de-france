@echo off
echo ================================================
echo   BACKEND AVEC VARIABLE D'ENVIRONNEMENT FORCEE
echo ================================================
echo.

cd backend

echo Chargement de la cle API depuis .env...
for /f "tokens=2 delims==" %%a in ('findstr /b "OPENAI_API_KEY" .env') do set OPENAI_API_KEY=%%a

echo Cle API chargee: %OPENAI_API_KEY:~0,20%...
echo.

echo Nettoyage du cache Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

echo.
echo Demarrage du serveur...
echo.
echo ================================================
echo Backend: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo ================================================
echo.

python -m app.main

pause
