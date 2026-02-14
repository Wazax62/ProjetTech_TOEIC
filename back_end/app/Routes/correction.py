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
    # cv2.imshow(window_name, img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


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


def find_markers(edged, image=None):
    """
    Trouve les marqueurs triangulaires dans l'image.
    
    Args:
        edged: Image des contours
        image: Image originale pour l'affichage (optionnel)
        
    Returns:
        Liste des marqueurs trouvés ou None en cas d'échec
    """
    # Trouver tous les contours
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if not cnts:
        return None

    if image is None:
        return None
    
    # Dessiner tous les contours sur une copie de l'image
    img = image.copy()
    cv2.drawContours(img, cnts, -1, (255, 0, 0), 2)
    # img_show(img, "Contours", height=950)

    markers = []
    markers_area = []
    
    if len(cnts) > 0:
        # Trier les contours par taille décroissante
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        # Examiner chaque contour
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 100:
                # Approximer le contour
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)

                # Si le contour approximé a 3 points, c'est potentiellement un marqueur
                if len(approx) == 3 and area > 100 and area < 5000:
                    markers_area.append(area)
                    markers.append(approx)

        # Vérifier qu'on a trouvé au moins 4 marqueurs
        if len(markers) < 4:
            # print("Couldn't find all the four markers." + " Cannot continue. Aborting!")
            return None

        # Si plus de 4 triangles sont trouvés, ne garder que les 4 plus similaires en taille
        while len(markers) > 4:
            mean = np.mean(markers_area)
            diff_mean = sorted([(abs(mean - v), i) for i, v in enumerate(markers_area)], reverse=True)
            del markers_area[diff_mean[0][1]]
            del markers[diff_mean[0][1]]

    else:
        # print("Error! No contour found! Impossible to continue. Aborting!")
        return None

    # Afficher les marqueurs sélectionnés
    if len(markers) > 0:
        img = image.copy()
        cv2.drawContours(img, markers, -1, (255, 0, 0), 2)
        # img_show(img, "Markers", height=950)
    else:
        # print("Error! No marker found! Giving up.")
        return None

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
# SECTION 5: FONCTIONS DE TRI DES CONTOURS
# -----------------------------------------------------

def sort_contours(contours, method="left-to-right"):
    """
    Trie les contours selon un critère spécifié.
    
    Args:
        contours: Liste des contours à trier
        method: Méthode de tri ("left-to-right", "right-to-left", "top-to-bottom", "bottom-to-top")
        
    Returns:
        Liste des contours triés
    """
    reverse = False
    i = 0

    # Définir l'axe et l'ordre de tri
    if method == "top-to-bottom":
        i = 1
    elif method == "right-to-left":
        reverse = True
    elif method == "bottom-to-top":
        reverse = True
        i = 1

    # Obtenir les rectangles englobants
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    
    # Trier les contours et les boîtes englobantes ensemble
    (contours, bounding_boxes) = zip(*sorted(zip(contours, bounding_boxes),
                                          key=lambda b: b[1][i], reverse=reverse))

    return contours


def sort_questionMarks(questionMarks, questions_format):
    """
    Trie les marques de questions selon le format spécifié.
    
    Args:
        questionMarks: Liste des marques de questions
        questions_format: Format des questions [lignes, colonnes]
        
    Returns:
        Liste triée des marques de questions
    """
    rows = questions_format[0]

    # Trier d'abord de gauche à droite
    questionMarks = sort_contours(questionMarks, method="left-to-right")[0]
    qm = []
    
    # Pour chaque colonne, trier de haut en bas
    for i in np.arange(0, len(questionMarks), rows):
        qm_col = sort_contours(questionMarks[i:i + rows], method="top-to-bottom")[0]
        qm.extend(qm_col)

    return qm


# -----------------------------------------------------
# SECTION 6: FONCTIONS DE DÉFINITION DES RÉGIONS
# -----------------------------------------------------

