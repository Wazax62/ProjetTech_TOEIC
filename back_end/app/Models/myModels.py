from app import db
from datetime import datetime


# Tables de liaison pour les relations many-to-many
test_site = db.Table(
    'test_site',
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True),
    db.Column('site_id', db.Integer, db.ForeignKey('site.id'), primary_key=True)
)

test_promotion = db.Table(
    'test_promotion',
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True),
    db.Column('promotion_id', db.Integer, db.ForeignKey('promotion.id'), primary_key=True)
)

test_groupe = db.Table(
    'test_groupe',
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True),
    db.Column('groupe_id', db.Integer, db.ForeignKey('groupe.id'), primary_key=True),
    db.Column('feuille_generee', db.Boolean, default=False) 
)




class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)  # Exemple : "Boulogne", "Calais", etc.
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
        }

class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)  # Exemple : "ING1 2024-2025"
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    site = db.relationship('Site', backref='promotions')
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'site_id': self.site_id,
            'site': self.site.nom
        }

class Groupe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)  # Exemple : "Cls 1 24-25 PODVIN"
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestre.id'), nullable=False)

    promotion = db.relationship('Promotion', backref='groupes')
    site = db.relationship('Site', backref='groupes')
    semestre = db.relationship('Semestre', backref='groupes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'promotion_id': self.promotion_id,
            'promotion': self.promotion.nom,
            'site_id': self.site_id,  
            'site': self.site.nom,
            'semestre_id': self.semestre_id,  
            'semestre': self.semestre.nom 
        }


class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.id'), nullable=False)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupe.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestre.id'), nullable=False) 
    specialite = db.Column(db.String(100), nullable=False)  # Exemple : "Informatique", "Génie Civil"

    promotion = db.relationship('Promotion', backref='etudiants')
    groupe = db.relationship('Groupe', backref='etudiants')
    site = db.relationship('Site', backref='etudiants')
    semestre = db.relationship('Semestre', backref='etudiants') 

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'promotion': self.promotion.nom,
            'promotion_id': self.promotion_id,

            'groupe': self.groupe.nom,
            'groupe_id': self.groupe_id,

            'site': self.site.nom,
            'site_id': self.site_id,
            'semestre': self.semestre.nom,
            'semestre_id': self.semestre_id,
            'specialite': self.specialite,
            # 'email': self.email

        
        }

    def __repr__(self):
        return f"<Etudiant {self.nom} {self.prenom}, Site: {self.site.nom}, Promo: {self.promotion.nom},Semestre: {self.semestre.nom}>"
    


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)  # Nom du test
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Date du test
    description = db.Column(db.Text, nullable=True)  # Description du test
   
    # Clé étrangère pour le site
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)  

    # Relations avec promotions et groupes
    groupes = db.relationship('Groupe', secondary=test_groupe, backref=db.backref('tests', lazy='dynamic'))
    promotions = db.relationship('Promotion', secondary=test_promotion, backref=db.backref('tests', lazy='dynamic'))
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'date': self.date.isoformat(),
            'description': self.description,
            'site_id': self.site_id,  # Juste l'ID du site au lieu de l'objet complet
            'promotions': [promotion.nom for promotion in self.promotions],
            'groupes': [groupe.nom for groupe in self.groupes]
           

        }

    def __repr__(self):
        return f"<Test {self.nom}, Date: {self.date}, Site ID: {self.site_id}>"

    
    #table score
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    h2_oral = db.Column(db.Float, nullable=False)  # H2 Oral (/100)
    note_oral = db.Column(db.Float, nullable=False)  # Note Oral (/20)
    score_oral = db.Column(db.Float, nullable=False)  # Score Oral (/100)
    h2_ecrit = db.Column(db.Float, nullable=False)  # H2 Écrit (/100)
    note_ecrit = db.Column(db.Float, nullable=False)  # Note Écrit (/20)
    score_ecrit = db.Column(db.Float, nullable=False)  # Score Écrit (/100)
    score_total_toeic = db.Column(db.Float, nullable=False)  # Score Total TOEIC
    note_cc = db.Column(db.Float, nullable=False)  # Note C.C
    note_ecue_toeic = db.Column(db.Float, nullable=False)  # Note ECUE TOEIC
    
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiant.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    
    etudiant = db.relationship('Etudiant', backref='scores')
    test = db.relationship('Test', backref='scores')
    
    def to_dict(self):
        return {
            'id': self.id,
            'note_total': self.note_total,
            'etudiant_id': self.etudiant_id,
            'test_id': self.test_id,
            'etudiant': self.etudiant.to_dict(),
            'test': self.test.to_dict()
        }

    def __repr__(self):
        return f"<Score {self.note_total} for student {self.etudiant.nom}>"

class ReponseProf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_question = db.Column(db.String(50), nullable=False)  # Numéro de la question
    choix = db.Column(db.String(2), nullable=False)  # Choix correct (ex: A, B, C, D)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    
    test = db.relationship('Test', backref='reponses_prof')
    
    def to_dict(self):
        return {
            'id': self.id,
            'num_question': self.num_question,
            'choix': self.choix,
            'test_id': self.test_id
        }

    def __repr__(self):
        return f"<ReponseProf {self.num_question} - {self.choix}>"

class ReponseEtudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_question = db.Column(db.String(50), nullable=False)
    choix = db.Column(db.String(50), nullable=False)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiant.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    
    # Suppression des 4 colonnes et de leurs relations
    etudiant = db.relationship('Etudiant', backref='reponses_etudiant')
    test = db.relationship('Test', backref='reponses_etudiant')
    
    def to_dict(self):
        return {
            'id': self.id,
            'num_question': self.num_question,
            'choix': self.choix,
            'etudiant_id': self.etudiant_id,
            'test_id': self.test_id,
            # Les informations contextuelles peuvent être obtenues via l'étudiant
            'site': self.etudiant.site.nom if self.etudiant and self.etudiant.site else None,
            'promotion': self.etudiant.promotion.nom if self.etudiant and self.etudiant.promotion else None,
            'semestre': self.etudiant.semestre.nom if self.etudiant and self.etudiant.semestre else None,
            'groupe': self.etudiant.groupe.nom if self.etudiant and self.etudiant.groupe else None
        }

# class ReponseEtudiant(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     num_question = db.Column(db.String(50), nullable=False)  # Numéro de la question
#     choix = db.Column(db.String(2), nullable=False)  # Choix de l'étudiant (ex: A, B, C, D)
#     etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiant.id'), nullable=False)
#     test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
#     site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)  # Nouvelle colonne
#     promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.id'), nullable=False)  # Nouvelle colonne
#     semestre_id = db.Column(db.Integer, db.ForeignKey('semestre.id'), nullable=False)  # Nouvelle colonne
#     groupe_id = db.Column(db.Integer, db.ForeignKey('groupe.id'), nullable=False)
    
#     etudiant = db.relationship('Etudiant', backref='reponses_etudiant')
#     test = db.relationship('Test', backref='reponses_etudiant')
#     site = db.relationship('Site', backref='reponses_etudiant')  # Nouvelle relation
#     promotion = db.relationship('Promotion', backref='reponses_etudiant')  # Nouvelle relation
#     semestre = db.relationship('Semestre', backref='reponses_etudiant')  # Nouvelle relation
#     groupe = db.relationship('Groupe', backref='reponses_etudiant')  # Nouvelle relation
    
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'num_question': self.num_question,
#             'choix': self.choix,
#             'etudiant_id': self.etudiant_id,
#             'test_id': self.test_id,
#             'site_id': self.site_id,  # Ajout du site_id
#             'site': self.site.nom,  # Ajout du nom du site
#             'promotion_id': self.promotion_id,  # Ajout du promotion_id
#             'promotion': self.promotion.nom,  # Ajout du nom de la promotion
#             'semestre_id': self.semestre_id,  # Ajout du semestre_id
#             'semestre': self.semestre.nom,  # Ajout du nom du semestre
#             'groupe_id': self.groupe_id,  # Ajout du groupe_id
#             'groupe': self.groupe.nom  # Ajout du nom du groupe
#         }

#     def __repr__(self):
#         return f"<ReponseEtudiant {self.num_question} - {self.choix}>"

#table semestre 
class Semestre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)  # Exemple : "S5", "S6", "S7", "S8"
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.id'), nullable=False)
    promotion = db.relationship('Promotion', backref='semestres')
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    site = db.relationship('Site', backref='semestres')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'promotion_id': self.promotion_id,
            'promotion': self.promotion.nom,
            'site_id': self.site_id,
            'site': self.site.nom if self.site else None  # Include site name
        }
# class Score(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     id_etudiant = db.Column(db.Integer, db.ForeignKey('etudiant.id'), nullable=False)
#     h2_oral = db.Column(db.Float, nullable=False)  # H2 Oral (/100)
#     note_oral = db.Column(db.Float, nullable=False)  # Note Oral (/20)
#     score_oral = db.Column(db.Float, nullable=False)  # Score Oral (/100)
#     h2_ecrit = db.Column(db.Float, nullable=False)  # H2 Écrit (/100)
#     note_ecrit = db.Column(db.Float, nullable=False)  # Note Écrit (/20)
#     score_ecrit = db.Column(db.Float, nullable=False)  # Score Écrit (/100)
#     score_total_toeic = db.Column(db.Float, nullable=False)  # Score Total TOEIC
#     note_cc = db.Column(db.Float, nullable=False)  # Note C.C
#     note_ecue_toeic = db.Column(db.Float, nullable=False)  # Note ECUE TOEIC
#     id_site = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
#     id_groupe = db.Column(db.Integer, db.ForeignKey('groupe.id'), nullable=False)
#     id_promotion = db.Column(db.Integer, db.ForeignKey('promotion.id'), nullable=False)
#     id_test = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)  # Si vous avez une table Test

#     etudiant = db.relationship('Etudiant', backref='scores')
#     site = db.relationship('Site', backref='scores')
#     groupe = db.relationship('Groupe', backref='scores')
#     promotion = db.relationship('Promotion', backref='scores')
#     test = db.relationship('Test', backref='scores')  # Si vous avez une table Test

#     def to_dict(self):
#         return {
#             'id': self.id,
#             'id_etudiant': self.id_etudiant,
#             'etudiant_nom': self.etudiant.nom,
#             'etudiant_prenom': self.etudiant.prenom,
#             'h2_oral': self.h2_oral,
#             'note_oral': self.note_oral,
#             'score_oral': self.score_oral,
#             'h2_ecrit': self.h2_ecrit,
#             'note_ecrit': self.note_ecrit,
#             'score_ecrit': self.score_ecrit,
#             'score_total_toeic': self.score_total_toeic,
#             'note_cc': self.note_cc,
#             'note_ecue_toeic': self.note_ecue_toeic,
#             'id_site': self.id_site,
#             'id_groupe': self.id_groupe,
#             'id_promotion': self.id_promotion,
#             'id_test': self.id_test
#         }