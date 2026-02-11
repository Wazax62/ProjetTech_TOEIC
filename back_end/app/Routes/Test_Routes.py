# test_routes.py
from datetime import datetime
from flask import request, jsonify
from flask_cors import cross_origin

from app import db
from app.Models.myModels import (
    Etudiant, 
    Groupe, 
    Promotion, 
    ReponseProf, 
    Site, 
    Test,
    test_groupe, 
    test_promotion
)


def register_test_routes(app):
    """Register all routes related to test creation and management"""
    
    @app.route('/api/tests', methods=['POST', 'OPTIONS'])
    @cross_origin(origin='http://localhost:4200', headers=['Content-Type'])
    def ajouter_test():
        """Create a new test with its responses, groups and promotions"""
        if request.method == "OPTIONS":
            response = jsonify({'message': 'CORS preflight request successful'})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            return response, 200  

        try:
            data = request.json
            if not data:
                return jsonify({'error': 'Aucune donnée reçue'}), 400

            test_data = data.get('test_data', {})
            test_responses = data.get('test_responses', [])
            selected_groups = data.get('selected_groups', [])  # Liste des IDs des groupes
            site_id = test_data.get('site')

            # Vérification des champs obligatoires
            if not test_data.get('nom'):
                return jsonify({'error': 'Le nom du test est requis'}), 400
            if not test_data.get('date'):
                return jsonify({'error': 'La date du test est requise'}), 400
            if not selected_groups:
                return jsonify({'error': 'Au moins un groupe doit être sélectionné'}), 400
            if not test_responses:
                return jsonify({'error': 'Les réponses du test sont requises'}), 400
            if not site_id:
                return jsonify({'error': 'Le site est requis'}), 400

            # Création du test
            test = Test(
                nom=test_data['nom'],
                description=test_data.get('description', ''),  
                date=datetime.strptime(test_data['date'], '%Y-%m-%d'),
                site_id=site_id,
            )

            db.session.add(test)
            
            added_promotions = set()  # Pour éviter les doublons
            for groupe_id in selected_groups:
                groupe = Groupe.query.get(groupe_id)
                if groupe:
                    # Utiliser UNIQUEMENT cette méthode (pas d'insert explicite)
                    test.groupes.append(groupe)

                    # Ajouter la promotion si pas déjà ajoutée
                    if groupe.promotion_id and groupe.promotion_id not in added_promotions:
                        promotion = Promotion.query.get(groupe.promotion_id)
                        if promotion:
                            test.promotions.append(promotion)
                            added_promotions.add(promotion.id)

                   

            # Important: faire un flush avant d'ajouter les réponses
            db.session.flush()

            # Ajout des réponses
            for response in test_responses:
                if 'num_question' in response and 'choix' in response:
                    reponse_prof = ReponseProf(
                        num_question=response['num_question'],
                        choix=response['choix'],
                        test_id=test.id
                    )
                    db.session.add(reponse_prof)
                else:
                    return jsonify({'error': 'Données de réponse incomplètes'}), 400

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Test créé avec succès',
                'test_id': test.id
            })

        except Exception as e:
            db.session.rollback()
            print(f"Erreur backend: {e}")  
            return jsonify({'error': str(e)}), 500

    @app.route('/api/sitesachraf', methods=['GET'])
    def trouver_sites_tests():
        """Get all sites from database"""
        sites = Site.query.all()
        result = [{"id": site.id, "nom": site.nom} for site in sites]
        return jsonify(result)
   
    @app.route('/api/groupesachraf', methods=['GET'])
    def get_groupes_tests():
        """Get groups by site_id"""
        site_id = request.args.get('site_id', type=int)

        # Debugging
        if site_id is None:
            print("⚠️ Avertissement : site_id est None ! Vérifiez la requête GET.")
            return jsonify({"error": "Le paramètre site_id est requis."}), 400

        print(f"🔍 Site ID reçu: {site_id}")

        # Vérifier si le site existe dans la base de données
        site = Site.query.get(site_id)
        if not site:
            print("❌ Aucun site trouvé avec cet ID")
            return jsonify([])  # Retourner une liste vide si le site n'existe pas

        # Récupérer uniquement les groupes du site sélectionné
        groupes = Groupe.query.filter_by(site_id=site_id).all()
        print(f"📌 Groupes trouvés ({len(groupes)}): {groupes}")

        result = []
        for groupe in groupes:
            nombre_etudiants = db.session.query(Etudiant).filter(Etudiant.groupe_id == groupe.id).count()
            nombre_tests = db.session.query(Test).join(test_groupe).filter(test_groupe.c.groupe_id == groupe.id).count()

            result.append({
                'id_groupe': groupe.id,
                'nom': groupe.nom,
                'promotion': groupe.promotion.nom if groupe.promotion else None,
                'site': groupe.site.nom if groupe.site else None,
                'semestre': groupe.semestre.nom if groupe.semestre else None,
                'nombre_tests': nombre_tests,
                'nombre_etudiants': nombre_etudiants
            })

        print("✅ API Response:", result)
        return jsonify(result)