def boundingRect_contour(c=None, br=None):
    """
    Convertit un rectangle englobant en contour ou vice versa.
    
    Args:
        c: Contour (optionnel)
        br: Rectangle englobant (x, y, w, h) (optionnel)
        
    Returns:
        Contour correspondant au rectangle englobant
    """
    if c is not None:
        (x, y, w, h) = cv2.boundingRect(c)
    elif br is not None:
        (x, y, w, h) = br
    else:
        return None

    # Créer un contour rectangulaire
    brc = np.array([
        [x, y],
        [x, y + h],
        [x + w, y + h],
        [x + w, y]
    ]).reshape(4, 1, 2)

    return brc


def define_each_alts_region(alts_regions, n_alternatives, alt_width):
    """
    Calcule les régions individuelles pour chaque alternative.
    
    Args:
        alts_regions: Régions des alternatives
        n_alternatives: Nombre d'alternatives par question
        alt_width: Largeur de chaque alternative
        
    Returns:
        Liste de toutes les régions d'alternatives
    """
    all_alternatives = []
    
    for alts in alts_regions:
        startColumn = alts[0][0][0]
        rowUp = alts[0][0][1]
        rowDown = alts[1][0][1]

        alternatives = []
        for i in range(n_alternatives):
            # Calculer la position de chaque alternative
            leftColumn = startColumn + (i * alt_width)
            alt = [[[int(leftColumn), int(rowUp)]],
                   [[int(leftColumn), int(rowDown)]],
                   [[int(leftColumn + alt_width), int(rowDown)]],
                   [[int(leftColumn + alt_width), int(rowUp)]]]
            alt = np.asarray(alt)
            alternatives.append(alt)

        all_alternatives.append(alternatives)
    
    return all_alternatives


def define_alternatives_region(questionMarks, marker_height, n_alternatives, img=None):
    """
    Calcule les régions des alternatives basées sur les marques de questions.
    
    Args:
        questionMarks: Marques de questions
        marker_height: Hauteur des marqueurs
        n_alternatives: Nombre d'alternatives par question
        img: Image pour l'affichage (optionnel)
        
    Returns:
        Liste des régions d'alternatives
    """
    # Calculer le décalage et la largeur des alternatives
    offset = int(np.ceil(marker_height * 2.7))
    alt_width = int(np.ceil(marker_height * 1.4))

    alts_region = []
    
    for c in questionMarks:
        alts = []
        for i in range(len(c)):
            alt = int(np.floor(i / 2)) * n_alternatives
            alts.append(
                [[c[i][0][0] + offset + (alt * alt_width),
                  c[i][0][1]]])

        alts = np.asarray(alts)
        alts_region.append(alts)

    # Dessiner les régions d'alternatives sur l'image
    if img is not None:
        for i, r in enumerate(alts_region):
            drawContours(img, [r], (255, 0, 0), 5)
            c = contour_center(r)
            cv2.putText(img, str(i), c, cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 0, 255), 2)
        # img_show(img, "Alternatives regions", height=950)

    # Définir chaque région d'alternative
    all_alternatives = define_each_alts_region(
        alts_region, n_alternatives, alt_width)
        
    return all_alternatives


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
    FILL_THRESHOLD = 0.60
    
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
            _, thresh_roi = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY_INV)
            
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

