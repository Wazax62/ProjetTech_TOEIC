from app import db
from werkzeug.security import check_password_hash, generate_password_hash

# Définition du modèle "Prof" représentant un enseignant dans la base de données
class Prof(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID unique de l'enseignant, clé primaire
    nom = db.Column(db.String(100), nullable=False)  # Nom de l'enseignant (champ requis)
    prenom = db.Column(db.String(100), nullable=False)  # Prénom de l'enseignant (champ requis)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email unique de l'enseignant (champ requis)
    mot_de_passe = db.Column(db.String(200), nullable=False)  # Mot de passe haché de l'enseignant (champ requis)
    is_active = db.Column(db.Boolean, default=True)  # Statut d'activation (par défaut à True, actif)
    # Méthode de représentation pour afficher un professeur sous forme de chaîne de caractères
    def __repr__(self):
        return f"<Prof {self.nom} {self.prenom}>"
    
    # Méthode pour définir le mot de passe de manière sécurisée
    def set_password(self, password):
        self.mot_de_passe = generate_password_hash(password)  # Hache le mot de passe et le stocke dans la base

    # Méthode pour vérifier si le mot de passe donné correspond au mot de passe stocké
    def check_password(self, password):
        return check_password_hash(self.mot_de_passe, password)  # Vérifie le mot de passe avec le hachage stocké
