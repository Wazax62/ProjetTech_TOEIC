# groupe_routes.py

from flask import request, jsonify
from app import db
from app.Models.myModels import Groupe, Promotion, Site, Semestre

def init_groupe_routes(app):
    @app.route('/api/groupes', methods=['GET'])
    def get_groupes():
        try:
            groupes = Groupe.query.all()
            if not groupes:
                return jsonify({'message': 'No groupes found'}), 404
            return jsonify([groupe.to_dict() for groupe in groupes])
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while fetching groupes'}), 500

    @app.route('/api/groupes', methods=['POST'])
    def add_groupe():
        try:
            data = request.get_json()
            print('Voici le groupe à ajouter :', data)

            # Chercher la promotion, le site et le semestre par ID (et non par nom)
            promotion = Promotion.query.filter_by(id=int(data['promotion_id'])).first()
            site = Site.query.filter_by(id=int(data['site_id'])).first()
            semestre = Semestre.query.filter_by(id=int(data['semestre_id'])).first()

            # Vérifier que la promotion, le site et le semestre existent
            if not promotion:
                return jsonify({'message': 'Promotion not found'}), 404
            if not site:
                return jsonify({'message': 'Site not found'}), 404
            if not semestre:
                return jsonify({'message': 'Semestre not found'}), 404

            # Créer un nouveau groupe avec le semestre_id
            new_groupe = Groupe(
                nom=data['nom'],
                promotion_id=promotion.id,
                site_id=site.id,
                semestre_id=semestre.id  # Ajout du semestre_id
            )

            # Ajouter et valider le nouveau groupe
            db.session.add(new_groupe)
            db.session.commit()

            print('Groupe ajouté avec succès :', new_groupe.to_dict())
            return jsonify(new_groupe.to_dict()), 201
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while adding the groupe'}), 500

    @app.route('/api/groupes/<int:id>', methods=['DELETE'])
    def delete_groupe(id):
        try:
            groupe = Groupe.query.get(id)
            if not groupe:
                return jsonify({'message': 'Groupe not found'}), 404
            db.session.delete(groupe)
            db.session.commit()
            return jsonify({'message': 'Groupe deleted successfully'}), 200
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while deleting the groupe'}), 500
            
    @app.route('/api/groupes/<int:id>', methods=['GET'])
    def get_groupe(id):
        try:
           groupe = Groupe.query.get(id)
           if not groupe:
               return jsonify({'message': 'Groupe not found'}), 404
           return jsonify(groupe.to_dict())
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while fetching the groupe'}), 500
            
    @app.route('/api/groupes/<int:id>', methods=['PUT'])
    def update_groupe(id):
        try:
            data = request.get_json()
            print('here the data of groupe to update',data)
            groupe = Groupe.query.get(id)
            if not groupe:
                return jsonify({'message': 'Groupe not found'}), 404
        
            groupe.nom = data.get('nom', groupe.nom)
            groupe.promotion_id = data.get('promotion_id', groupe.promotion_id)
            groupe.site_id = data.get('site_id', groupe.site_id)
            groupe.semestre_id = data.get('semestre_id', groupe.semestre_id)
        
            db.session.commit()
        
            return jsonify(groupe.to_dict()), 200
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while updating the groupe'}), 500
            
    @app.route('/api/groupes/by_site_promotion_semestre', methods=['GET'])
    def get_groupes_by_site_promotion_semestre():
        try:
            # Récupérer les paramètres de la requête
            site_id = request.args.get('site_id')
            promotion_id = request.args.get('promotion_id')
            semestre_id = request.args.get('semestre_id')

            # Vérifier que les paramètres sont présents
            if not site_id or not promotion_id or not semestre_id:
                return jsonify({'error': 'Les paramètres site_id, promotion_id et semestre_id sont requis'}), 400

            # Convertir les paramètres en entiers
            site_id = int(site_id)
            promotion_id = int(promotion_id)
            semestre_id = int(semestre_id)

            # Filtrer les groupes par site, promotion et semestre
            groupes = Groupe.query.filter_by(
                site_id=site_id,
                promotion_id=promotion_id,
                semestre_id=semestre_id
            ).all()

            # Si aucun groupe n'est trouvé
            if not groupes:
                return jsonify({'message': 'Aucun groupe trouvé pour ce site, promotion et semestre'}), 404

            # Retourner les groupes au format JSON
            return jsonify([groupe.to_dict() for groupe in groupes])
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'Une erreur est survenue lors de la récupération des groupes'}), 500

    @app.route('/api/groupes/by_promotion_and_site/<int:promotion_id>/<int:site_id>', methods=['GET'])
    def get_groupes_by_promotion_and_site(promotion_id, site_id):
        try:
            groupes = Groupe.query.filter_by(promotion_id=promotion_id, site_id=site_id).all()
            if not groupes:
                return jsonify({'message': 'No groupes found for this promotion and site'}), 404
            return jsonify([groupe.to_dict() for groupe in groupes])
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while fetching groupes'}), 500