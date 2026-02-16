import cv2
import numpy as np
import imutils
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageDraw

# -----------------------------------------------------
# SECTION 1: FONCTIONS DE TRANSFORMATION D'IMAGES
# -----------------------------------------------------

def order_points(pts):
    """
    Trie les points d'un contour quadrilatère pour les mettre dans un ordre standard.
    
    Args:
        pts: Points du contour
        
    Returns:
        Tableau de points dans l'ordre: haut-gauche, haut-droite, bas-droite, bas-gauche
    """
    # Initialiser le tableau de points résultant
    rect = np.zeros((4, 2), dtype="float32")
    
    # Somme des coordonnées x+y
    s = pts.sum(axis=1)
    # Différence des coordonnées x-y
    diff = np.diff(pts, axis=1)

    # Point haut-gauche = plus petite somme
    rect[0] = pts[np.argmin(s)]
    # Point bas-droite = plus grande somme
    rect[2] = pts[np.argmax(s)]

    # Point haut-droite = plus petite différence
    rect[1] = pts[np.argmin(diff)]
    # Point bas-gauche = plus grande différence
    rect[3] = pts[np.argmax(diff)]

    return rect


def four_point_transform(image, pts):
    """
    Applique une transformation en perspective à partir de quatre points.
    
    Args:
        image: Image d'entrée
        pts: Coordonnées des points pour la transformation
        
    Returns:
        Image transformée et matrice de transformation
    """
    # Ordonner les points
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # Calculer les dimensions de l'image transformée
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    # Définir les points de destination pour la transformation
    dst = np.array([
        [0, 0],                         # haut-gauche
        [maxWidth - 1, 0],              # haut-droite
        [maxWidth - 1, maxHeight - 1],  # bas-droite
        [0, maxHeight - 1]              # bas-gauche
    ], dtype="float32")

    # Calculer la matrice de transformation
    m = cv2.getPerspectiveTransform(rect, dst)
    
    # Appliquer la transformation
    warped = cv2.warpPerspective(image, m, (maxWidth, maxHeight))

    return warped, m


def auto_canny(image, sigma=0.33):
    """
    Applique l'algorithme Canny avec des seuils automatiques.
    
    Args:
        image: Image en niveaux de gris
        sigma: Paramètre pour ajuster les seuils
        
    Returns:
        Image avec les contours détectés
    """
    # Calculer la médiane de l'intensité des pixels
    m = np.median(image)

    # Calculer les seuils inférieur et supérieur
    lower = int(max(0, (1.0 - sigma) * m))
    upper = int(min(255, (1.0 + sigma) * m))
    
    # Appliquer l'algorithme Canny
    edged = cv2.Canny(image, lower, upper)

    return edged


def auto_thresh(image, thresh_min=-0.3, thresh_max=0.7):
    """
    Applique un seuillage automatique à l'image.
    
    Args:
        image: Image en niveaux de gris
        thresh_min: Facteur pour le seuil minimum
        thresh_max: Facteur pour le seuil maximum
        
    Returns:
        Tuple (valeur du seuil, image seuillée)
    """
    m = np.median(image)
    lower_thresh = int(max(0, (1.0 + thresh_min) * m))
    upper_thresh = int(min(255, (1.0 + thresh_max) * m))
    
    # Appliquer le seuillage binaire inversé
    thresh = cv2.threshold(image, lower_thresh, upper_thresh, cv2.THRESH_BINARY_INV)
    
    return thresh


def resize(image, height=None, width=None, inter=cv2.INTER_AREA):
    """
    Redimensionne une image en conservant son rapport d'aspect.
    
    Args:
        image: Image d'entrée
        height: Hauteur souhaitée (optionnel)
        width: Largeur souhaitée (optionnel)
        inter: Méthode d'interpolation
        
    Returns:
        Image redimensionnée
    """
    (h, w) = image.shape[:2]
    
    # Si aucune dimension n'est spécifiée, retourner l'image telle quelle
    if height is None and width is None:
        return image
    
    # Calculer les dimensions en fonction du paramètre fourni
    if height is not None:
        ratio = height / float(h)
        dim = (int(w * ratio), height)
    elif width is not None:
        ratio = width / float(w)
        dim = (width, int(h * ratio))

    # Redimensionner l'image
    resized = cv2.resize(image, dim, interpolation=inter)
    return resized


