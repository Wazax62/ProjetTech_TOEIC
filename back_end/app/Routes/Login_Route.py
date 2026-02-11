# ------------------------------------------------------
# DÉPENDANCES NÉCESSAIRES
# ------------------------------------------------------

from flask import jsonify, request
from app.Models.Prof import Prof
import jwt
import datetime
from app.config import Config

# ------------------------------------------------------
# Fonction de login pour les enseignants
# ------------------------------------------------------
def login_user(app):
    @app.route('/api/login', methods=['POST'])
    def login():
        # Récupérer les données envoyées dans le corps de la requête
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Vérifier que l'email et le mot de passe sont présents
        if not email or not password:
            return jsonify({"status": "error", "message": "Email et mot de passe requis"}), 400

        # Chercher l'utilisateur dans la base de données
        teacher = Prof.query.filter_by(email=email).first()
        
        # Si l'utilisateur n'existe pas ou que le mot de passe est incorrect
        if not teacher or not teacher.check_password(password): 
            return jsonify({"status": "error", "message": "Nom d'utilisateur ou mot de passe incorrect"}), 401

        # Si le compte n'est pas encore activé
        if not teacher.is_active:
            return jsonify({"status": "success", "accountActivated": False}), 200

        # Générer un token JWT
        token = jwt.encode({
            'id': teacher.id,
            'email': teacher.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, Config.SECRET_KEY, algorithm='HS256')

        # Connexion réussie avec compte activé
        return jsonify({
            "status": "success", 
            "accountActivated": True,
            "token": token,
            "user": {
                "id": teacher.id,
                "nom": teacher.nom,
                "prenom": teacher.prenom,
                "email": teacher.email
            }
        }), 200

