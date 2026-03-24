import os
import os
from reportlab.lib.units import inch

# OUI : L'image doit venir d'ici
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image

# NON : Ne mettez pas "Image" dans cette ligne !
from reportlab.graphics.shapes import Drawing, String, Polygon
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from flask import request, jsonify, make_response
from app import db
from app.Models.myModels import Etudiant, Groupe, Promotion, Semestre, Site,test_groupe, Test,ReponseEtudiant,ReponseProf,Score
from flask import make_response
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from reportlab.lib.styles import ParagraphStyle
import locale
from datetime import datetime
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as PlatypusImage
from reportlab.graphics.shapes import Drawing, String



def get_radar_chart(percentages, labels):
    # Conteneur beaucoup plus compact (180x130)
    d = Drawing(150,100)
    
    ss = SpiderChart()
    ss.width = 90
    ss.height = 90
    ss.x = 45       
    ss.y = 20        
    
    N = len(percentages)
    ss.data = [percentages, [100]*N, [80]*N, [60]*N, [40]*N, [20]*N]
    ss.labels = labels
    
    # Styles
    ss.strands[0].fillColor = colors.lightblue
    ss.strands[0].strokeColor = colors.blue
    ss.strands[0].strokeWidth = 1.5
    for i in range(1, 6):
        ss.strands[i].fillColor = None  
        ss.strands[i].strokeColor = colors.darkred
        ss.strands[i].strokeWidth = 0.5
    
    d.add(ss)
    
    # Textes de l'échelle (police taille 5)
    center_x = ss.x + (ss.width / 2)
    center_y = ss.y + (ss.height / 2)
    radius = ss.height / 2
    for val in [20, 40, 60, 80, 100]:
        dist = (val / 100.0) * radius
        label_y = center_y + dist
        d.add(String(center_x + 3, label_y - 2, f"{val}%", fontSize=5, fillColor=colors.black))
    
    return d



