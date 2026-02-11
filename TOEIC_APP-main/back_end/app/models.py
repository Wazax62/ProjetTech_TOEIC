from app import db
from werkzeug.security import check_password_hash, generate_password_hash

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Colonne de type Integer pour l'ID (clé primaire)
    nom = db.Column(db.String(100), nullable=False)  # Colonne pour le nom
    prenom = db.Column(db.String(100), nullable=False)  # Colonne pour le prénom
    email = db.Column(db.String(120), unique=True, nullable=False)  # Colonne pour l'email (unique)
    mot_de_passe = db.Column(db.String(200), nullable=False)  # Colonne pour le mot de passe
    is_active = db.Column(db.Boolean, default=True)  # Colonne pour l'état d'activité de l'enseignant (par défaut actif)

    def __repr__(self):
        return f"<Teacher {self.nom} {self.prenom}>"
    
    def set_password(self, password):
        # Hachage du mot de passe avant de le stocker
        self.mot_de_passe = generate_password_hash(password)

    def check_password(self, password):
        # Vérification du mot de passe avec le mot de passe haché stocké
        return check_password_hash(self.mot_de_passe, password)