def detect_student_number(image):
    """
    Détecte le numéro d'étudiant à partir des cercles remplis dans la partie supérieure.
    
    Args:
        image: Image contenant la zone du numéro étudiant
        
    Returns:
        Numéro d'étudiant détecté (sous forme de chaîne)
    """
    # Convertir en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Appliquer un seuillage pour isoler les marques foncées
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    

    # Détecter les contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print(f"Contours trouvés : {len(contours)}")

    # Afficher les contours détectés
    image_with_contours = image.copy()
    cv2.drawContours(image_with_contours, contours, -1, (0, 255, 0), 3)

    detected_squares = []

    # Identifier les carrés parmi les contours
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)
        
        # Filtrer les contours qui ressemblent à des carrés
        if len(approx) == 4 and 100 < area < 5000: 
            detected_squares.append(approx)

    # print(f"Carreaux détectés : {len(detected_squares)}")

    # Trier les carrés de droite à gauche
    detected_squares = sorted(detected_squares, key=lambda square: -cv2.boundingRect(square)[0])

    # Afficher les carrés détectés
    image_with_squares = image.copy()
    cv2.drawContours(image_with_squares, detected_squares, -1, (0, 0, 255), 2)
    # cv2.imshow("Detected Squares", image_with_squares)
    # cv2.waitKey(0)

    student_number = ""

    # Analyser chaque carré pour trouver les chiffres
    for square in detected_squares:
        # Trier les points du carré par coordonnée X
        square_sorted_by_x = sorted(square, key=lambda point: point[0][0])
        x_min = square_sorted_by_x[0][0][0] 
        x_max = square_sorted_by_x[2][0][0]  
        
        # print(f"x_min: {x_min}, x_max: {x_max}")
        
        # Extraire la zone verticale correspondant au carré
        zone_potentielle = gray[:, x_min:x_max]  
        
        # Dessiner un rectangle vertical pour visualiser la zone
        cv2.rectangle(image_with_squares, (x_min, 0), (x_max, image.shape[0]), (255, 0, 255), 1)

        # Appliquer un seuillage pour isoler les marques
        _, thresh_zone = cv2.threshold(zone_potentielle, 150, 255, cv2.THRESH_BINARY_INV)

        # Détecter les cercles dans cette zone
        circles = cv2.HoughCircles(
            thresh_zone,
            cv2.HOUGH_GRADIENT, 
            dp=1.5,
            minDist=15,
            param1=60,
            param2=18,
            minRadius=7,
            maxRadius=12
        )

        if circles is not None:
            # Convertir les coordonnées des cercles en entiers
            circles = np.round(circles[0, :]).astype("int")
            
            # Trier les cercles selon la coordonnée Y
            circles_sorted_by_y = sorted(circles, key=lambda circle: circle[1])
            
            # Liste pour stocker les cercles avec leur index
            circles_with_index = []
            
            for idx, circle in enumerate(circles_sorted_by_y):
                x, y, r = circle
                
                # Compter les pixels noirs à l'intérieur du cercle
                black_pixels = 0
                for px in range(x - r, x + r + 1):  
                    for py in range(y - r, y + r + 1):  
                        if (px - x) ** 2 + (py - y) ** 2 <= r ** 2:  # Si le point est à l'intérieur du cercle
                            
                            if 0 <= px < thresh.shape[1] and 0 <= py < thresh.shape[0]:  # Vérifier les limites
                                if np.array_equal(thresh[py, px], 0):  # Si le pixel est noir
                                    black_pixels += 1
                
                # Si suffisamment de pixels noirs, considérer le cercle comme rempli
                if black_pixels > 300:
                    cv2.circle(image_with_squares, (x + x_min, y), r, (0, 255, 0), 4)
                    cv2.putText(image_with_squares, f"Index: {idx}", (x + x_min, y - r - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    circles_with_index.append((idx, circle))
                    
                    # Ajouter le chiffre au numéro d'étudiant
                    student_number += str(idx)
                    # print(f"Circle {idx}: Black pixels inside the circle: {black_pixels}")
            
            # Afficher les cercles avec leurs indices
            # cv2.imshow("Circles with Indexes", image_with_squares)
            # cv2.waitKey(0)

        # Afficher les cercles triés avec leurs indices
        # print("Circles sorted by Y axis with their index:")
        # for idx, circle in circles_with_index:
            # print(f"Index: {idx}, Circle: {circle}")
        
        # Inverser le numéro et supprimer les zéros en tête
        student_number_reversed = student_number[::-1].lstrip("0")
        # print(f"Student number (reversed, no leading zeros): {student_number_reversed}")

    return student_number_reversed

        


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

    print(student_results)
    return student_results

        




# -----------------------------------------------------
# SECTION 10: POINT D'ENTRÉE DU PROGRAMME
# -----------------------------------------------------

# Exemple d'utilisation
# if __name__ == "__main__":
#     pdf_path = "C:/Users/admin/Downloads/test2.pdf"
#     process_pdf_for_students(pdf_path)