# # site_routes.py

# from flask import jsonify
# from app.Models.myModels import Site

# def init_site_routes(app):
#     @app.route('/api/sites', methods=['GET'])
#     def get_sites():
#         app.logger.info("Route /api/sites a été atteinte.")
#         try:
#             # Récupérer tous les sites depuis la base de données
#             sites = Site.query.all()

#             # Si aucun site n'est trouvé
#             if not sites:
#                 app.logger.info("Aucun site trouvé.")
#                 return jsonify({'message': 'No sites found'}), 404

#             # Convertir les sites en dictionnaires et les retourner en JSON
#             return jsonify([site.to_dict() for site in sites])
#         except Exception as e:
#             app.logger.error(f"Erreur : {e}")
#             return jsonify({'error': 'An error occurred while fetching sites'}), 500
# site_routes.py

from flask import jsonify, request
from app.Models.myModels import Site
from app import db  # Importez db depuis votre application

def init_site_routes(app):
    @app.route('/api/sites', methods=['GET'])
    def get_sites():
        app.logger.info("Route /api/sites a été atteinte.")
        try:
            # Récupérer tous les sites depuis la base de données
            sites = Site.query.all()

            # Si aucun site n'est trouvé
            if not sites:
                app.logger.info("Aucun site trouvé.")
                return jsonify({'message': 'No sites found'}), 404

            # Convertir les sites en dictionnaires et les retourner en JSON
            return jsonify([site.to_dict() for site in sites])
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while fetching sites'}), 500

    @app.route('/api/sites', methods=['POST'])
    def create_site():
        app.logger.info("Route POST /api/sites a été atteinte.")
        try:
            # Récupérer les données du corps de la requête
            data = request.get_json()
            
            # Validation des données
            if not data or 'nom' not in data:
                app.logger.error("Données manquantes ou incorrectes")
                return jsonify({'error': 'Le nom du site est requis'}), 400
                
            if not isinstance(data['nom'], str) or len(data['nom']) > 50:
                app.logger.error("Nom de site invalide")
                return jsonify({'error': 'Le nom doit être une chaîne de caractères (max 50 caractères)'}), 400
            
            # Vérifier si le site existe déjà
            existing_site = Site.query.filter_by(nom=data['nom']).first()
            if existing_site:
                app.logger.error("Site déjà existant")
                return jsonify({'error': 'Ce site existe déjà'}), 409
            
            # Créer un nouveau site
            new_site = Site(nom=data['nom'])
            
            # Ajouter à la base de données
            db.session.add(new_site)
            db.session.commit()
            
            app.logger.info(f"Site créé avec succès: {new_site.nom}")
            return jsonify(new_site.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la création du site: {e}")
            return jsonify({'error': 'Une erreur est survenue lors de la création du site'}), 500
        
    @app.route('/api/sites/<int:site_id>', methods=['DELETE'])
    def delete_site(site_id):
        app.logger.info(f"Route DELETE /api/sites/{site_id} a été atteinte.")
        try:
            # Récupérer le site à supprimer
            site = Site.query.get(site_id)
            
            # Vérifier si le site existe
            if not site:
                app.logger.error(f"Site avec ID {site_id} non trouvé")
                return jsonify({'error': 'Site non trouvé'}), 404
            
            # Supprimer le site de la base de données
            db.session.delete(site)
            db.session.commit()
            
            app.logger.info(f"Site {site_id} supprimé avec succès")
            return jsonify({'message': 'Site supprimé avec succès'}), 200
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la suppression du site: {e}")
            return jsonify({'error': 'Une erreur est survenue lors de la suppression du site'}), 500