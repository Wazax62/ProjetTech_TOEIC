# ------------------------------------------------------
# DÉPENDANCES NÉCESSAIRES
# ------------------------------------------------------



import logging
import os
from flask import jsonify, request
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
from app import db, mail
from app.Models.Prof import Prof
from itsdangerous import BadSignature, SignatureExpired


# ------------------------------------------------------
# CLÉ SECRÈTE POUR SIGNER LES TOKENS
# ------------------------------------------------------
# La clé secrète est générée aléatoirement et utilisée pour signer les tokens
# afin d'assurer leur sécurité.
secret_key = os.urandom(24)   # Génération d'une clé secrète aléatoire

# ------------------------------------------------------
# INITIALISATION DU SERIALIZER
# ------------------------------------------------------
# Utilisation de URLSafeTimedSerializer pour générer un token sécurisé
# Ce token sera envoyé dans le lien d'activation du compte.
s = URLSafeTimedSerializer(secret_key)

# ------------------------------------------------------
# FONCTION GÉNÉRANT LE LIEN D'ACTIVATION
# ------------------------------------------------------
def generate_activation_link(email):
    """
    Cette fonction génère un lien d'activation contenant un token sécurisé pour activer le compte de l'utilisateur.

    :param email: L'email de l'utilisateur à activer
    :return: Le lien d'activation avec le token
    """
    token = s.dumps(email, salt='email-activation')  # Génération du token
    return f'http://localhost:4200/activate-account/{token}'  # Génération du lien d'activation

# ------------------------------------------------------
# ROUTE D'ENREGISTREMENT D'ENSEIGNANT
# ------------------------------------------------------
def register_routes(app):
    """
    La route /api/register permet l'enregistrement d'un nouvel enseignant. Cette fonction prend les informations
    d'un enseignant via une requête POST, vérifie les données, les enregistre dans la base de données et envoie
    un email de confirmation avec un lien d'activation.
    """

    @app.route('/api/register', methods=['POST'])
    def register():
        try:
            # Récupération des données envoyées par le client
            data = request.get_json()
            print("Données reçues:", data)

            # Extraction des données spécifiques
            nom = data.get('firstName')
            prenom = data.get('lastName')
            email = data.get('email')
            mot_de_passe = data.get('password')

            # Vérification des champs obligatoires
            if not nom or not prenom or not email or not mot_de_passe:
                return jsonify({"status": "error", "message": "Tous les champs sont obligatoires"}), 400

            # Vérification si l'email existe déjà dans la base de données
            teacher_exists = Prof.query.filter_by(email=email).first()
            if teacher_exists:
                return jsonify({"status": "error", "message": "L'email est déjà utilisé"}), 400

            # Hachage du mot de passe avant de le stocker
            hashed_password = generate_password_hash(mot_de_passe, method='pbkdf2:sha256')

            # Création d'un nouvel enseignant (professeur) avec l'état 'is_active' mis à False
            new_teacher = Prof(nom=nom, prenom=prenom, email=email, mot_de_passe=hashed_password, is_active=False)

            # Ajout de l'enseignant à la base de données
            db.session.add(new_teacher)
            db.session.commit()

            # Génération du lien d'activation
            activation_link = generate_activation_link(email)

            # Création du message d'email
           
            msg = Message(
                subject="TOEICGrader - Activez votre compte pour commencer la correction TOEIC",
                sender='toeicgrader@gmail.com',
                recipients=[email]
            )

            # Dans votre code Python, modifiez la partie du footer dans le HTML:

            # Corps de l'email en HTML
            msg.html = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Activation de compte TOEICGrader</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        max-width: 600px;
                        margin: 0 auto;
                    }}
                    .header {{
                        background-color: #0046a0; /* Bleu foncé uniquement */
                        color: white;
                        padding: 20px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 20px;
                        background-color: #f9f9f9;
                        border-left: 4px solid #0046a0; /* Bleu foncé uniquement */
                    }}
                    .button {{
                        display: inline-block;
                        background-color: #0046a0; /* Bleu foncé uniquement */
                        color: white;
                        text-decoration: none;
                        padding: 12px 25px;
                        border-radius: 5px;
                        margin: 20px 0;
                        font-weight: bold;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 0.9em;
                        text-align: center;
                        color: #666;
                    }}
                    .signature {{
                        margin-top: 20px;
                        font-weight: bold;
                        color: #0046a0; /* Bleu foncé uniquement */
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>TOEICGrader</h1>
                    <p>Votre plateforme de correction TOEIC</p>
                </div>
                
                <div class="content">
                    <p>Bonjour {prenom} {nom},</p>
                    
                    <p>Nous vous remercions de vous être inscrit(e) à <strong>TOEICGrader</strong>. Votre compte a été créé avec succès.</p>
                    
                    <p>Pour commencer à utiliser notre plateforme de correction TOEIC, veuillez activer votre compte en cliquant sur le lien ci-dessous :</p>
                    
                    <div style="text-align: center;">
                        <a href="{activation_link}" class="button">Activer mon compte</a>
                    </div>
                    
                    <p>Si le bouton ne fonctionne pas, vous pouvez copier et coller ce lien dans votre navigateur :</p>
                    <p style="word-break: break-all; font-size: 0.9em;">{activation_link}</p>
                    
                    <p>Ce lien expirera dans 24 heures.</p>
                    
                    <div class="signature">
                        L'équipe TOEICGrader
                    </div>
                </div>
                
                <div class="footer">
                    <p>© 2025 TOEICGrader - Plateforme de correction TOEIC</p>
                </div>
            </body>
            </html>
            """
            # Envoi du message
            mail.send(msg)

            # Réponse en cas de succès
            return jsonify({"status": "success", "emailSent": True, "message": "Enseignant enregistré avec succès"}), 201

        except Exception as e:
            # En cas d'erreur, on enregistre l'erreur et renvoie un message générique
            print("Erreur survenue:", e)
            logging.error(f"Erreur dans la route /api/register: {e}")

            return jsonify({"status": "error", "message": f"Erreur interne du serveur: {str(e)}"}), 500


# ------------------------------------------------------
# ROUTE D'ACTIVATION DU COMPTE
# ------------------------------------------------------

def activate(app):
    
    @app.route('/api/activate/<token>', methods=['GET'])
    def activate_account(token):
        try:
            # Décodage du token pour obtenir l'email (le token doit être valide et dans les 3600 secondes)
            email = s.loads(token, salt='email-activation', max_age=3600)  # max_age=3600 signifie que le lien expire après 1 heure
            
            # Recherche de l'enseignant dans la base de données avec l'email récupéré
            teacher = Prof.query.filter_by(email=email).first()
            
            # Si aucun enseignant n'est trouvé, renvoyer une erreur
            if not teacher:
                return jsonify({"status": "error", "message": "Utilisateur non trouvé"}), 404

            # Si l'enseignant est trouvé, activer son compte
            teacher.is_active = True
            db.session.commit()  # Sauvegarde dans la base de données

            # Retourner une réponse de succès si l'activation est réussie
            return jsonify({"status": "success", "message": "Compte activé avec succès"}), 200

        except SignatureExpired:
            # Si le token a expiré (au-delà de l'heure), retourner une erreur
            return jsonify({"status": "error", "message": "Le lien d'activation a expiré"}), 400
        except BadSignature:
            # Si le token est invalide ou corrompu, retourner une erreur
            return jsonify({"status": "error", "message": "Jeton d'activation invalide"}), 400