# promotion_routes.py

from flask import request, jsonify
from app import db
from app.Models.myModels import Promotion

def init_promotion_routes(app):
    @app.route('/api/promotions', methods=['GET'])
    def get_promotions():
        try:
            promotions = Promotion.query.all()
            if not promotions:
                return jsonify({'message': 'No promotions found'}), 404
            return jsonify([promotion.to_dict() for promotion in promotions])
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while fetching promotions'}), 500

    @app.route('/api/promotions/<int:id>', methods=['GET'])
    def get_promotion(id):
        try:
            promotion = Promotion.query.get(id)
            if not promotion:
                return jsonify({'message': 'Promotion not found'}), 404
            return jsonify(promotion.to_dict())
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while fetching the promotion'}), 500

    @app.route('/api/promotions', methods=['POST'])
    def add_promotion():
        try:
            data = request.get_json()
            new_promotion = Promotion(
                nom=data['nom'],
                site_id=data['site_id']
            )
            db.session.add(new_promotion)
            db.session.commit()
            return jsonify(new_promotion.to_dict()), 201
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while adding the promotion'}), 500

    @app.route('/api/promotions/<int:id>', methods=['PUT'])
    def update_promotion(id):
        try:
            data = request.get_json()
            promotion = Promotion.query.get(id)
            if not promotion:
                return jsonify({'message': 'Promotion not found'}), 404
            promotion.nom = data['nom']
            promotion.site_id = data['site_id']
            db.session.commit()
            return jsonify(promotion.to_dict()), 200
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while updating the promotion'}), 500

    @app.route('/api/promotions/<int:id>', methods=['DELETE'])
    def delete_promotion(id):
        try:
            promotion = Promotion.query.get(id)
            if not promotion:
                return jsonify({'message': 'Promotion not found'}), 404
            db.session.delete(promotion)
            db.session.commit()
            return jsonify({'message': 'Promotion deleted successfully'}), 200
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while deleting the promotion'}), 500
    
    @app.route('/api/promotions/by_site/<int:site_id>', methods=['GET'])
    def get_promotions_by_site(site_id):
        try:
            promotions = Promotion.query.filter_by(site_id=site_id).all()
            if not promotions:
                return jsonify({'message': 'No promotions found for this site'}), 404
            return jsonify([promotion.to_dict() for promotion in promotions])
        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'An error occurred while fetching promotions'}), 500