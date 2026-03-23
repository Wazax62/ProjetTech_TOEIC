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
    Prétraite une image pour la détection des contours avec normalisation de l'éclairage.
    """
    # 1. Filtre bilatéral pour réduire le bruit tout en gardant des bords nets
    # (J'ai légèrement augmenté les paramètres pour mieux lisser le grain de papier)
    blurred = cv2.bilateralFilter(image, 9, 75, 75)
    
    # 2. Convertir en niveaux de gris
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # 3. NOUVEAU : Normalisation du contraste (CLAHE)
    # Permet de rattraper les zones d'ombre ou de sur-exposition du scan
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray_clahe = clahe.apply(gray)

    # 4. Détecter les contours sur l'image corrigée
    edged = auto_canny(gray_clahe)
    
    # 5. Dilater puis éroder pour fermer les petites discontinuités (Fermeture morphologique)
    edged_dilate = cv2.dilate(edged, np.ones((3, 3), np.uint8), iterations=1)
    edged_erode = cv2.erode(edged_dilate, np.ones((3, 3), np.uint8), iterations=1)

    # On renvoie bien gray (pour la suite de ton code) et edged_erode (pour les marqueurs)
    return (gray, edged_erode)


def pdf_to_image(pdf_path, page_num=0, zoom=2.0):
    """
    Convertit une page d'un fichier PDF en image.
    """
    # Utilisation de 'with' pour garantir que le fichier est fermé après lecture !
    with fitz.open(pdf_path) as pdf_document:
        page = pdf_document.load_page(page_num)
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
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
    if image is None:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    candidates = []
    
    # 1. On récupère TOUS les candidats qui ressemblent de près ou de loin à un marqueur
    for c in cnts:
        area = cv2.contourArea(c)
        if 150 < area < 1500: 
            rect = cv2.minAreaRect(c)
            w, h = rect[1]
            if w > 0 and h > 0:
                aspect_ratio = max(w, h) / min(w, h)
                if 0 < aspect_ratio < 2.8:
                    fill_ratio = area / (w * h)
                    if 0.35 < fill_ratio < 0.65:
                        peri = cv2.arcLength(c, True)
                        approx = cv2.approxPolyDP(c, 0.05 * peri, True)
                        
                        if 3 <= len(approx) <= 5:
                            # ON AJOUTE LE CENTRE DU TRIANGLE POUR NOTRE CALCUL SPATIAL
                            M = cv2.moments(approx)
                            if M["m00"] != 0:
                                cx = int(M["m10"] / M["m00"])
                                cy = int(M["m01"] / M["m00"])
                                candidates.append((approx, cx, cy))

    if len(candidates) < 4:
        print(f"Erreur : Seulement {len(candidates)} candidats trouvés.")
        return None

    # 2. L'IDÉE DE GÉNIE : Le tri par position spatiale
    # On récupère les dimensions de la page scannée
    height, width = image.shape[:2]
    
    # On cherche le candidat le plus proche de chaque coin (Théorème de Pythagore)
    
    # Haut-Gauche (Top-Left) : Coordonnées (0, 0)
    tl = min(candidates, key=lambda c: c[1]**2 + c[2]**2)
    
    # Haut-Droite (Top-Right) : Coordonnées (width, 0)
    tr = min(candidates, key=lambda c: (c[1] - width)**2 + c[2]**2)
    
    # Bas-Gauche (Bottom-Left) : Coordonnées (0, height)
    bl = min(candidates, key=lambda c: c[1]**2 + (c[2] - height)**2)
    
    # Bas-Droite (Bottom-Right) : Coordonnées (width, height)
    br = min(candidates, key=lambda c: (c[1] - width)**2 + (c[2] - height)**2)
    
    # On extrait uniquement les contours de nos 4 gagnants
    markers = [tl[0], tr[0], br[0], bl[0]]

    # Petite sécurité : on vérifie qu'on n'a pas sélectionné le même triangle pour deux coins différents
    # (ce qui arriverait si tout un côté de la page est rogné)
    unique_markers = {tuple(m.flatten()) for m in markers}
    if len(unique_markers) < 4:
         print("Erreur : Impossible de trouver un marqueur distinct pour chaque coin.")
         return None
         

    # Affichage
    img_markers = image.copy()
    cv2.drawContours(img_markers, markers, -1, (0, 255, 0), 3)
    #img_show(img_markers, "Marqueurs détectés", height=800)

    return markers


def debug_markers(image):
    """
    Affiche tous les contours détectés avec leurs statistiques mathématiques
    pour comprendre pourquoi l'algorithme les rejette.
    """
    if image is None:
        print("Erreur : Aucune image fournie au débogueur.")
        return

    # On crée une copie pour dessiner dessus
    debug_img = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Même seuillage que notre fonction principale
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Débogage : {len(cnts)} contours totaux trouvés sur l'image.")
    
    for c in cnts:
        area = cv2.contourArea(c)
        
        # On ignore juste les micro-poussières de moins de 50 pixels pour ne pas polluer l'écran
        if area > 50:
            rect = cv2.minAreaRect(c)
            w, h = rect[1]
            
            if w > 0 and h > 0:
                aspect_ratio = max(w, h) / min(w, h)
                fill_ratio = area / (w * h)
                
                # 1. Dessiner le contour en bleu clair
                cv2.drawContours(debug_img, [c], -1, (255, 150, 0), 2)
                
                # 2. Trouver le centre pour placer le texte
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                else:
                    cx, cy = int(rect[0][0]), int(rect[0][1])
                    
                # 3. Écrire les stats en rouge fluo
                text_A = f"A: {int(area)}"
                text_R = f"R: {aspect_ratio:.1f}"
                text_F = f"F: {fill_ratio:.2f}"
                
                # J'utilise une police assez petite pour que ça rentre
                cv2.putText(debug_img, text_A, (cx - 20, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
                cv2.putText(debug_img, text_R, (cx - 20, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
                cv2.putText(debug_img, text_F, (cx - 20, cy + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # Sauvegarder l'image sur ton ordinateur pour pouvoir zoomer tranquillement
    cv2.imwrite("debug_vision_ordi.jpg", debug_img)
    print("Image sauvegardée sous 'debug_vision_ordi.jpg' dans le dossier de ton script.")



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
           # Si un cercle suffisamment rempli a été trouvé
            if max_filled_pixels > 50 and best_circle_index is not None:
                
                chosen_circle = circles_sorted_by_y[best_circle_index]
                y_cercle = chosen_circle[1]
                y_carre_centre = y_min + (h / 2.0)
                
                # --- 1. L'ESPACEMENT RÉEL (La solution anti-décalage) ---
                # On calcule l'écart moyen entre les cercles trouvés dans CETTE colonne
                y_coords = [c[1] for c in circles_sorted_by_y]
                diffs = np.diff(y_coords)
                
                # On ignore les grands écarts si OpenCV a raté un cercle vide au milieu
                ecarts_valides = [d for d in diffs if h * 0.8 < d < h * 2.0]
                
                if len(ecarts_valides) > 0:
                    espacement = np.median(ecarts_valides)
                else:
                    espacement = h * 1.3 # Fallback de sécurité
                
                # --- 2. CALCUL DU CHIFFRE EXACT ---
                # Distance totale entre le centre du carré et notre cercle rempli
                distance_totale = y_cercle - y_carre_centre
                
                # On convertit cette distance en "nombre de sauts"
                nombre_de_sauts = distance_totale / espacement
                
                # D'après les mathématiques de ton PDF ReportLab : 
                # Le centre du chiffre '0' se trouve toujours à environ 1.15 saut du centre du carré.
                # Le '1' est à 2.15, le '2' est à 3.15, etc.
                valeur_detectee = round(nombre_de_sauts - 1.15)
                
                # Sécurité pour éviter un bug si un étudiant coche en dehors de la zone
                valeur_detectee = max(0, min(9, valeur_detectee))
                
                student_number += str(valeur_detectee)
                
                # Dessiner le cercle choisi en vert et écrire la valeur
                cv2.circle(image_with_squares, (chosen_circle[0] + x_min, chosen_circle[1]), chosen_circle[2], (0, 255, 0), 4)
                cv2.putText(image_with_squares, str(valeur_detectee), (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    std_clean = ""
    for i in range (len(student_number)) : 
        if student_number[i] != "0" : 
            std_clean = student_number[i:]
            break
    student_number = std_clean 

    cv2.imshow("Detection", image_with_squares)
    cv2.waitKey(0)

    return student_number
        


# -----------------------------------------------------
# SECTION 9: FONCTION PRINCIPALE DE TRAITEMENT PDF
# -----------------------------------------------------

def process_pdf_for_students(pdf_path):
    """
    Traite un fichier PDF contenant les feuilles de réponses des étudiants.
    """
    student_results = {}

    # Le bloc 'with' va automatiquement libérer le fichier PDF, même si une erreur survient
    with fitz.open(pdf_path) as pdf_document:
        page_count = pdf_document.page_count
        
    # On boucle sur le nombre de pages (le fichier est ré-ouvert page par page dans pdf_to_image)
    for page_number in range(page_count): 
        # Convertir la page en image
        page_img = pdf_to_image(pdf_path, page_num=page_number)
        
        # Prétraitement de l'image
        gray, edged = preprocess(page_img)  

        #debug_markers(page_img)
        
        # Détecter les marqueurs triangulaires
        markers = find_markers(edged, page_img)
        
        # ==========================================
        # AJOUT : Vérification de sécurité CRUCIALE
        # ==========================================
        if markers is None:
            raise ValueError(f"Impossible de détecter les 4 marqueurs sur la page {page_number + 1}. Le scan est peut-être coupé ou trop bruité.")
        
        # Calculer les centres des marqueurs
        markers_center = np.array([contour_center(c) for c in markers]) 
        
        # Appliquer la transformation et découper les régions
        ansROI, warped, upper_image, m_transform = warpcrop(page_img, gray, markers_center)
        
        # Détecter le numéro d'étudiant dans la partie supérieure
        student_number = detect_student_number(upper_image)
        
        # ... (le reste de votre code de cette fonction ne change pas) ...
        # Appliquer un seuillage à l'image transformée
        thresh_val, thresh_img = auto_thresh(warped)
        
        kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60))
        lignes_verticales = cv2.morphologyEx(thresh_img, cv2.MORPH_OPEN, kernel_vertical)
        thresh_img = cv2.subtract(thresh_img, lignes_verticales)
        
        thresh_img_dilate = cv2.dilate(thresh_img, np.ones((3, 3), np.uint8), iterations=3)
        thresh_img_erode = cv2.erode(thresh_img_dilate, np.ones((3, 3), np.uint8), iterations=3)
        thresh_img = thresh_img_erode
        
        thresh_img = resize(thresh_img, height=1000)
        ansROI = resize(ansROI, height=1000)
        
        thresh_img = thresh_img[10:-10, 10:-10]
        ansROI = ansROI[10:-10, 10:-10]
        
        question_circles = detect_sections_columns_and_contours(thresh_img, ansROI)
        student_answers = check_answers(question_circles, ansROI)
        student_results[student_number] = student_answers
        print(student_number,page_number + 1)
        #img_show(ansROI, f"Réponses de l'étudiant {student_number} - Page {page_number + 1}", height=800)

    return student_results

        




# -----------------------------------------------------
# SECTION 10: POINT D'ENTRÉE DU PROGRAMME
# -----------------------------------------------------

# Exemple d'utilisation
#if __name__ == "__main__":
#   pdf_path = r"C:\Users\HugoL\Downloads\scan_apodvin_2026-03-23-10-09-38.pdf"
#   print(process_pdf_for_students(pdf_path))