# -----------------------------------------------------
# SECTION 2: FONCTIONS D'AFFICHAGE ET DE PRÉTRAITEMENT
# -----------------------------------------------------

# Variable globale pour l'affichage de débogage
DEBUG = True


def img_show(img, window_name, width=None, height=None):
    """
    Affiche une image dans une fenêtre si le mode DEBUG est activé.
    
    Args:
        img: Image à afficher
        window_name: Nom de la fenêtre
        width: Largeur d'affichage (optionnel)
        height: Hauteur d'affichage (optionnel)
    """
    if not DEBUG:
        return

    if width or height:
        img_h = img.shape[0]
        img_w = img.shape[1]

        # Calculer les dimensions proportionnelles
        if width and not height:
            r = width / img_w
            height = int(img_h * r)

        if height and not width:
            r = height / img_h
            width = int(img_w * r)

        if width and height:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, width, height)

    # Afficher l'image et attendre une touche
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def preprocess(image):
    """
    Prétraite une image pour la détection des contours.
    
    Args:
        image: Image d'entrée BGR
        
    Returns:
        Tuple contenant l'image en niveaux de gris et les contours détectés
    """
    # Appliquer un filtre bilatéral pour réduire le bruit
    blurred = cv2.bilateralFilter(image, 2, 200, 200)
    
    # Convertir en niveaux de gris
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # Détecter les contours
    edged = auto_canny(gray)
    
    # Dilater les contours pour fermer les petites discontinuités
    edged_dilate = cv2.dilate(edged, np.ones((3, 3), np.uint8), iterations=1)
    
    # Éroder pour affiner les contours
    edged_erode = cv2.erode(edged_dilate, np.ones((3, 3), np.uint8), iterations=1)

    # Décommenter pour afficher les étapes intermédiaires
    # img_show(blurred, "Blurred Image", height=950)
    # img_show(gray, "Gray Image", height=950)
    # img_show(edged, "Edges", height=950)
    # img_show(edged_dilate, "Dilated Edges", height=950)
    # img_show(edged_erode, "Eroded Edges", height=950)

    return (gray, edged_dilate)


def pdf_to_image(pdf_path, page_num=0, zoom=2.0):
    """
    Convertit une page d'un fichier PDF en image.
    
    Args:
        pdf_path: Chemin du fichier PDF
        page_num: Numéro de la page à convertir (0-indexé)
        zoom: Facteur de zoom pour la conversion
        
    Returns:
        Image OpenCV (BGR)
    """
    # Ouvrir le document PDF
    pdf_document = fitz.open(pdf_path)
    
    # Charger la page spécifiée
    page = pdf_document.load_page(page_num)
    
    # Définir la matrice de transformation pour le zoom
    matrix = fitz.Matrix(zoom, zoom)
    
    # Obtenir la représentation pixmap de la page
    pix = page.get_pixmap(matrix=matrix)
    
    # Convertir en image PIL
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Convertir l'image PIL en image OpenCV
    img_cv = np.array(img)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
    
    return img_cv


# -----------------------------------------------------
# SECTION 3: FONCTIONS DE DÉTECTION DES MARQUEURS
# -----------------------------------------------------

def drawContours(img, contours, color, thickness, idx=-1):
    """
    Dessine des contours sur une image.
    
    Args:
        img: Image sur laquelle dessiner
        contours: Liste des contours à dessiner
        color: Couleur des contours (B,G,R)
        thickness: Épaisseur des contours
        idx: Index du contour à dessiner (-1 pour tous)
    """
    cv2.drawContours(img, contours, idx, color, thickness)


def contour_center(contour):
    """
    Calcule le centre d'un contour.
    
    Args:
        contour: Contour d'entrée
        
    Returns:
        Tuple (x, y) des coordonnées du centre
    """
    # Calculer les moments du contour
    M = cv2.moments(contour)
    
    if M["m00"] != 0:
        # Calculer le centre du contour
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return (cx, cy)
    else:
        return (0, 0)


import cv2
import numpy as np

