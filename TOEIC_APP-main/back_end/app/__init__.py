from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Charger la configuration
    app.config.from_object('app.config.Config')

    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # Initialiser Flask-Mail

    # Configurer CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:4200", "allow_headers": ["Content-Type"], "methods": ["GET", "POST", "OPTIONS"]}})

    # Importer les modèles après l'initialisation
    from app import models

    # Enregistrer les routes
    from app.routes import register_routes
   

    return app
