@echo off
echo Fermeture FORCEE de tous les processus Python...
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe
echo.
echo Processus Python arretes!
pause
