from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.graphics.shapes import Drawing, Polygon
from datetime import datetime

def draw_filled_triangle(canvas, x1, y1, x2, y2, x3, y3, fill_color=colors.black):
    drawing = Drawing(width=0, height=0)
    triangle = Polygon([x1, y1, x2, y2, x3, y3])
    triangle.fillColor = fill_color
    triangle.strokeColor = None
    drawing.add(triangle)
    drawing.drawOn(canvas, 0, 0)

def generate_toeic_pdf(pdf_filename, etudiants, test):
    c = canvas.Canvas(pdf_filename, pagesize=A4)
    width, height = A4
    x_start = 80
    y_start = height - 30
    
    # Formater la date dans un format français
    date_test = test.date.strftime("%A %d %B %Y").lower()
    
    # Créer une description de cours basée sur les informations du test
    course_description = f"{test.nom}"
    # if test.promotions:
    #     course_description += f" - {', '.join([p for p in test.promotions])}"
    
    # Instructions par défaut avec un peu plus d'informations sur la manière de remplir les cercles
    instructions = (
        "Noirciez les cercles avec un crayon HB ou 2B. \n "
        "Pas de stylo. \n"
        "Effacez bien pour corriger.\n"
        "Ne cochez pas, ne dépassez pas."
    )

    
    # # Description du test si disponible
    # if test.description:
    #     instructions = test.description
    
    # Loop over students and generate individual pages for each
    for etudiant in etudiants:
        name = f"{etudiant.prenom} {etudiant.nom}"
        student_number = str(etudiant.id).zfill(10)  # Pad with zeros to 10 digits
        
        # Table header for student details
        table_data = [
            ["Name", name],
            ["Course", course_description],
            ["Period", f"{etudiant.semestre.nom} - {etudiant.promotion.nom}"],
            ["Date", date_test],
            ["Instructions", instructions]
        ]

        col_widths = [110, 160]
        row_heights = [20, 20, 20, 20, 44]
        table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 8),
            ('FONTSIZE', (1, 4), (1, 4), 6),  # Augmenter ici (colonne 1, ligne 4 = instructions)
            ('LEADING', (1, 4), (1, 4), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        c.setFont("Helvetica-Bold", 8)
        
        # Draw the table for the student
        table.wrapOn(c, width, height)
        table.drawOn(c, 35, y_start - 110)

        # Student number area
        num_x_start = width / 2 + 100
        num_y_start = y_start
        circle_diameter = 10
        c.drawString(num_x_start - 70, num_y_start, "Student Number")

        # Drawing the student number in circles
        for i, num in enumerate(student_number):
            c.setStrokeColor(colors.black)
            c.rect(num_x_start + (i * (circle_diameter + 3)), num_y_start, circle_diameter, circle_diameter, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 7)
            c.drawString(num_x_start + 2 + (i * (circle_diameter + 3)), num_y_start + 2, num)

        # Draw all circles as empty, then color only those matching the student number
        circle_x_start = num_x_start
        circle_y_start = num_y_start - 20

        # First, draw all empty circles
        for row in range(10):
            c.setFont("Helvetica", 6)
            c.drawString(circle_x_start - 12, circle_y_start - row * (circle_diameter + 3), str(row))
            
            for col in range(len(student_number)):
                x_pos = circle_x_start + col * (circle_diameter + 3)
                y_pos = circle_y_start - row * (circle_diameter + 3)
                c.setLineWidth(1)
                c.circle(x_pos + circle_diameter / 2, y_pos, circle_diameter / 2, stroke=1, fill=0)

        # Then, color only the circles that match the student number
        for col in range(len(student_number)):
            digit = int(student_number[col])
            row = digit  # The row corresponding to this digit
            
            x_pos = circle_x_start + col * (circle_diameter + 3)
            y_pos = circle_y_start - row * (circle_diameter + 3)
            
            c.setFillColor(colors.black)
            c.circle(x_pos + circle_diameter / 2, y_pos, circle_diameter / 2, stroke=1, fill=1)

        # Section for the questions
        question_number = 1
        question_y_start = y_start - 190
        question_y = y_start - 170
        circle_diameter = 10
        column_width = width / 2
        
        # Exemple d'un cercle correctement rempli
        example_x = x_start
        example_y = question_y_start + 60
        c.drawString(example_x, example_y, "Exemple d'une réponse correcte:")
        
        # Cercle vide
        c.circle(example_x + 100, example_y, circle_diameter / 2, stroke=1, fill=0)
        c.drawString(example_x + 120, example_y, "Incorrect")
        
        # Cercle bien rempli
        c.setFillColor(colors.black)
        c.circle(example_x + 180, example_y, circle_diameter / 2, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.drawString(example_x + 200, example_y, "Correct")
        
        for section in range(4):
            for row in range(50):
                y_pos = question_y - (row * 12.5)
                if row < 50:
                    x_pos = x_start
                c.setFont("Helvetica", 10)
                c.setFillColor(colors.black)
                c.drawString(x_pos - 5, y_pos - 3, str(question_number))

                for i, letter in enumerate(["A", "B", "C", "D"]):
                    response_x_pos = x_pos + 25 + (i * 20)
                    c.circle(response_x_pos, y_pos, circle_diameter / 2, stroke=1, fill=0)
                    c.setFont("Helvetica-Bold", 6)
                    c.setFillColor(colors.Color(0.8, 0.8, 0.8))  # Gris foncé
                    c.drawString(response_x_pos - 2, y_pos - 2, letter)

                question_number += 1

                # Draw triangles and text based on sections
                if section == 0:
                    triangle_x1 = x_start - 25
                    triangle_y1 = question_y_start + 40
                    triangle_x2 = x_start - 5
                    triangle_y2 = question_y_start + 40
                    triangle_x3 = x_start - 15
                    triangle_y3 = question_y_start + 50
                    draw_filled_triangle(c, triangle_x1, triangle_y1, triangle_x2, triangle_y2, triangle_x3, triangle_y3, colors.black)

                    c.setStrokeColor(colors.black)
                    c.rect(x_start - 25, question_y_start - (50 * 12.1) + 5, 250, (52 * 12) + 10)

                    triangle_x1 = x_start - 25
                    triangle_y1 = question_y_start - (50 * 12) - 15
                    triangle_x2 = x_start - 5
                    triangle_y2 = question_y_start - (50 * 12) - 15
                    triangle_x3 = x_start -15
                    triangle_y3 = question_y_start - (50 * 12) - 5
                    draw_filled_triangle(c, triangle_x1, triangle_y1, triangle_x2, triangle_y2, triangle_x3, triangle_y3, colors.black)

                    c.setFont("Helvetica-Bold", 8)
                    c.drawString(x_start + 110, question_y_start - (50 * 12) - 10, "Listening")
                elif section == 2:
                    triangle_x1 = x_start + 205
                    triangle_y1 = question_y_start + 40
                    triangle_x2 = x_start + 225
                    triangle_y2 = question_y_start + 40
                    triangle_x3 = x_start + 215
                    triangle_y3 = question_y_start + 50
                    draw_filled_triangle(c, triangle_x1, triangle_y1, triangle_x2, triangle_y2, triangle_x3, triangle_y3, colors.black)

                    c.setStrokeColor(colors.black)
                    c.rect(x_start - 15, question_y_start - (50 * 12.1) + 5, 240, (52 * 12) + 10)

                    triangle_x1 = x_start + 205
                    triangle_y1 = question_y_start - (50 * 12) - 15
                    triangle_x2 = x_start + 225
                    triangle_y2 = question_y_start - (50 * 12) - 15
                    triangle_x3 = x_start + 215
                    triangle_y3 = question_y_start - (50 * 12) - 5
                    draw_filled_triangle(c, triangle_x1, triangle_y1, triangle_x2, triangle_y2, triangle_x3, triangle_y3, colors.black)

                    c.setFont("Helvetica-Bold", 8)
                    c.drawString(x_start + 130, question_y_start - (50 * 12) - 10, "Reading")

            x_start += 120

        # Final triangle at the end
        triangle_x1 = x_start + 225
        triangle_y1 = question_y_start + 150
        triangle_x2 = x_start + 245
        triangle_y2 = question_y_start + 150
        triangle_x3 = x_start + 235
        triangle_y3 = question_y_start
        draw_filled_triangle(c, triangle_x1, triangle_y1, triangle_x2, triangle_y2, triangle_x3, triangle_y3, colors.black)
        # Reset position after drawing questions
        x_start = 30
        y_start = height - 30
        # Move to the next page
        c.showPage()

    c.save()
    print(f"PDF generated: {pdf_filename}")

# Exemple d'utilisation avec les objets de la base de données
# (Cet exemple ne s'exécutera pas tel quel - il montre comment appeler la fonction)
"""
# Dans une route Flask par exemple
@app.route('/generate_toeic_pdf/<int:test_id>')
def generate_toeic_sheets(test_id):
    test = Test.query.get_or_404(test_id)
    
    # Récupérer tous les étudiants concernés par ce test
    # (à adapter selon votre logique d'association entre tests et étudiants)
    etudiants = []
    for promotion in test.promotions:
        for etudiant in promotion.etudiants:
            etudiants.append(etudiant)
    
    # Générer le PDF
    pdf_filename = f"toeic_test_{test_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    generate_toeic_pdf(pdf_filename, etudiants, test)
    
    # Retourner le fichier PDF au navigateur
    return send_file(pdf_filename, as_attachment=True)
"""