@echo off
echo ================================================
echo   DEMARRAGE ULTRA-SIMPLE - CLE API EN DUR
echo ================================================
echo.

REM Definir la cle API directement comme variable d'environnement
set OPENAI_API_KEY=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
set SECRET_KEY=mdf-chatbot-secret-key
set DEBUG=True

echo Cle API definie: %OPENAI_API_KEY:~0,20%...
echo.

cd backend

echo Nettoyage cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc >nul 2>&1

echo.
echo Demarrage backend...
python -m app.main

pause