def find_markers(edged, image=None):
    """
    Trouve les marqueurs triangulaires de manière robuste dans une image bruitée.
    """
    # 1. Petit nettoyage morphologique pour boucher les trous dans les contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    # 2. Trouver les contours
    cnts, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not cnts or image is None:
        return None

    markers = []
    markers_info = [] # Pour stocker (contour, aire, score_de_proximité)

    for c in cnts:
        area = cv2.contourArea(c)
        
        # Filtre de taille (ajuste selon la résolution de ton PDF)
        if 100 < area < 10000:
            peri = cv2.arcLength(c, True)
            # On augmente légèrement la tolérance (0.04 au lieu de 0.02)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            
            # 3. Critères de sélection robustes
            # - Entre 3 et 5 points (souvent le bruit ajoute un point)
            # - Doit être convexe
            if 3 <= len(approx) <= 5 and cv2.isContourConvex(approx):
                # On calcule la bounding box pour vérifier le ratio
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                
                # Un triangle de marqueur est généralement assez équilibré (pas une ligne)
                if 0.5 < aspect_ratio < 2.0:
                    markers.append(approx)
                    markers_info.append(area)

    # 4. Gestion du nombre de marqueurs
    if len(markers) < 4:
        print(f"Erreur : Seulement {len(markers)} marqueurs trouvés. Le PDF est peut-être trop bruité.")
        return None

    # 5. Si on en a trop, on garde les 4 dont l'aire est la plus proche de la médiane
    # C'est plus robuste que la moyenne car la médiane ignore les valeurs aberrantes
    if len(markers) > 4:
        median_area = np.median(markers_info)
        # On trie par différence absolue avec la médiane
        indexed_markers = sorted(enumerate(markers), 
                                 key=lambda x: abs(cv2.contourArea(x[1]) - median_area))
        markers = [indexed_markers[i][1] for i in range(4)]

    # Affichage final
    img_markers = image.copy()
    cv2.drawContours(img_markers, markers, -1, (0, 255, 0), 3)
    # img_show(img_markers, "Marqueurs détectés") # Décommente si ta fonction img_show est définie

    return markers


# -----------------------------------------------------
# SECTION 4: FONCTIONS DE TRANSFORMATION ET DÉCOUPAGE
# -----------------------------------------------------

def warpcrop(image, gray, points):
    """
    Applique une transformation en perspective et découpe les régions d'intérêt.
    
    Args:
        image: Image couleur d'entrée
        gray: Image en niveaux de gris
        points: Coordonnées des quatre points pour la transformation
        
    Returns:
        Tuple contenant:
        - ansROI: Image découpée avec transformation perspective
        - warped: Image en niveaux de gris redressée
        - upper_image: Partie supérieure de l'image
        - m_transform: Matrice de transformation
    """
    # Trier les points par coordonnée y (de haut en bas)
    points = points[points[:, 1].argsort()]
   
    # Appliquer la transformation de perspective à l'image couleur
    ansROI = four_point_transform(image, points.reshape(4, 2))[0]
    
    # Appliquer la transformation de perspective à l'image en niveaux de gris
    warped, m_transform = four_point_transform(gray, points.reshape(4, 2))

    # Extraire la partie supérieure de l'image (au-dessus des deux premiers marqueurs)
    x1, y1 = points[0][0], points[0][1]
    x2, y2 = points[1][0], points[1][1]
    upper_y = min(y1, y2) 
    upper_image = image[:upper_y, :] 
    
    # img_show(warped, "Warped", height=800)
    # img_show(upper_image, "Upper Image", height=800)

    return ansROI, warped, upper_image, m_transform



# -----------------------------------------------------
# SECTION 7: DÉTECTION ET VÉRIFICATION DES RÉPONSES
# -----------------------------------------------------

