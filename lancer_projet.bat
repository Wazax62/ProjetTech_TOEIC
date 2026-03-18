@echo off
title LANCEUR PROJET TOEIC
echo ==========================================
echo      DEMARRAGE DU PROJET (FLASK + ANGULAR)
echo ==========================================

echo [1/2] Démarrage du serveur Flask (Port 5000)...
start /min "BACKEND - Flask" cmd /k "cd back_end && python run.py"

echo [2/2] Démarrage du serveur Angular (Port 4200)...
start /min "FRONTEND - Angular" cmd /k "npm start"

echo.
echo ------------------------------------------
echo Attente du chargement des serveurs...
echo ------------------------------------------

timeout /t 15 >nul
start /max http://localhost:4200/login

exit