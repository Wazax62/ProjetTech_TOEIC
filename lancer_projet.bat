@echo off
title LANCEUR PROJET TOEIC
echo ==========================================
echo      DEMARRAGE DU PROJET (FLASK + ANGULAR)
echo ==========================================

:: 1. Lancement du Back-end
echo [1/2] Démarrage du serveur Flask (Port 5000)...
:: On entre dans back_end, on active l'env et on lance run.py
start "BACKEND - Flask" cmd /k "cd back_end && python run.py"

:: 2. Lancement du Front-end
echo [2/2] Démarrage du serveur Angular (Port 4200)...
:: npm start se lance depuis la racine car package.json est là
start "FRONTEND - Angular" cmd /k "npm start"

echo.
echo ------------------------------------------
echo Attente du chargement des serveurs...
echo ------------------------------------------

:: Attente de 12 secondes avant d'ouvrir le navigateur
timeout /t 12 >nul
start http://localhost:4200/login

exit