def detect_sections_columns_and_contours(thresh_img, ansROI):
    img_h, img_w = thresh_img.shape[:2]
    
    # Ratios basés sur ton générateur ReportLab
    pt_to_px = img_w / 470.0
    expected_diameter = img_w * 0.0212
    expected_radius = int(expected_diameter / 2)
    max_square_dim = int(img_w * 0.06) # Assez large pour le nombre "200"

    img_pil = Image.fromarray(cv2.cvtColor(ansROI, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    raw_squares = []

    # DÉCOUPAGE STRICT EN 4 COLONNES (Plus de fusion accidentelle !)
    num_columns = 4
    col_width = img_w // num_columns
    
    for i in range(num_columns):
        col_x = i * col_width
        col_thresh = thresh_img[:, col_x:col_x + col_width]
        contours_col, _ = cv2.findContours(col_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        col_squares = []
        for cnt in contours_col:
            x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(cnt)
            # On cherche les objets qui ont la taille d'un numéro
            if w_cont <= max_square_dim and h_cont <= max_square_dim and x_cont > 0 and y_cont > 0:  
                col_squares.append((col_x + x_cont, y_cont, w_cont, h_cont, i))
        
        # FILTRE D'ALIGNEMENT : Les vrais numéros sont tous parfaitement alignés verticalement
        if col_squares:
            # On trouve la position X médiane de la colonne
            median_x = np.median([sq[0] for sq in col_squares])
            # On ne garde que les carrés qui sont alignés sur cet axe X (tolérance de 15px)
            aligned_squares = [sq for sq in col_squares if abs(sq[0] - median_x) < 15]
            raw_squares.extend(aligned_squares)

    # Trier par Colonne, puis par position verticale (Y), puis horizontale (X)
    raw_squares.sort(key=lambda x: (x[4], x[1], x[0]))
    
    purple_squares = []
    
    # FILTRE ANTI-DOUBLON : Supprime les cases coloriées prises pour des numéros
    for sq in raw_squares:
        if not purple_squares:
            purple_squares.append(sq)
        else:
            prev_sq = purple_squares[-1]
            # Si on est dans la même colonne et sur la même ligne
            if sq[4] == prev_sq[4] and abs(sq[1] - prev_sq[1]) < 15:
                continue 
            purple_squares.append(sq)
            
    question_number = 1
    question_circles = {}
    colors_list = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255)]

    # CALCUL MATHÉMATIQUE EXACT DES RÉPONSES
    for square_idx, (x_sq, y_sq, w_sq, h_sq, _) in enumerate(purple_squares):
        square_center_y = y_sq + h_sq // 2
        
        # Position de base de la question
        x_pos_px = x_sq + (5 * pt_to_px)
        
        # Projection parfaite des 4 cases de réponse
        cx_A = int(x_pos_px + (25 * pt_to_px))
        cx_B = int(x_pos_px + (45 * pt_to_px))
        cx_C = int(x_pos_px + (65 * pt_to_px))
        cx_D = int(x_pos_px + (85 * pt_to_px))
        
        final_circles_for_question = [
            (cx_A, square_center_y, expected_radius, 0, 0),
            (cx_B, square_center_y, expected_radius, 0, 0),
            (cx_C, square_center_y, expected_radius, 0, 0),
            (cx_D, square_center_y, expected_radius, 0, 0)
        ]
        
        question_circles[f"Question {question_number}"] = final_circles_for_question
        
        # Dessiner le résultat théorique pour le debug
        for i, (cx, cy, r, _, _) in enumerate(final_circles_for_question):
            color = colors_list[i % len(colors_list)]
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=color, width=2)

        question_number += 1

    img_pil.save("debug_cercles_finaux.jpg")
    return question_circles

