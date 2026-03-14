# evaluation_routes.py
from datetime import datetime
import tempfile
import os
from werkzeug.utils import secure_filename
from flask import request, jsonify, send_file
from sqlalchemy import insert

from app import db
from app.Models.myModels import (
    Etudiant, 
    Groupe, 
    ReponseEtudiant, 
    Test,
    test_groupe,
    test_promotion,
    ReponseProf
)
from app.Routes.pdf_generator import generate_toeic_pdf
from app.Routes.correction import process_pdf_for_students


def register_evaluation_routes(app):
    """Register routes for evaluation management"""
    
    @app.route('/api/evaluations', methods=['GET'])     
    def get_tests():         
        """Get all tests with their associated groups and sheet generation status"""
        # Requête pour récupérer les tests et leurs groupes associés avec le statut feuille_generee
        result = db.session.query(Test, Groupe, test_groupe.c.feuille_generee).select_from(Test) \
                .join(test_groupe, Test.id == test_groupe.c.test_id) \
                .join(Groupe, Groupe.id == test_groupe.c.groupe_id).all()
                         
        # Structure les données comme suit : [{test_id, test_title, groupe_id, groupe_name, feuille_generee}, ...]
        tests_data = []
        for test, groupe, feuille_generee in result:
            tests_data.append({
                'test_id': test.id,
                'test_title': test.nom,
                'test_description': test.description,
                'test_date': test.date,
                'groupe_id': groupe.id,
                'groupe_name': groupe.nom,
                'feuille_generee': feuille_generee  # Ajout de la valeur feuille_generee
            })
                
        return jsonify(tests_data)
    
    @app.route('/api/generateresponsesheet/<int:test_id>/<int:groupe_id>', methods=['GET'])
    def generate_response_sheet(test_id, groupe_id):
        """Generate response sheet PDF for a test and group"""
        test = Test.query.get_or_404(test_id)
        
        # Récupérer le groupe
        groupe = Groupe.query.get_or_404(groupe_id)
        
        # Récupérer tous les étudiants du groupe spécifié
        etudiants = Etudiant.query.filter_by(groupe_id=groupe_id).all()
        
        if not etudiants:
            return {"error": "Aucun étudiant trouvé dans ce groupe"}, 404
        
        # Nom du fichier avec horodatage pour éviter les conflits
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"fiche_reponse_test_{test_id}_groupe_{groupe_id}_{timestamp}.pdf"
        pdf_path = os.path.join(os.getcwd(), "temp", pdf_filename)
        
        # Créer le dossier temp s'il n'existe pas
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        # Générer le PDF
        generate_toeic_pdf(pdf_path, etudiants, test)
    
        test_groupe_entry = db.session.query(test_groupe).filter(
            test_groupe.c.test_id == test_id,
            test_groupe.c.groupe_id == groupe_id
        ).first()
            
        if test_groupe_entry:
            # Update the entry
            db.session.execute(
                test_groupe.update().where(
                    (test_groupe.c.test_id == test_id) & 
                    (test_groupe.c.groupe_id == groupe_id)
                ).values(feuille_generee=True)
            )
            db.session.commit()
        else:
            return {"error": "La relation Test-Groupe n'existe pas."}, 404

        # Envoyer le fichier au client
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"fiche_reponse_{test.nom}_{groupe.nom}.pdf",
            mimetype='application/pdf'
        )

    @app.route('/api/process-pdf', methods=['POST'])
    def process_pdf():
        """Process a submitted PDF with student responses"""
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'Aucun fichier trouvé'}), 400
        
        file = request.files['pdf_file']
        test_id = request.form.get('test_id')  # Récupérer le test_id
        groupe_id = request.form.get('groupe_id')  # Récupérer le groupe_id
        
        if not test_id or not groupe_id:
            return jsonify({'error': 'test_id et groupe_id sont requis'}), 400
            
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if file and file.filename.endswith('.pdf'):
            # Créer un fichier temporaire pour stocker le PDF
            temp_dir = tempfile.mkdtemp()
            pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(pdf_path)
            
            try:
                # Appeler la fonction pour traiter le PDF et récupérer les résultats
                results = process_pdf_for_students(pdf_path)
                
                # Récupérer tous les étudiants du groupe concerné
                etudiants = Etudiant.query.filter_by(groupe_id=groupe_id).all()
                etudiant_dict = {etudiant.id : etudiant for etudiant in etudiants}
                
                pdf_student_ids = set(map(str, results.keys()))
                group_student_ids = set(map(str, etudiant_dict.keys())) 

                missing_students = pdf_student_ids.difference(group_student_ids)
                
                if missing_students:
                    # Nettoyer
                    os.remove(pdf_path)
                    os.rmdir(temp_dir)
                    
                    # Afficher les IDs des étudiants du groupe dans la réponse JSON
                    return jsonify({
                        'error': f"Les étudiants suivants du groupe sont : {', '.join(map(str, group_student_ids))}"
                    }), 400
                
                saved_responses = []
                
                for student_id, reponses in results.items():
                    for num_question, choix in reponses.items():  
                        reponse = ReponseEtudiant(
                            choix=choix,  
                            num_question=num_question,
                            etudiant_id=student_id,
                            test_id=int(test_id)
                        )
                        db.session.add(reponse)
                        saved_responses.append(reponse.to_dict())

                # Valider les changements dans la base de données
                db.session.commit()

                # Nettoyer
                os.remove(pdf_path)
                os.rmdir(temp_dir)
                
                return jsonify({
                    'message': f'{len(saved_responses)} réponses enregistrées avec succès pour {len(pdf_student_ids)} étudiants du PDF',
                    'saved_count': len(saved_responses),
                    'student_count': len(pdf_student_ids)
                }), 200
            except Exception as e:
                # Annuler les changements en cas d'erreur
                db.session.rollback()
                
                # Nettoyer les fichiers temporaires
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
                
                return jsonify({'error': str(e)}), 500
        
        return jsonify({'error': 'Format de fichier non pris en charge'}), 400
    
    @app.route('/api/evaluations/duplicate/<int:old_test_id>', methods=['POST'])
    def duplicate_test(old_test_id):
        old_test = Test.query.get_or_404(old_test_id)
        data = request.get_json() or {}

        # Gestion sécurisée de la date
        try:
            new_date = datetime.fromisoformat(data["date"]) if data.get("date") else datetime.utcnow()
        except ValueError:
            new_date = datetime.utcnow()

        # --- SÉCURISATION CONTRE LES "NULL" ENVOYÉS PAR LE FRONTEND ---
        
        # 1. Sécuriser le nom
        nouveau_nom = data.get("nom")
        if not nouveau_nom:  # Si la clé est absente, vide ou 'null'
            nouveau_nom = old_test.nom + " (Copie)"
            
        # 2. Sécuriser la description
        nouvelle_desc = data.get("description")
        if nouvelle_desc is None:
            nouvelle_desc = old_test.description
            
        # 3. Sécuriser le site_id (C'est lui qui causait l'erreur 500 !)
        nouveau_site_id = data.get("site_id")
        if not nouveau_site_id:
            nouveau_site_id = old_test.site_id

        # On crée le nouveau test avec les valeurs 100% sûres
        new_test = Test(
            nom=nouveau_nom,
            description=nouvelle_desc,
            date=new_date,
            site_id=nouveau_site_id,
        )
        
        db.session.add(new_test)
        db.session.flush()  # Génère l'ID du nouveau test sans le verrouiller

            # 2) Associer promotions (copie de l'ancien si non fourni ou liste vide)
        promotions_ids = data.get("promotions_ids")
        # On remplace 'is None' par 'not' pour attraper les listes vides []
        if not promotions_ids: 
            promotions_ids = [p.id for p in old_test.promotions]
            
        for promo_id in promotions_ids:
            stmt = insert(test_promotion).values(test_id=new_test.id, promotion_id=promo_id)
            db.session.execute(stmt)
        
        # 3) Associer groupes (copie de l'ancien si non fourni ou liste vide)
        groupes_ids = data.get("groupes_ids")
        # Pareil ici : on intercepte les listes vides envoyées par Angular
        if not groupes_ids: 
            groupes_ids = [g.id for g in old_test.groupes]
            
        for grp_id in groupes_ids:
            stmt = insert(test_groupe).values(
                test_id=new_test.id,
                groupe_id=grp_id,
                feuille_generee=False
            )
            db.session.execute(stmt)

        # 4) Copier les réponses prof
        if data.get("copyReponsesProf", True):
            for old_rp in old_test.reponses_prof:
                new_rp = ReponseProf(
                    num_question=old_rp.num_question,
                    choix=old_rp.choix,
                    test_id=new_test.id
                )
                db.session.add(new_rp)

        # SAUVEGARDE FINALE DE TOUT D'UN COUP
        try:
            db.session.commit()
            return jsonify({
                "message": "Test dupliqué avec succès",
                "new_test_id": new_test.id,
                "new_test_nom": new_test.nom
            }), 201
        except Exception as e:
            db.session.rollback() # Annule tout en cas de problème
            return jsonify({"error": str(e)}), 500
    
    

    @app.route('/api/evaluations/<int:test_id>', methods=['DELETE'])
    def delete_evaluation(test_id):
        test = Test.query.get_or_404(test_id)
        
        ReponseProf.query.filter_by(test_id=test_id).delete()
        
        ReponseEtudiant.query.filter_by(test_id=test_id).delete()
        
        db.session.delete(test)
        db.session.commit()
        
        return jsonify({"message": "Test et ses réponses supprimés avec succès"}), 200