def init_score_routes(app):
    @app.route('/api/tests/by_site_promotion_group_semester/<int:site_id>/<int:promotion_id>/<int:groupe_id>/<int:semestre_id>', methods=['GET'])
    def get_tests_by_site_promotion_group_semester(site_id, promotion_id, groupe_id, semestre_id):
        try:
            # Vérifier d'abord que le groupe existe et appartient à la promotion, site et semestre
            groupe = Groupe.query.filter_by(
                id=groupe_id,
                promotion_id=promotion_id,
                site_id=site_id,
                semestre_id=semestre_id
            ).first()
            
            if not groupe:
                return jsonify({'message': 'Groupe non trouvé pour cette combinaison site/promotion/semestre'}), 404

            # Récupérer les tests associés à ce groupe
            tests = Test.query \
                .join(test_groupe, Test.id == test_groupe.c.test_id) \
                .filter(test_groupe.c.groupe_id == groupe_id) \
                .all()

            if not tests:
                return jsonify({'message': 'Aucun test trouvé pour ce groupe'}), 404

            return jsonify([test.to_dict() for test in tests])

        except Exception as e:
            app.logger.error(f"Erreur : {e}")
            return jsonify({'error': 'Une erreur est survenue lors de la récupération des tests'}), 500
        

 
    ###################################SCORE(AVEC GESTION DES ABSENTS)
    @app.route('/api/scores/calculate', methods=['GET'])
    def calculate_scores():
        try:
            # Récupérer les paramètres de la requête
            site_id = request.args.get('site_id')
            promotion_id = request.args.get('promotion_id')
            groupe_id = request.args.get('groupe_id')
            semestre_id = request.args.get('semestre_id')
            test_id = request.args.get('test_id')

            # Vérifier que tous les paramètres sont présents
            if not all([site_id, promotion_id, groupe_id, semestre_id, test_id]):
                return jsonify({'error': 'Tous les paramètres sont requis'}), 400

            # Convertir les paramètres en entiers
            site_id = int(site_id)
            promotion_id = int(promotion_id)
            groupe_id = int(groupe_id)
            semestre_id = int(semestre_id)
            test_id = int(test_id)

            # Récupérer le semestre pour connaître la valeur M
            semestre = Semestre.query.get(semestre_id)
            if not semestre:
                return jsonify({'error': 'Semestre non trouvé'}), 404

            # Déterminer la valeur M en fonction du semestre
            semestre_nom = semestre.nom.upper()
            if 'S5' in semestre_nom:
                M = 535
            elif 'S6' in semestre_nom:
                M = 585
            elif 'S7' in semestre_nom:
                M = 635
            elif 'S8' in semestre_nom:
                M = 685
            else:
                M = 535  # Valeur par défaut

            # Récupérer tous les étudiants de la promo/site/groupe/semestre
            tous_etudiants = Etudiant.query.filter(
                Etudiant.site_id == site_id,
                Etudiant.promotion_id == promotion_id,
                Etudiant.groupe_id == groupe_id,
                Etudiant.semestre_id == semestre_id
            ).all()

            if not tous_etudiants:
                return jsonify({'message': 'Aucun étudiant trouvé pour ces critères'}), 404

            # Récupérer les étudiants qui ont répondu au test sélectionné
            etudiants_avec_reponses = db.session.query(Etudiant)\
                .join(ReponseEtudiant, (Etudiant.id == ReponseEtudiant.etudiant_id) & 
                                (ReponseEtudiant.test_id == test_id))\
                .filter(
                    Etudiant.site_id == site_id,
                    Etudiant.promotion_id == promotion_id,
                    Etudiant.groupe_id == groupe_id,
                    Etudiant.semestre_id == semestre_id
                )\
                .distinct()\
                .all()

            # Récupérer les réponses correctes du professeur pour ce test
            reponses_prof = {
                int(r.num_question): r.choix 
                for r in ReponseProf.query.filter_by(test_id=test_id).all()
            }

            results = []

            # Traiter d'abord les étudiants avec réponses
            for etudiant in etudiants_avec_reponses:
                # Vérifier si un score existe déjà pour cet étudiant et ce test
                existing_score = Score.query.filter_by(
                    etudiant_id=etudiant.id,
                    test_id=test_id
                ).first()

                # Récupérer toutes les réponses de l'étudiant pour ce test
                reponses_etudiant = ReponseEtudiant.query.filter_by(
                    etudiant_id=etudiant.id,
                    test_id=test_id
                ).all()

                # Convertir en format {num_question: choix}
                reponses_etudiant_dict = {int(r.num_question): r.choix for r in reponses_etudiant}

                # Calculer H2 Oral (questions 1-100)
                h2_oral = 0
                for q in range(1, 101):
                    if q in reponses_etudiant_dict and q in reponses_prof:
                        if reponses_etudiant_dict[q] == reponses_prof[q]:
                            h2_oral += 1

                # Calculer Note Oral
                note_oral = (h2_oral * 20) / 100

                # Calculer Score Oral
                if h2_oral < 6:
                    score_oral = 5
                elif h2_oral < 26:
                    score_oral = (h2_oral - 5) * 5
                elif h2_oral < 35:
                    score_oral = (h2_oral - 4) * 5
                elif h2_oral < 44:
                    score_oral = (h2_oral - 3) * 5
                elif h2_oral < 47:
                    score_oral = (h2_oral - 2) * 5
                elif h2_oral < 48:
                    score_oral = (h2_oral - 1) * 5
                elif h2_oral < 53:
                    score_oral = h2_oral * 5
                elif h2_oral < 56:
                    score_oral = (h2_oral + 1) * 5
                elif h2_oral < 59:
                    score_oral = (h2_oral + 2) * 5
                elif h2_oral < 64:
                    score_oral = (h2_oral + 3) * 5
                elif h2_oral < 67:
                    score_oral = (h2_oral + 4) * 5
                elif h2_oral < 70:
                    score_oral = (h2_oral + 5) * 5
                elif h2_oral < 77:
                    score_oral = (h2_oral + 6) * 5
                elif h2_oral < 80:
                    score_oral = (h2_oral + 7) * 5
                elif h2_oral < 83:
                    score_oral = (h2_oral + 8) * 5
                elif h2_oral < 90:
                    score_oral = (h2_oral + 9) * 5
                else:
                    score_oral = 495

                # Calculer H2 Ecrit (questions 101-200)
                h2_ecrit = 0
                for q in range(101, 201):
                    if q in reponses_etudiant_dict and q in reponses_prof:
                        if reponses_etudiant_dict[q] == reponses_prof[q]:
                            h2_ecrit += 1

                # Calculer Note Ecrit
                note_ecrit = (h2_ecrit * 20) / 100

                # Calculer Score Ecrit
                if h2_ecrit < 16:
                    score_ecrit = 5
                elif h2_ecrit < 25:
                    score_ecrit = (h2_ecrit - 14) * 5
                elif h2_ecrit < 28:
                    score_ecrit = (h2_ecrit - 13) * 5
                elif h2_ecrit < 33:
                    score_ecrit = (h2_ecrit - 12) * 5
                elif h2_ecrit < 38:
                    score_ecrit = (h2_ecrit - 11) * 5
                elif h2_ecrit < 41:
                    score_ecrit = (h2_ecrit - 10) * 5
                elif h2_ecrit < 46:
                    score_ecrit = (h2_ecrit - 9) * 5
                elif h2_ecrit < 49:
                    score_ecrit = (h2_ecrit - 8) * 5
                elif h2_ecrit < 56:
                    score_ecrit = (h2_ecrit - 7) * 5
                elif h2_ecrit < 61:
                    score_ecrit = (h2_ecrit - 6) * 5
                elif h2_ecrit < 64:
                    score_ecrit = (h2_ecrit - 5) * 5
                elif h2_ecrit < 67:
                    score_ecrit = (h2_ecrit - 4) * 5
                elif h2_ecrit < 72:
                    score_ecrit = (h2_ecrit - 3) * 5
                elif h2_ecrit < 77:
                    score_ecrit = (h2_ecrit - 2) * 5
                elif h2_ecrit < 89:
                    score_ecrit = (h2_ecrit - 1) * 5
                elif h2_ecrit < 92:
                    score_ecrit = h2_ecrit * 5
                elif h2_ecrit < 94:
                    score_ecrit = (h2_ecrit + 1) * 5
                elif h2_ecrit < 98:
                    score_ecrit = (h2_ecrit + 2) * 5
                else:
                    score_ecrit = 495

                # Calculer Score Total TOEIC
                score_total_toeic = score_oral + score_ecrit

                # Calculer Note C.C
                note_cc = score_total_toeic / 49.5

                # Calculer Note ECUE TOEIC
                note_ecue_toeic = max(10 * (1 + (score_total_toeic - M) / (990 - M)), 0)

                # Créer ou mettre à jour le score dans la base de données
                if existing_score:
                    # Mettre à jour le score existant
                    existing_score.h2_oral = h2_oral
                    existing_score.note_oral = round(note_oral, 2)
                    existing_score.score_oral = score_oral
                    existing_score.h2_ecrit = h2_ecrit
                    existing_score.note_ecrit = round(note_ecrit, 2)
                    existing_score.score_ecrit = score_ecrit
                    existing_score.score_total_toeic = score_total_toeic
                    existing_score.note_cc = round(note_cc, 2)
                    existing_score.note_ecue_toeic = round(note_ecue_toeic, 2)
                else:
                    # Créer un nouveau score
                    new_score = Score(
                        h2_oral=h2_oral,
                        note_oral=round(note_oral, 2),
                        score_oral=score_oral,
                        h2_ecrit=h2_ecrit,
                        note_ecrit=round(note_ecrit, 2),
                        score_ecrit=score_ecrit,
                        score_total_toeic=score_total_toeic,
                        note_cc=round(note_cc, 2),
                        note_ecue_toeic=round(note_ecue_toeic, 2),
                        etudiant_id=etudiant.id,
                        test_id=test_id
                    )
                    db.session.add(new_score)

                # Ajouter le résultat pour la réponse JSON
                results.append({
                    'etudiant_id': etudiant.id,
                    'nom': etudiant.nom,
                    'prenom': etudiant.prenom,
                    'h2_oral': h2_oral,
                    'note_oral': round(note_oral, 2),
                    'score_oral': score_oral,
                    'h2_ecrit': h2_ecrit,
                    'note_ecrit': round(note_ecrit, 2),
                    'score_ecrit': score_ecrit,
                    'score_total_toeic': score_total_toeic,
                    'note_cc': round(note_cc, 2),
                    'note_ecue_toeic': round(note_ecue_toeic, 2)
                })

            # Maintenant traiter les étudiants absents (sans réponses)
            etudiants_absents = [etudiant for etudiant in tous_etudiants if etudiant not in etudiants_avec_reponses]
            
            for etudiant in etudiants_absents:
                # Vérifier si un score existe déjà pour cet étudiant et ce test
                existing_score = Score.query.filter_by(
                    etudiant_id=etudiant.id,
                    test_id=test_id
                ).first()

                # Tous les scores à 0 pour les absents
                h2_oral = 0
                note_oral = 0.0
                score_oral = 0
                h2_ecrit = 0
                note_ecrit = 0.0
                score_ecrit = 0
                score_total_toeic = 0
                note_cc = 0.0
                note_ecue_toeic = 0.0

                # Créer ou mettre à jour le score dans la base de données
                if existing_score:
                    # Mettre à jour le score existant
                    existing_score.h2_oral = h2_oral
                    existing_score.note_oral = note_oral
                    existing_score.score_oral = score_oral
                    existing_score.h2_ecrit = h2_ecrit
                    existing_score.note_ecrit = note_ecrit
                    existing_score.score_ecrit = score_ecrit
                    existing_score.score_total_toeic = score_total_toeic
                    existing_score.note_cc = note_cc
                    existing_score.note_ecue_toeic = note_ecue_toeic
                else:
                    # Créer un nouveau score
                    new_score = Score(
                        h2_oral=h2_oral,
                        note_oral=note_oral,
                        score_oral=score_oral,
                        h2_ecrit=h2_ecrit,
                        note_ecrit=note_ecrit,
                        score_ecrit=score_ecrit,
                        score_total_toeic=score_total_toeic,
                        note_cc=note_cc,
                        note_ecue_toeic=note_ecue_toeic,
                        etudiant_id=etudiant.id,
                        test_id=test_id
                    )
                    db.session.add(new_score)

                # Ajouter le résultat pour la réponse JSON
                results.append({
                    'etudiant_id': etudiant.id,
                    'nom': etudiant.nom,
                    'prenom': etudiant.prenom,
                    'h2_oral': h2_oral,
                    'note_oral': note_oral,
                    'score_oral': score_oral,
                    'h2_ecrit': h2_ecrit,
                    'note_ecrit': note_ecrit,
                    'score_ecrit': score_ecrit,
                    'score_total_toeic': score_total_toeic,
                    'note_cc': note_cc,
                    'note_ecue_toeic': note_ecue_toeic
                })

            # Valider les changements dans la base de données
            db.session.commit()

            return jsonify(results)

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors du calcul et sauvegarde des scores: {str(e)}")
            return jsonify({'error': str(e)}), 500
        


        #ici le code generate_oral_pdf AVEC gerer les absents
   ##########################################################################################
    @app.route('/api/generate-oral-pdf', methods=['GET'])
    def generate_oral_pdf():
        try:
            # Récupérer les paramètres de la requête
            site_id = request.args.get('site_id')
            promotion_id = request.args.get('promotion_id')
            groupe_id = request.args.get('groupe_id')
            semestre_id = request.args.get('semestre_id')
            test_id = request.args.get('test_id')

            # Vérifier que tous les paramètres sont présents
            if not all([site_id, promotion_id, groupe_id, semestre_id, test_id]):
                return jsonify({'error': 'Tous les paramètres sont requis'}), 400

            # Convertir les paramètres en entiers
            site_id = int(site_id)
            promotion_id = int(promotion_id)
            groupe_id = int(groupe_id)
            semestre_id = int(semestre_id)
            test_id = int(test_id)

            # Récupérer tous les étudiants du groupe
            tous_etudiants = Etudiant.query.filter(
                Etudiant.site_id == site_id,
                Etudiant.promotion_id == promotion_id,
                Etudiant.groupe_id == groupe_id,
                Etudiant.semestre_id == semestre_id
            ).all()

            if not tous_etudiants:
                return jsonify({'message': 'Aucun étudiant trouvé pour ces critères'}), 404

            # Récupérer les étudiants qui ont répondu au test
            etudiants_avec_reponses = db.session.query(Etudiant)\
                .join(ReponseEtudiant, Etudiant.id == ReponseEtudiant.etudiant_id)\
                .filter(
                    ReponseEtudiant.test_id == test_id,
                    Etudiant.site_id == site_id,
                    Etudiant.promotion_id == promotion_id,
                    Etudiant.groupe_id == groupe_id,
                    Etudiant.semestre_id == semestre_id
                )\
                .distinct()\
                .all()

            # Séparer les étudiants présents et absents
            etudiants_absents = [etudiant for etudiant in tous_etudiants if etudiant not in etudiants_avec_reponses]
            etudiants_presents = etudiants_avec_reponses

            # Récupérer les scores pour tous les étudiants (même les absents)
            scores = {score.etudiant_id: score for score in Score.query.filter_by(test_id=test_id).all()}

            # Récupérer les réponses correctes du professeur
            reponses_prof = {
                int(r.num_question): r.choix 
                for r in ReponseProf.query.filter_by(test_id=test_id).all()
            }

            # Créer le PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []

            # Styles
            styles = getSampleStyleSheet()
            style_title = styles['Title']
            style_heading = styles['Heading2']
            style_normal = styles['Normal']
            style_absent = ParagraphStyle(
                'Absent',
                parent=style_normal,
                textColor=colors.red,
                fontSize=12
            )

            # Titre du document
            elements.append(Paragraph("Rapport des Scores Oral - TOEIC", style_title))
            elements.append(Spacer(1, 0.5 * inch))
            #nom du groupe
            groupe = Groupe.query.get(groupe_id) 
            if groupe:
                elements.append(Paragraph(f"Groupe : {groupe.nom}", style_heading))
               # elements.append(Spacer(1, 0.3 * inch))
            # date du test    
            test = Test.query.get(test_id)
            try:
                date_formatee = test.date.strftime("le %d/%m/%Y à %H:%M")
            except locale.Error:
                locale.setlocale(locale.LC_TIME, '')  
            if test and test.date:
                # Mettre la première lettre du mois en majuscule
                date_formatee = date_formatee.replace(
                    test.date.strftime("%B"), 
                    test.date.strftime("%B").capitalize()
                )
                elements.append(Paragraph(date_formatee, style_heading))

            elements.append(Spacer(1, 0.3 * inch))
            base_dir = os.path.dirname(__file__)
            logo_path = os.path.join(base_dir, "..", "..", "..", "src", "assets", "images", "eilco_logo.png")
            logo_path = os.path.normpath(logo_path)

            if os.path.exists(logo_path):

                logo = Image(logo_path, width=6*inch, height=2.4*inch)
                logo.hAlign = 'CENTER'
                    
                elements.append(logo)
                elements.append(Spacer(1, 0.2 * inch))
            else:
                print(f"⚠️ Logo introuvable : {logo_path}")
            
            elements.append(PageBreak())


 

            # Traiter d'abord les étudiants présents
            for etudiant in etudiants_presents:
                score = scores.get(etudiant.id)
                
                # Ajouter l'entête de l'étudiant
                elements.append(Paragraph(f"Étudiant: {etudiant.nom} {etudiant.prenom}", style_normal))
                elements.append(Spacer(1, 0.1 * inch))

                if score:
                    # Récupérer les réponses de l'étudiant
                    reponses_etudiant = ReponseEtudiant.query.filter_by(
                        etudiant_id=etudiant.id,
                        test_id=test_id
                    ).all()
                    reponses_etudiant_dict = {int(r.num_question): r.choix for r in reponses_etudiant}

                    # Calculer les scores par partie
                    parties = [
                        {'nom': 'Partie 1 (Q1-6)', 'debut': 1, 'fin': 6},
                        {'nom': 'Partie 2 (Q7-31)', 'debut': 7, 'fin': 31},
                        {'nom': 'Partie 3 (Q32-70)', 'debut': 32, 'fin': 70},
                        {'nom': 'Partie 4 (Q71-100)', 'debut': 71, 'fin': 100}
                    ]

                    # ... (votre code juste au-dessus)
                    data = [['Partie', 'Questions Correctes', 'Total Questions', 'Pourcentage']]
                    
                    # --- NOUVEAU : On prépare nos listes pour le graphique ---
                    pct_list = []
                    labels_list = ['Part 1', '     Part 2', 'Part 3', 'Part 4     ']
                    
                    for partie in parties:
                        bonnes_reponses = sum(
                            1 for q in range(partie['debut'], partie['fin'] + 1)
                            if reponses_etudiant_dict.get(q) == reponses_prof.get(q)
                        )
                        total = partie['fin'] - partie['debut'] + 1
                        pourcentage = (bonnes_reponses / total) * 100
                        
                        # On stocke le pourcentage pour le graphique
                        pct_list.append(pourcentage)
                        
                        data.append([
                            partie['nom'],
                            str(bonnes_reponses),
                            str(total),
                            f"{pourcentage:.1f}%"
                        ])

                    # Ajouter les totaux au tableau
                    data.append(['TOTAL ORAL', str(score.h2_oral), '100', f"{score.h2_oral}%"])
                    data.append(['SCORE TOEIC ORAL', '', '', str(score.score_oral)])



                # 3. Le tableau des scores (compact)
                    table_scores = Table(data, rowHeights=14)
                    table_scores.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 7), 
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                    ('SPAN', (0,-1), (1,-1)),
                    ('BACKGROUND', (0,-2), (-1,-2), colors.lightgrey),
                    ('BACKGROUND', (0,-1), (-1,-1), colors.lightblue),
                    ]))
                
                # 4. Le diagramme radar miniature
                    radar = get_radar_chart(pct_list, labels_list)
                
                # 5. La disposition Côte à Côte (Tableau à gauche, Radar à droite)
                    layout_table = Table([[table_scores,"", radar]], colWidths=[3.0*inch, 2.5*inch])
                    layout_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('ALIGN', (1,0), (1,0), 'RIGHT'),
                    ]))
                
                    elements.append(layout_table)
            
            # Ligne de séparation au lieu d'un saut de page
                elements.append(Spacer(1, 0.1))
                ligne = Table([['']], colWidths=[6.5*inch], style=[('LINEBELOW', (0,0), (-1,-1), 1, colors.black)])
                elements.append(ligne)
                elements.append(Spacer(1, 0.1))
            # Traiter les étudiants absents
            for etudiant in etudiants_absents:
                elements.append(Paragraph(f"Étudiant: {etudiant.nom} {etudiant.prenom}", style_heading))
                elements.append(Spacer(1, 00.1))
                elements.append(Paragraph("La feuille de cette élève n'a pas encore été scannée", style_absent))
                elements.append(Spacer(1, 0.1))

            # Générer le PDF
            doc.build(elements)

            # Préparer la réponse
            buffer.seek(0)
            response = make_response(buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=scores_oral.pdf'

            return response

        except Exception as e:
            app.logger.error(f"Erreur lors de la génération du PDF: {str(e)}")
            return jsonify({'error': str(e)}), 500


    ################### MM POUR ECRIT ##################################################
    @app.route('/api/generate-ecrit-pdf', methods=['GET'])
    def generate_ecrit_pdf():
        try:
            # Récupérer les paramètres de la requête
            site_id = request.args.get('site_id')
            promotion_id = request.args.get('promotion_id')
            groupe_id = request.args.get('groupe_id')
            semestre_id = request.args.get('semestre_id')
            test_id = request.args.get('test_id')

            # Vérifier que tous les paramètres sont présents
            if not all([site_id, promotion_id, groupe_id, semestre_id, test_id]):
                return jsonify({'error': 'Tous les paramètres sont requis'}), 400

            # Convertir les paramètres en entiers
            site_id = int(site_id)
            promotion_id = int(promotion_id)
            groupe_id = int(groupe_id)
            semestre_id = int(semestre_id)
            test_id = int(test_id)

            # Récupérer tous les étudiants du groupe
            tous_etudiants = Etudiant.query.filter(
                Etudiant.site_id == site_id,
                Etudiant.promotion_id == promotion_id,
                Etudiant.groupe_id == groupe_id,
                Etudiant.semestre_id == semestre_id
            ).all()

            if not tous_etudiants:
                return jsonify({'message': 'Aucun étudiant trouvé pour ces critères'}), 404

            # Récupérer les étudiants qui ont répondu au test
            etudiants_avec_reponses = db.session.query(Etudiant)\
                .join(ReponseEtudiant, Etudiant.id == ReponseEtudiant.etudiant_id)\
                .filter(
                    ReponseEtudiant.test_id == test_id,
                    Etudiant.site_id == site_id,
                    Etudiant.promotion_id == promotion_id,
                    Etudiant.groupe_id == groupe_id,
                    Etudiant.semestre_id == semestre_id
                )\
                .distinct()\
                .all()

            # Séparer les étudiants présents et absents
            etudiants_absents = [etudiant for etudiant in tous_etudiants if etudiant not in etudiants_avec_reponses]
            etudiants_presents = etudiants_avec_reponses

            # Récupérer les scores pour tous les étudiants
            scores = {score.etudiant_id: score for score in Score.query.filter_by(test_id=test_id).all()}

            # Récupérer les réponses correctes du professeur
            reponses_prof = {
                int(r.num_question): r.choix 
                for r in ReponseProf.query.filter_by(test_id=test_id).all()
            }

            # Créer le PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []

            # Styles
            styles = getSampleStyleSheet()
            style_title = styles['Title']
            style_heading = styles['Heading2']
            style_normal = styles['Normal']
            style_absent = ParagraphStyle(
                'Absent',
                parent=style_normal,
                textColor=colors.red,
                fontSize=12
            )

            # Titre du document
            elements.append(Paragraph("Rapport des Scores Écrit - TOEIC", style_title))
            elements.append(Spacer(1, 0.5 * inch))
        

            #nom du groupe
            groupe = Groupe.query.get(groupe_id) 
            if groupe:
                elements.append(Paragraph(f"Groupe : {groupe.nom}", style_heading))
               # elements.append(Spacer(1, 0.3 * inch))
            # date du test    
            test = Test.query.get(test_id)
            try:
                date_formatee = test.date.strftime("le %d/%m/%Y à %H:%M")
            except locale.Error:
                locale.setlocale(locale.LC_TIME, '')  
            if test and test.date:
                # Mettre la première lettre du mois en majuscule
                date_formatee = date_formatee.replace(
                    test.date.strftime("%B"), 
                    test.date.strftime("%B").capitalize()
                )
                elements.append(Paragraph(date_formatee, style_heading))

            elements.append(Spacer(1, 0.3 * inch))
            base_dir = os.path.dirname(__file__)
            logo_path = os.path.join(base_dir, "..", "..", "..", "src", "assets", "images", "eilco_logo.png")
            logo_path = os.path.normpath(logo_path)

            if os.path.exists(logo_path):
                logo = Image(logo_path, width=6*inch, height=2.4*inch)
                logo.hAlign = 'CENTER'
                    
                elements.append(logo)
                elements.append(Spacer(1, 0.2 * inch))
            else:
                print(f"⚠️ Logo introuvable : {logo_path}")
                # --- FIN LOGO ---

            elements.append(PageBreak())



            # Traiter d'abord les étudiants présents
            for etudiant in etudiants_presents:
                score = scores.get(etudiant.id)
                
                # Ajouter l'entête de l'étudiant
                elements.append(Paragraph(f"Étudiant: {etudiant.nom} {etudiant.prenom}", style_heading))
                elements.append(Spacer(1, 0.2 * inch))

                if score:
                    # Récupérer les réponses de l'étudiant
                    reponses_etudiant = ReponseEtudiant.query.filter_by(
                        etudiant_id=etudiant.id,
                        test_id=test_id
                    ).all()
                    reponses_etudiant_dict = {int(r.num_question): r.choix for r in reponses_etudiant}

                    # Calculer les scores par partie
                    parties = [
                        {'nom': 'Partie 5 (Q101-130)', 'debut': 101, 'fin': 130},
                        {'nom': 'Partie 6 (Q131-146)', 'debut': 131, 'fin': 146},
                        {'nom': 'Partie 7 (Q147-200)', 'debut': 147, 'fin': 200}
                    ]

                    # ... (votre code juste au-dessus)
                    data = [['Partie', 'Questions Correctes', 'Total Questions', 'Pourcentage']]
                    
                    # --- NOUVEAU : On prépare nos listes pour le graphique ---
                    pct_list = []
                    labels_list = ['Part 5', 'Part 6', 'Part 7']
                    
                    for partie in parties:
                        bonnes_reponses = sum(
                            1 for q in range(partie['debut'], partie['fin'] + 1)
                            if reponses_etudiant_dict.get(q) == reponses_prof.get(q)
                        )
                        total = partie['fin'] - partie['debut'] + 1
                        pourcentage = (bonnes_reponses / total) * 100
                        
                        # On stocke le pourcentage pour le graphique
                        pct_list.append(pourcentage)
                        
                        data.append([
                            partie['nom'],
                            str(bonnes_reponses),
                            str(total),
                            f"{pourcentage:.1f}%"
                        ])

                    # Ajouter les totaux au tableau
                    data.append(['TOTAL ÉCRIT', str(score.h2_ecrit), '100', f"{score.h2_ecrit}%"])
                    data.append(['SCORE TOEIC ÉCRIT','','',  str(score.score_ecrit)])

                    # Créer et styliser le tableau
                    table_scores = Table(data, rowHeights=14)
                    table_scores.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 7), 
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                    ('SPAN', (0,-1), (1,-1)),
                    ('BACKGROUND', (0,-2), (-1,-2), colors.lightgrey),
                    ('BACKGROUND', (0,-1), (-1,-1), colors.lightblue),
                    ]))
                
                # 4. Le diagramme radar miniature
                    radar = get_radar_chart(pct_list, labels_list)
                
                # 5. La disposition Côte à Côte (Tableau à gauche, Radar à droite)
                    layout_table = Table([[table_scores,"", radar]], colWidths=[3.0*inch, 2.5*inch])
                    layout_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('ALIGN', (1,0), (1,0), 'RIGHT'),
                    ]))
                
                    elements.append(layout_table)
             # Ligne de séparation au lieu d'un saut de page
                elements.append(Spacer(1, 0.1))
                ligne = Table([['']], colWidths=[6.5*inch], style=[('LINEBELOW', (0,0), (-1,-1), 1, colors.black)])
                elements.append(ligne)
                elements.append(Spacer(1, 0.1))
            # Traiter les étudiants absents
            for etudiant in etudiants_absents:
                elements.append(Paragraph(f"Étudiant: {etudiant.nom} {etudiant.prenom}", style_heading))
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(Paragraph("La feuille de cette élève n'a pas encore été scannée", style_absent))
                elements.append(Spacer(1, 0.1 * inch))

            # Générer le PDF
            doc.build(elements)

            # Préparer la réponse
            buffer.seek(0)
            response = make_response(buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=scores_ecrit.pdf'

            return response

        except Exception as e:
            app.logger.error(f"Erreur lors de la génération du PDF: {str(e)}")
            return jsonify({'error': str(e)}), 500
