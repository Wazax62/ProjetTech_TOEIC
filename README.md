# Projet TOEIC

- Vous pouvez utiliser ce tutoriel pour réaliser l'installation : [Cliquez-ici](https://youtu.be/VY9SJpZouuY)

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants:

- [Angular](https://angular.io/guide/setup-local) (version 19.2.3)
- [Python](https://www.python.org/downloads/) (version 3.12.1)
- [XAMPP](https://www.apachefriends.org/fr/index.html) (pour la base de données MySQL)

## Installation

### 1. Téléchargement du projet

Téléchargez le fichier ZIP du projet et décompressez-le dans un dossier de votre choix.

### 2. Configuration du back-end

1. Accédez au dossier du projet et naviguez vers le back-end:

   ```bash
   cd chemin/vers/le/projet/back_end
   ```

2. Installez les dépendances Python:

   ```bash
   python -m pip install -r requirement.txt
   ```

3. Configuration de la base de données:

   - Lancez XAMPP et démarrez les services Apache et MySQL
   - Accédez à phpMyAdmin (généralement via http://localhost/phpmyadmin)
   - Créez une nouvelle base de données nommée `toeic_app`
   - Importer à l'intérieur la base vide présente dans le projet


1. Dans un nouveau terminal, accédez au dossier racine du projet:

   ```bash
   cd chemin/vers/le/projet
   ```

2. Installez les dépendances Angular:

   ```bash
   npm install
   ```

3. Le serveur Angular démarrera généralement sur le port 4200. Accédez à l'application via l'URL affichée dans le terminal (habituellement http://localhost:4200/).



