# semestre_routes.py

from flask import request, jsonify
from app.Models.myModels import Semestre
from app import db



def init_semestre_routes(app):
    @app.route('/api/semestres/by_promotion', methods=['GET'])
    def get_semestres_by_site_and_promotion():
        try:
            # Récupérer les paramètres de la requête
            promotion_id = request.args.get('promotion_id')

            # Vérifier que les paramètres sont présents
            if not promotion_id:
                return jsonify({'error': 'Les paramètres promotion_id est requis'}), 400

            # Convertir les paramètres en entiers
            promotion_id = int(promotion_id)

            # Filtrer les semestres par site et promotion
            semestres = Semestre.query.filter_by(promotion_id=promotion_id).all()

            # Vérifier si des semestres ont été trouvés
            if not semestres:
                return jsonify({'message': 'Aucun semestre trouvé pour ce site et cette promotion'}), 404

            # Retourner les semestres au format JSON
            return jsonify([semestre.to_dict() for semestre in semestres])
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'Une erreur est survenue lors de la récupération des semestres'}), 500
        #####################################

    @app.route('/api/semestres', methods=['GET'])
    def get_semestres():
        try:
            semestres = Semestre.query.all()
            if not semestres:
                return jsonify({'message': 'No promotions found'}), 404
            return jsonify([semestre.to_dict() for semestre in semestres])
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while fetching promotions'}), 500

    @app.route('/api/semestres/<int:id>', methods=['GET'])
    def get_semestre(id):
        try:
            semestre = Semestre.query.get(id)
            if not semestre:
                return jsonify({'message': 'Promotion not found'}), 404
            return jsonify(semestre.to_dict())
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while fetching the promotion'}), 500

     # Route pour ajouter un semestre
    @app.route('/api/semestres', methods=['POST'])
    def add_semestre():
        try:
            data = request.get_json()
            
            # Validation des données
            if not data.get('nom'):
                return jsonify({'error': 'Le nom du semestre est requis'}), 400
            if not data.get('promotion_id'):
                return jsonify({'error': 'L\'ID de promotion est requis'}), 400
            if not data.get('site_id'):
                return jsonify({'error': 'L\'ID de site est requis'}), 400

            new_semestre = Semestre(
                nom=data['nom'],
                promotion_id=data['promotion_id'],
                site_id=data['site_id']
            )
            
            db.session.add(new_semestre)
            db.session.commit()
            
            return jsonify(new_semestre.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': str(e)}), 500

     # Route pour modifier un semestre
    @app.route('/api/semestres/<int:id>', methods=['PUT'])
    def update_semestre(id):
        try:
            data = request.get_json()
            semestre = Semestre.query.get(id)
            
            if not semestre:
                return jsonify({'message': 'Semestre non trouvé'}), 404

            if 'nom' in data:
                semestre.nom = data['nom']
            if 'promotion_id' in data:
                semestre.promotion_id = data['promotion_id']
            if 'site_id' in data:
                semestre.site_id = data['site_id']
            
            db.session.commit()
            return jsonify(semestre.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': str(e)}), 500

    # Route pour supprimer un semestre
    @app.route('/api/semestres/<int:id>', methods=['DELETE'])
    def delete_semestre(id):
        try:
            semestre = Semestre.query.get(id)
            if not semestre:
                return jsonify({'message': 'Semestre non trouvé'}), 404
                
            db.session.delete(semestre)
            db.session.commit()
            return jsonify({'message': 'Semestre supprimé avec succès'}), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': str(e)}), 500
