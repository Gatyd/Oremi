import cv2
import numpy as np
import pytesseract
import re
from datetime import datetime
from PIL import Image
import io

# Configuration Tesseract pour Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Importation de PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
    print("PaddleOCR disponible et importé avec succès")
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("PaddleOCR non disponible, utilisation de Tesseract uniquement")

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from django.core.files.uploadedfile import InMemoryUploadedFile

class CarteGriseExtractorView(APIView):
    """
    API View pour extraire les informations d'une carte grise
    Accepte uniquement les requêtes multipart/form-data
    """
    parser_classes = (MultiPartParser,)
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        try:
            # Uniquement multipart/form-data
            if 'image' not in request.FILES:
                return Response({
                    'error': 'Aucune image fournie',
                    'message': 'Veuillez envoyer une image avec la clé "image" en multipart/form-data'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['image']
            
            # Validation du fichier d'image
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
            if image_file.content_type not in allowed_types:
                return Response({
                    'error': 'Type de fichier non supporté',
                    'allowed_types': allowed_types,
                    'received_type': image_file.content_type
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Taille maximum de 10MB
            if image_file.size > 10 * 1024 * 1024:
                return Response({
                    'error': 'Fichier trop volumineux',
                    'max_size': '10MB',
                    'received_size': f'{image_file.size / (1024*1024):.1f}MB'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Lire et traiter l'image
            if image_file.content_type == 'application/pdf':
                # Pour les PDF, prendre la première page
                import fitz  # PyMuPDF
                pdf_data = image_file.read()
                doc = fitz.open(stream=pdf_data, filetype="pdf")
                page = doc[0]
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                image = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
            else:
                # Lire l'image directement
                image_data = image_file.read()
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return Response({
                    'error': 'Impossible de décoder l\'image',
                    'message': 'Vérifiez que le fichier est une image valide'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Redimensionner si trop volumineux
            image = self._resize_if_too_large(image)
            
            # Préprocessing intelligent
            processed_image = self._preprocess_image(image)
            
            # Extraction du texte
            extracted_text = self._extract_text_with_ocr(processed_image)
            
            # Parsing des informations
            parsed_data = self._extract_information_from_text(extracted_text)
            
            return Response(parsed_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Erreur lors de l'extraction: {str(e)}")
            return Response({
                'error': 'Erreur interne lors de l\'extraction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _resize_if_too_large(self, image):
        """Redimensionner l'image si elle est trop volumineuse pour optimiser les performances"""
        height, width = image.shape[:2]
        max_dimension = 2000  # Dimension maximale recommandée
        
        if max(height, width) > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))
            
            print(f"📏 Redimensionnement: {width}x{height} → {new_width}x{new_height}")
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return resized
        
        return image

    def _needs_preprocessing(self, image):
        """Détermine si l'image a besoin de prétraitement"""
        # Convertir en niveaux de gris pour analyse
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Calculer des métriques de qualité
        # 1. Contraste (écart-type des pixels)
        contrast = np.std(gray)
        
        # 2. Netteté (variance du Laplacien)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 3. Histogramme pour détecter le bruit
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        # Pic unique = bonne qualité, distribution étalée = bruit
        hist_entropy = -np.sum(hist * np.log2(hist + 1e-7)) / len(hist)
        
        print(f"📊 Métriques qualité - Contraste: {contrast:.2f}, Netteté: {laplacian_var:.2f}, Entropie: {hist_entropy:.2f}")
        
        # Critères pour décider si prétraitement nécessaire
        needs_preprocessing = False
        
        # Image floue (faible variance Laplacien)
        if laplacian_var < 50:
            print("🔍 Image détectée comme floue - prétraitement activé")
            needs_preprocessing = True
            
        # Contraste faible  
        elif contrast < 30:
            print("🔍 Contraste faible détecté - prétraitement activé")
            needs_preprocessing = True
            
        # Beaucoup de bruit (entropie élevée)
        elif hist_entropy > 7:
            print("🔍 Bruit important détecté - prétraitement activé") 
            needs_preprocessing = True
        else:
            print("✨ Image de bonne qualité - prétraitement DÉSACTIVÉ")
            
        return False

    def _preprocess_image_light(self, image):
        """Prétraitement léger pour images de bonne qualité"""
        # Conversion en niveaux de gris uniquement
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Redimensionnement si trop petit seulement
        height, width = gray.shape
        if height < 400:  # Seuil plus bas
            scale = 400 / height
            new_width = int(width * scale)
            gray = cv2.resize(gray, (new_width, 400), interpolation=cv2.INTER_CUBIC)
            print(f"📏 Redimensionnement léger: {width}x{height} → {new_width}x400")
        
        return gray

    def _preprocess_image_aggressive(self, image):
        """Prétraitement agressif pour images de mauvaise qualité"""
        print("🔧 Prétraitement agressif activé")
        
        # Conversion en niveaux de gris
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Redimensionnement pour améliorer la résolution
        height, width = gray.shape
        if height < 600:
            scale = 600 / height
            new_width = int(width * scale)
            gray = cv2.resize(gray, (new_width, 600), interpolation=cv2.INTER_CUBIC)

        # Détection et correction d'inclinaison
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None and len(lines) > 0:
            angles = []
            for line in lines[:10]:
                rho, theta = line[0]
                angle = (theta * 180 / np.pi) - 90
                angles.append(angle)
            
            mean_angle = np.mean(angles)
            if abs(mean_angle) > 1:
                center = (gray.shape[1] // 2, gray.shape[0] // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, mean_angle, 1.0)
                gray = cv2.warpAffine(gray, rotation_matrix, (gray.shape[1], gray.shape[0]), 
                                    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        # Amélioration du contraste avec CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Débruitage
        denoised = cv2.medianBlur(gray, 3)
        
        # Amélioration de la netteté
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(
            sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return binary

    def _preprocess_image(self, image):
        """Préprocessing intelligent de l'image"""
        
        # Détecter si l'image a besoin de prétraitement
        if self._needs_preprocessing(image):
            return self._preprocess_image_aggressive(image)
        else:
            return self._preprocess_image_light(image)
    
    def _extract_text_with_ocr(self, image):
        """Extraire le texte de l'image avec PaddleOCR (priorité) ou Tesseract"""
        
        # Essayer d'abord PaddleOCR si disponible
        if PADDLEOCR_AVAILABLE:
            try:
                print("Tentative d'extraction avec PaddleOCR...")
                return self._extract_with_paddleocr(image)
            except Exception as e:
                print(f"Échec PaddleOCR: {str(e)}. Basculement vers Tesseract...")
        
        # Utiliser Tesseract en fallback ou si PaddleOCR n'est pas disponible
        print("Utilisation de Tesseract...")
        return self._extract_with_tesseract(image)
    
    def _extract_with_paddleocr(self, image):
        """Extraire le texte avec PaddleOCR"""
        try:
            # Initialiser PaddleOCR (essayer d'abord en anglais qui a des modèles disponibles)
            ocr = PaddleOCR(use_angle_cls=True, lang='en')  # utilise les modèles anglais
            
            # Convertir l'image OpenCV en format PIL puis en numpy array si nécessaire
            if isinstance(image, np.ndarray):
                # Convertir BGR (OpenCV) vers RGB (PaddleOCR)
                if len(image.shape) == 3 and image.shape[2] == 3:
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    image_rgb = image
            else:
                image_rgb = np.array(image)
            
            # Extraction OCR
            result = ocr.ocr(image_rgb, cls=True)
            
            # Concaténer tout le texte extrait
            extracted_text = ""
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text = line[1][0]  # Le texte extrait
                        confidence = line[1][1]  # La confiance
                        
                        # Filtrer les résultats avec une confiance trop faible
                        if confidence > 0.5:  # Seuil de confiance
                            extracted_text += text + " "
            
            if extracted_text.strip():
                print(f"PaddleOCR - Succès: {len(extracted_text.strip())} caractères extraits")
                cleaned_text = self._clean_extracted_text(extracted_text)
                return cleaned_text
            else:
                raise ValueError("Aucun texte extrait avec PaddleOCR")
                
        except Exception as e:
            raise ValueError(f"Erreur PaddleOCR: {str(e)}")

    def _extract_with_tesseract(self, image):
        """Extraire le texte avec Tesseract (méthode de fallback)"""
        
        # Configurations à essayer (par ordre de préférence)
        # PSM 6: uniform block of text
        # PSM 4: single column of text of variable sizes
        # PSM 3: fully automatic page segmentation
        configs_to_try = [
            r'--oem 3 --psm 6 -l fra',  # Français d'abord, block uniforme
            r'--oem 3 --psm 4 -l fra',  # Français, colonne simple
            r'--oem 3 --psm 3 -l fra',  # Français, segmentation automatique
            r'--oem 3 --psm 6 -l eng',  # Anglais en fallback, block uniforme
            r'--oem 3 --psm 4 -l eng',  # Anglais, colonne simple
            r'--oem 3 --psm 6',         # Sans spécification de langue
        ]
        
        best_text = ""
        best_length = 0
        last_error = None        
        for config in configs_to_try:
            try:
                print(f"Tentative OCR avec config: {config}")
                text = pytesseract.image_to_string(image, config=config)
                
                # Vérifier si du texte a été extrait et sa qualité
                if text.strip():
                    text_length = len(text.strip())
                    print(f"Succès avec config: {config} - {text_length} caractères extraits")
                    
                    # Garder le meilleur résultat (plus de texte généralement = mieux)
                    if text_length > best_length:
                        best_text = text
                        best_length = text_length
                    
                    # Si on a un résultat français ou très long, on s'arrête là
                    if 'fra' in config or text_length > 500:
                        cleaned_text = self._clean_extracted_text(text)
                        return cleaned_text
                    
            except Exception as e:
                print(f"Échec avec config {config}: {str(e)}")
                last_error = e
                continue
        
        # Si on a au moins un texte extrait, utiliser le meilleur
        if best_text:
            print(f"Utilisation du meilleur résultat: {best_length} caractères")
            cleaned_text = self._clean_extracted_text(best_text)
            return cleaned_text
        
        # Si toutes les configurations ont échoué
        raise ValueError(f"Erreur OCR - Toutes les configurations ont échoué. Dernière erreur: {str(last_error)}")
    
    def _clean_extracted_text(self, text):
        """Nettoyer le texte extrait"""
        
        # Supprimer les caractères indésirables
        text = re.sub(r'[^\w\s\-\.\/\(\):,]', ' ', text)
        
        # Normaliser les espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les espaces en début et fin
        text = text.strip()
        
        return text
    
    def _extract_information_from_text(self, text):
        """
        Extraire les informations de la carte grise optimisée
        Recherche avec et sans point pour gérer les variations d'OCR
        """
        parsed_data = {
            'numero_immatriculation': None,    # A - Numéro d'immatriculation
            'marque_vehicule': None,          # D.1 - Marque du véhicule
            'modele_vehicule': None,          # D.2 - Modèle du véhicule
            'cylindree': None,                # P.1 - Cylindrée
            'numero_chassis': None,           # E - Numéro de châssis
            'date_mise_circulation': None,    # B - Date de mise en circulation
            'nombre_places': None,            # S.1 - Nombre de places assises
            'carburation': None,              # P.3 - Carburation
        }
        
        found_count = 0
        
        # A - Numéro d'immatriculation (pas de point dans le code A)
        immat_patterns = [
            r'A[:\s]*([A-Z]{2}[-\s]?\d{3}[-\s]?[A-Z]{2})',  # Avec préfixe A
            r'([A-Z]{2}[-\s]?\d{3}[-\s]?[A-Z]{2})',  # Nouveau format AA-123-AA
            r'(\d{1,4}[-\s]?[A-Z]{1,3}[-\s]?\d{2})',  # Ancien format 1234-AA-12
        ]
        
        for pattern in immat_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed_data['numero_immatriculation'] = match.group(1).replace(' ', '-').upper()
                found_count += 1
                break

        # D.1 - Marque du véhicule (avec et sans point)
        marque_patterns = [
            r'D\.1[:\s]*([A-Z][A-Z\s]*)',  # Avec point D.1
            r'D1[:\s]*([A-Z][A-Z\s]*)',    # Sans point D1
            r'(RENAULT|PEUGEOT|CITROEN|VOLKSWAGEN|BMW|MERCEDES|AUDI|FORD|OPEL|NISSAN|TOYOTA|HONDA|FIAT|SEAT|SKODA|DACIA|KIA|HYUNDAI|MAZDA|MITSUBISHI|SUBARU|VOLVO|LEXUS|INFINITI|ACURA)',
        ]
        
        for pattern in marque_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed_data['marque_vehicule'] = match.group(1).strip().upper()
                found_count += 1
                break

        # D.2 - Modèle/Type du véhicule (avec et sans point)
        type_patterns = [
            r'D\.2[:\s]*([A-Z0-9][A-Z0-9\s\-]*)',  # Avec point D.2
            r'D2[:\s]*([A-Z0-9][A-Z0-9\s\-]*)',    # Sans point D2
            r'(YARIS|CLIO|POLO|GOLF|A3|C3|208|308|FOCUS|FIESTA|CORSA|ASTRA|CIVIC|ACCORD|PASSAT|JETTA|TIGUAN|QASHQAI|X3|A4|C4|3008|5008)',  # Modèles courants
        ]
        
        for pattern in type_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed_data['modele_vehicule'] = match.group(1).strip().upper()
                found_count += 1
                break

        # P.1 - Cylindrée (avec et sans point)
        cylindree_patterns = [
            r'P\.1[:\s]*(\d{3,5})',  # Avec point P.1
            r'P1[:\s]*(\d{3,5})',    # Sans point P1
            r'(\d{4})\s*cm³?',       # Format 1234 cm³
            r'(\d{4})\s*CC',         # Format 1234 CC
        ]
        
        for pattern in cylindree_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed_data['cylindree'] = f"{match.group(1)} cm³"
                found_count += 1
                break

        # E - Numéro de châssis (VIN - 17 caractères alphanumériques)
        vin_patterns = [
            r'E[:\s]*([A-HJ-NPR-Z0-9]{17})',  # Avec préfixe E
            r'VIN[:\s]*([A-HJ-NPR-Z0-9]{17})',  # Avec préfixe VIN
            r'([A-HJ-NPR-Z0-9]{17})',  # Pattern général 17 caractères
        ]
        
        for pattern in vin_patterns:
            matches = re.findall(pattern, text)
            for vin in matches:
                if len(vin) == 17:  # VIN doit faire exactement 17 caractères
                    parsed_data['numero_chassis'] = vin
                    found_count += 1
                    break
            if parsed_data['numero_chassis']:
                break        # B - Date de mise en circulation (prioriser la date qui suit B.)
        date_patterns = [
            r'B\.?\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})',  # Avec préfixe B. ou B suivi de date
            r'B\s+(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})',     # B suivi d'espace puis date
            # En dernier recours, première date trouvée (pas la dernière)
            r'(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})',         # Première date rencontrée
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Prendre la PREMIÈRE date trouvée (pas la dernière comme avant)
                date_str = matches[0].replace(' ', '/').replace('-', '/').replace('.', '/')
                parsed_data['date_mise_circulation'] = date_str
                found_count += 1
                break

        # S.1 - Nombre de places assises (avec et sans point)
        places_patterns = [
            r'S\.1[:\s]*(\d{1,2})',     # Avec point S.1
            r'S1[:\s]*(\d{1,2})',       # Sans point S1
            r'PLACES[:\s]*(\d{1,2})',   # Avec mot PLACES
            r'(\d{1,2})\s*PLACES',      # Format inverse
        ]
        
        for pattern in places_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                places = int(match.group(1))
                if 1 <= places <= 50:  # Vérification logique
                    parsed_data['nombre_places'] = str(places)
                    found_count += 1
                    break

        # P.3 - Carburation/Type de carburant (avec et sans point)
        carburant_patterns = [
            r'P\.3[:\s]*([A-Z]+)',  # Avec point P.3
            r'P3[:\s]*([A-Z]+)',    # Sans point P3
            r'(ESSENCE|DIESEL|ELECTRIQUE|HYBRIDE|GPL|GNV|ETHANOL)',  # Types courants
        ]
        
        for pattern in carburant_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed_data['carburation'] = match.group(1).strip().upper()
                found_count += 1
                break

        # Évaluer le niveau de confiance basé sur les 8 informations demandées
        if found_count >= 6:
            parsed_data['extraction_confidence'] = 'high'
        elif found_count >= 3:
            parsed_data['extraction_confidence'] = 'medium'
        elif found_count >= 1:
            parsed_data['extraction_confidence'] = 'low'
        else:
            # Aucune information trouvée
            return {
                'error': 'Aucune information de carte grise détectée dans l\'image',
                'suggestion': 'Vérifiez que l\'image est une carte grise française et qu\'elle est lisible',
                'extracted_text_sample': text[:200] + '...' if len(text) > 200 else text
            }

        # Ajouter le texte extrait pour debug (limité à 500 caractères)
        # parsed_data['text'] = text[:500] + '...' if len(text) > 500 else text
        
        return parsed_data
