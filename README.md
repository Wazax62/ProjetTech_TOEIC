# Projet TOEIC

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
   pip install -r requirements.txt
   ```

3. Configuration de la base de données:

   - Lancez XAMPP et démarrez les services Apache et MySQL
   - Accédez à phpMyAdmin (généralement via http://localhost/phpmyadmin)
   - Créez une nouvelle base de données nommée `toeic_app`
   - Le fichier `back_end/app/config.py` contient la configuration par défaut:
     ```python
     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:@localhost/toeic_app'
     ```
   - Si nécessaire, modifiez ce paramètre pour correspondre à votre configuration MySQL (nom d'utilisateur, mot de passe, etc.)

4. Création des tables de la base de données avec SQLAlchemy:

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Démarrez le serveur back-end:

   ```bash
   python run.py
   ```

   **Attention**: Le back-end doit s'exécuter sur le port 5000. Si ce port est déjà utilisé, modifiez la configuration dans le fichier `run.py` et assurez-vous de mettre à jour les URLs correspondantes dans le front-end.

### 3. Configuration du front-end Angular

1. Dans un nouveau terminal, accédez au dossier racine du projet:

   ```bash
   cd chemin/vers/le/projet
   ```

2. Installez les dépendances Angular:

   ```bash
   npm install
   ```

3. Démarrez le serveur de développement Angular:

   ```bash
   npm start
   ```

4. Le serveur Angular démarrera généralement sur le port 4200. Accédez à l'application via l'URL affichée dans le terminal (habituellement http://localhost:4200/).

## Configuration du fichier config.py

Le fichier `back_end/app/config.py` contient les paramètres suivants que vous pouvez modifier selon vos besoins:

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre-clé-secrète'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:@localhost/toeic_app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'toeicgrader@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'spet xrcx nlxe upjc')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'toeicgrader@gmail.com')
```

Paramètres à modifier si nécessaire:

- `SQLALCHEMY_DATABASE_URI`: URL de connexion à la base de données

## Structure du projet

```
projet-toeic/
│
├── back_end/
│   ├── app/
│   │   ├── config.py      # Configuration de la base de données et email
│   │   └── ...            # Autres fichiers de l'application
│   ├── requirements.txt   # Liste des dépendances Python
│   └── run.py             # Script de démarrage du serveur
│
└── src/                   # Code source Angular
    ├── app/
    ├── assets/
    └── ...
```

## Utilisation

Une fois que le back-end et le front-end sont en cours d'exécution, vous pouvez accéder à l'application TOEIC en ouvrant votre navigateur et en naviguant vers l'URL du front-end (généralement http://localhost:4200/).

## Résolution des problèmes courants

- Si vous rencontrez des erreurs lors de la connexion à la base de données, vérifiez que:

  - Les services XAMPP sont bien démarrés
  - La base de données `toeic_app` a été créée correctement
  - Les informations de connexion dans `app/config.py` correspondent à votre configuration MySQL

- Si le front-end ne peut pas communiquer avec le back-end, vérifiez que:
  - Le serveur back-end est bien en cours d'exécution sur le port 5000
  - Les URLs dans le code front-end pointent vers le bon port (http://localhost:5000)
