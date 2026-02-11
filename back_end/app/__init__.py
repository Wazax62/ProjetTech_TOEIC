from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail


# from app.Models.Prof import Prof
# from app.Models.Teacher import Test, ReponseJuste


# Initialisation des extensions globales
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    CORS(app) # <-- Indispensable !
    app.config.from_object('app.config.Config')

    # Import models here
    from app.Models.Prof import Prof
    from app.Models.myModels import Site, Promotion, Groupe,Test, Etudiant, Score, ReponseProf, ReponseEtudiant, Semestre

    from app.Models.Teacher import ReponseJuste, TestDetails
    

   
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app) 

   
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200", "allow_headers": ["Content-Type"], "methods": ["GET", "POST", "OPTIONS", "DELETE", "PUT"]}})    
   
    from app.Routes.Etudiant_Routes import init_etudiant_routes
    from app.Routes.Evaluations_Routes import register_evaluation_routes
    from app.Routes.Groupe_Routes import init_groupe_routes
    from app.Routes.Login_Route import login_user
    from app.Routes.Promotion_Routes import init_promotion_routes
    from app.Routes.Register_Routes import register_routes,activate
    from app.Routes.Scores_Routes import init_score_routes
    from app.Routes.Semestre_Routes import init_semestre_routes
    from app.Routes.Site_Routes import init_site_routes
    from app.Routes.Test_Routes import register_test_routes
    init_etudiant_routes(app)
    register_evaluation_routes(app)
    init_groupe_routes(app)
    login_user(app)
    init_promotion_routes(app)
    register_routes(app)
    activate(app)
    init_score_routes(app)
    init_semestre_routes(app)
    init_site_routes(app)
    register_test_routes(app)
    return app
