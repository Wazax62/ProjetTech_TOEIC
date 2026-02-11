from app import db
from datetime import date

class TestDetails(db.Model):
    __tablename__ = 'tests'

    id_test = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    site = db.Column(db.String(50), nullable=True)
    date = db.Column(db.Date, nullable=True)
    
    reponses = db.relationship('ReponseJuste', backref='test', cascade="all, delete-orphan", lazy=True)

    def __init__(self, titre, description, site, date):
        self.titre = titre
        self.description = description
        self.site = site
        self.date = date

    def modifier_test(self, new_data):
        self.titre = new_data.get('titre', self.titre)
        self.description = new_data.get('description', self.description)
        self.site = new_data.get('site', self.site)
        self.date = new_data.get('date', self.date)

    def suppression_test(self):
        db.session.delete(self)
        db.session.commit()

    def generer_fiche_reponse(self):
        pass

    def ajouter_image_referente(self):
        pass

    def importer_fichier(self):
        pass

    def corrige_test(self):
        pass


"""
class Groupe(db.Model):
    __tablename__ = 'groupes'

    id_groupe = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    id_promotion = db.Column(db.Integer, nullable=True)  

   

    def __init__(self, nom, id_promotion=None):
        self.nom = nom
        self.id_promotion = id_promotion




class TestGroupe(db.Model):
    __tablename__ = 'tests_groupes'

    id_test = db.Column(db.Integer, db.ForeignKey('test.id_test'), nullable=False)
    id_groupe = db.Column(db.Integer, db.ForeignKey('groupes.id_groupe'), nullable=False)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    nombre_evaluation = db.Column(db.Integer, nullable=True)
    nombre_etudiant = db.Column(db.Integer, nullable=True)

    tests = db.relationship('Test', back_populates='testgroupe', cascade="all, delete-orphan")

    def __init__(self, id_groupe, titre, description, nombre_evaluation, nombre_etudiant):
        self.id_groupe = id_groupe
        self.titre = titre
        self.description = description
        self.nombre_evaluation = nombre_evaluation
        self.nombre_etudiant = nombre_etudiant

"""



class ReponseJuste(db.Model):
    __tablename__ = 'reponses_justes'

    id_reponse_juste = db.Column(db.Integer, primary_key=True)
    numero_question = db.Column(db.Integer, nullable=False)
    choix = db.Column(db.String(1), nullable=False)  
    
   
    id_test = db.Column(db.Integer, db.ForeignKey('tests.id_test'), nullable=False)

    def __init__(self, numero_question, choix, id_test):
        self.numero_question = numero_question
        self.choix = choix
        self.id_test = id_test


 