def check_answers(question_circles, img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    answers = ['A', 'B', 'C', 'D']
    page_answers = {}
    
    # SEUIL DE REMPLISSAGE (À ajuster si besoin)
    # 0.40 signifie que 40% de l'intérieur du cercle doit être strictement noir.
    # Une croix fait généralement entre 0.10 et 0.25.
    FILL_THRESHOLD = 0.50
    
    for question_number, circles in enumerate(question_circles.values(), start=1):
        fill_ratios = []
        
        for cx, cy, r, _, _ in circles:
            # On prend 80% du rayon pour ignorer le bord imprimé du cercle
            roi_r = max(1, int(r * 0.8))
            y1, y2 = max(0, cy - roi_r), min(gray_img.shape[0], cy + roi_r)
            x1, x2 = max(0, cx - roi_r), min(gray_img.shape[1], cx + roi_r)
            roi = gray_img[y1:y2, x1:x2]
            
            if roi.size == 0:
                fill_ratios.append(0)
                continue
                
            # 1. Binariser l'image : tout ce qui est plus foncé que 150 devient BLANC (valeur 255), le reste NOIR (0)
            # Cela permet d'isoler uniquement les vrais coups de crayon
            _, thresh_roi = cv2.threshold(roi, 200, 255, cv2.THRESH_BINARY_INV)
            
            # 2. Compter le nombre de pixels coloriés
            colored_pixels = cv2.countNonZero(thresh_roi)
            total_pixels = roi.shape[0] * roi.shape[1]
            
            # 3. Calculer le ratio de remplissage (entre 0.0 et 1.0)
            ratio = colored_pixels / total_pixels if total_pixels > 0 else 0
            fill_ratios.append(ratio)
            
        # Trouver la case la plus remplie
        max_ratio = max(fill_ratios)
        
        # Si la case la plus remplie dépasse notre seuil de 40%
        if max_ratio >= FILL_THRESHOLD:
            # On vérifie si l'étudiant n'a pas noirci deux cases (on prend celles qui sont proches du max)
            selected = [answers[i] for i, ratio in enumerate(fill_ratios) if ratio >= FILL_THRESHOLD and ratio >= max_ratio - 0.15]
            
            if len(selected) > 1:
                page_answers[question_number] = "Réponse multiple"
            else:
                page_answers[question_number] = selected[0]
        else:
            # Si aucune case ne dépasse 40% (même s'il y a une croix à 20%), c'est considéré vide
            page_answers[question_number] = "Vide"
            
    return page_answers


# -----------------------------------------------------
# SECTION 8: DÉTECTION DU NUMÉRO D'ÉTUDIANT
# -----------------------------------------------------

import cv2
import numpy as np

import cv2
import numpy as np

def detect_student_number(image):
    """
    Détecte le numéro d'étudiant à partir des cercles remplis sous des carrés de repère.
    Les cercles vont de -1 (tout en haut) à 9 (tout en bas).
    """
    # 1. Convertir en niveaux de gris et binariser
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # 2. Détecter les contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_squares = []

    # 3. Identifier les carrés de repère
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)
        if len(approx) == 4 and 100 < area < 5000: 
            detected_squares.append(approx)

    # 4. Trier les carrés de GAUCHE à DROITE
    detected_squares = sorted(detected_squares, key=lambda square: cv2.boundingRect(square)[0])

    image_with_squares = image.copy()
    student_number = ""

    # 5. Analyser chaque colonne
    for square in detected_squares:
        x_min, y_min, w, h = cv2.boundingRect(square)
        x_max = x_min + w
        
        zone_potentielle = gray[:, x_min:x_max] 
        thresh_zone = thresh[:, x_min:x_max] 

        # Détecter les cercles
        circles = cv2.HoughCircles(
            zone_potentielle,
            cv2.HOUGH_GRADIENT, 
            dp=1.5, minDist=15, param1=60, param2=18, minRadius=7, maxRadius=12
        )

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            # Trier les cercles de haut en bas (index 0 correspondra à -1)
            circles_sorted_by_y = sorted(circles, key=lambda c: c[1])
            
            best_circle_index = None # Initialisé à None pour éviter la confusion avec la valeur -1
            max_filled_pixels = 0
            
            # Analyser chaque cercle dans la colonne
            for idx, (x, y, r) in enumerate(circles_sorted_by_y):
                mask = np.zeros(thresh_zone.shape, dtype="uint8")
                cv2.circle(mask, (x, y), r, 255, -1)
                
                masked_circle = cv2.bitwise_and(thresh_zone, thresh_zone, mask=mask)
                filled_pixels = cv2.countNonZero(masked_circle)
                
                if filled_pixels > max_filled_pixels:
                    max_filled_pixels = filled_pixels
                    best_circle_index = idx

                # Optionnel : Dessin de tous les cercles détectés pour le debug
                cv2.circle(image_with_squares, (x + x_min, y), r, (255, 0, 0), 2)
            
            # Si un cercle suffisamment rempli a été trouvé
            if max_filled_pixels > 50 and best_circle_index is not None:
                # --- LA MODIFICATION EST ICI ---
                # L'index 0 devient -1, l'index 1 devient 0, etc.
                valeur_detectee = best_circle_index - 1
                
                student_number += str(valeur_detectee)
                
                # Dessiner le cercle choisi en vert et écrire la valeur au-dessus du carré
                chosen_circle = circles_sorted_by_y[best_circle_index]
                cv2.circle(image_with_squares, (chosen_circle[0] + x_min, chosen_circle[1]), chosen_circle[2], (0, 255, 0), 4)
                cv2.putText(image_with_squares, str(valeur_detectee), (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    std_clean = ""
    for i in range (len(student_number)) : 
        if student_number[i] != "0" : 
            std_clean = student_number[i:]
            break
    student_number = std_clean 

    #cv2.imshow("Detection", image_with_squares)
    #cv2.waitKey(0)

    return student_number
        


# -----------------------------------------------------
# SECTION 9: FONCTION PRINCIPALE DE TRAITEMENT PDF
# -----------------------------------------------------

def process_pdf_for_students(pdf_path):
    """
    Traite un fichier PDF contenant les feuilles de réponses des étudiants.
    
    Args:
        pdf_path: Chemin vers le fichier PDF à traiter
    
    Returns:
        dict: Un dictionnaire où la clé est le numéro de l'étudiant et la valeur sont ses réponses.
    """
    # Ouvrir le document PDF
    pdf_document = fitz.open(pdf_path)
    
    # Dictionnaire pour stocker les résultats
    student_results = {}

    # Traiter chaque page du PDF (chaque étudiant)
    for page_number in range(pdf_document.page_count): 
        # Convertir la page en image
        page_img = pdf_to_image(pdf_path, page_num=page_number)

        # print(f"\n--- Étudiant {page_number + 1} ---")
        
        # Prétraitement de l'image
        gray, edged = preprocess(page_img)  
        
        # Détecter les marqueurs triangulaires
        markers = find_markers(edged, page_img)
        
        # Calculer les centres des marqueurs
        markers_center = np.array([contour_center(c) for c in markers]) 
        
        # Appliquer la transformation et découper les régions
        ansROI, warped, upper_image, m_transform = warpcrop(page_img, gray, markers_center)
        
        # Détecter le numéro d'étudiant dans la partie supérieure
        student_number = detect_student_number(upper_image)
        
        # Appliquer un seuillage à l'image transformée
        thresh_val, thresh_img = auto_thresh(warped)
        #img_show(thresh_img, "Thresholded Warped Image", height=1000)

        kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60))
        lignes_verticales = cv2.morphologyEx(thresh_img, cv2.MORPH_OPEN, kernel_vertical)
        thresh_img = cv2.subtract(thresh_img, lignes_verticales)
        
        # Améliorer l'image seuillée
        thresh_img_dilate = cv2.dilate(thresh_img, np.ones((3, 3), np.uint8), iterations=3)
        thresh_img_erode = cv2.erode(thresh_img_dilate, np.ones((3, 3), np.uint8), iterations=3)
        thresh_img = thresh_img_erode
        
        # Redimensionner les images pour un meilleur traitement
        thresh_img = resize(thresh_img, height=1000)
        ansROI = resize(ansROI, height=1000)
        
        # Enlever les bords (qui peuvent contenir des artefacts)
        thresh_img = thresh_img[10:-10, 10:-10]
        ansROI = ansROI[10:-10, 10:-10]
        
        # Métadonnées pour la détection des questions
        metadata = {"n_questions": 200}  
        
        # Détecter les sections, colonnes et les cercles de réponses
        question_circles = detect_sections_columns_and_contours(thresh_img, ansROI)
        
        # Vérifier les réponses de l'étudiant
        student_answers = check_answers(question_circles, ansROI)
        # print(student_answers)
        
        # Ajouter les résultats au dictionnaire avec le numéro d'étudiant comme clé
        student_results[student_number] = student_answers
        """img_show(warped, "Warped Image with Detected Circles", height=1000)
        img_show(ansROI, "Answer ROI", height=1000)
        img_show(upper_image, "Upper Image", height=1000)
        img_show(thresh_img_erode, "Thresholded Image", height=1000)
        img_show(thresh_img_dilate, "Detected Squares and Circles", height=1000)
    """
    print(student_results)
    return student_results

        




# -----------------------------------------------------
# SECTION 10: POINT D'ENTRÉE DU PROGRAMME
# -----------------------------------------------------

# Exemple d'utilisation
#if __name__ == "__main__":
#   pdf_path = r"C:\Users\HugoL\Downloads\scan_ccadet_2026-02-16-14-57-33.pdf"
#   process_pdf_for_students(pdf_path)