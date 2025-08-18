import numpy as np
from PIL import Image
import io
import cv2
import mediapipe as mp
import math
from typing import Dict, Any

class ColorToneService:
    def __init__(self):
        # Keep your original parameter keys but update the palettes to match the function code
        self.SKIN_PALETTE = {
            "Clear Winter": (223, 189, 160),
            "Cool Winter": (211, 170, 150), 
            "Deep Winter": (218, 153, 120),
            "Soft Summer": (228, 183, 162),
            "Light Summer": (209, 170, 138),
            "Cool Summer": (211, 163, 153),
            "Warm Spring": (229, 181, 147),
            "Light Spring": (215, 163, 133),
            "Clear Spring": (206, 159, 145),
            "Warm Autumn": (173, 114, 85),
            "Soft Autumn": (226, 160, 117),
            "Deep Autumn": (141, 92, 68),
        }
        
        self.EYE_PALETTE = {
            "Clear Winter": (90, 97, 97),
            "Cool Winter": (93, 81, 73),
            "Deep Winter": (53, 38, 28),
            "Soft Summer": (127, 113, 107),
            "Light Summer": (96, 102, 105),
            "Cool Summer": (77, 87, 87),
            "Warm Spring": (113, 119, 119),
            "Light Spring": (121, 116, 101),
            "Clear Spring": (79, 79, 74),
            "Warm Autumn": (77, 49, 39),
            "Soft Autumn": (77, 58, 47),
            "Deep Autumn": (42, 32, 26),
        }
        
        self.SEASON_MAP = {
            "Clear Winter": "True Winter",
            "Cool Winter": "Cool Winter", 
            "Deep Winter": "Deep Winter",
            "Soft Summer": "Soft Summer",
            "Light Summer": "Light Summer",
            "Cool Summer": "True Summer",
            "Warm Spring": "Warm Spring",
            "Light Spring": "Light Spring",
            "Clear Spring": "True Spring",
            "Warm Autumn": "True Autumn",
            "Soft Autumn": "Soft Autumn",
            "Deep Autumn": "Deep Autumn",
        }

    def _calculate_distance(self, rgb1, rgb2, scale_factor=0.5):
        """Calculate distance with downscaling like in the function code"""
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        dist = math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
        return dist**scale_factor  # Downscaling applied

    def _extract_colors_from_landmarks(self, image_rgb: np.ndarray) -> tuple:
        """Extract colors using separate left/right processing like the function code"""
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1, 
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        # Convert RGB to BGR for OpenCV processing
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        results = face_mesh.process(image_rgb)
        face_mesh.close()

        if not results.multi_face_landmarks:
            raise ValueError("Wajah tidak terdeteksi dalam gambar.")

        face_landmarks = results.multi_face_landmarks[0]
        image_shape = image_bgr.shape
        
        # Use separate left/right indices like in the function code
        left_cheek_indices = [117, 123, 187, 205, 36, 101, 118]
        right_cheek_indices = [347, 330, 266, 425, 411, 352, 346]
        
        left_eye_indices = [469, 470, 471, 472]
        right_eye_indices = [474, 475, 476, 477]

        # Extract cheek points
        left_cheek_points = []
        for index in left_cheek_indices:
            x = int(face_landmarks.landmark[index].x * image_shape[1])
            y = int(face_landmarks.landmark[index].y * image_shape[0])
            left_cheek_points.append([x, y])
            
        right_cheek_points = []
        for index in right_cheek_indices:
            x = int(face_landmarks.landmark[index].x * image_shape[1])
            y = int(face_landmarks.landmark[index].y * image_shape[0])
            right_cheek_points.append([x, y])

        # Extract eye points
        left_eye_points = []
        for index in left_eye_indices:
            x = int(face_landmarks.landmark[index].x * image_shape[1])
            y = int(face_landmarks.landmark[index].y * image_shape[0])
            left_eye_points.append([x, y])
            
        right_eye_points = []
        for index in right_eye_indices:
            x = int(face_landmarks.landmark[index].x * image_shape[1])
            y = int(face_landmarks.landmark[index].y * image_shape[0])
            right_eye_points.append([x, y])

        # Extract skin color using both cheeks
        mask = np.zeros(image_bgr.shape[:2], dtype=np.uint8)
        if left_cheek_points:
            cv2.fillPoly(mask, [np.array(left_cheek_points)], 255)
        if right_cheek_points:
            cv2.fillPoly(mask, [np.array(right_cheek_points)], 255)
        
        mean_color_bgr = cv2.mean(image_bgr, mask=mask)
        # Convert BGR to RGB
        skin_rgb = tuple([int(x) for x in mean_color_bgr[:3]])[::-1]

        # Extract eye color using both eyes
        mask.fill(0)
        if left_eye_points:
            cv2.fillPoly(mask, [np.array(left_eye_points)], 255)
        if right_eye_points:
            cv2.fillPoly(mask, [np.array(right_eye_points)], 255)
            
        mean_eye_color_bgr = cv2.mean(image_bgr, mask=mask)
        # Convert BGR to RGB
        eye_rgb = tuple([int(x) for x in mean_eye_color_bgr[:3]])[::-1]

        return skin_rgb, eye_rgb

    def _classify_color(self, current_rgb, color_palette):
        """Classify color using only skin color like in the function code"""
        min_d = float('inf')
        closest_category = None

        for category, reference_rgb in color_palette.items():
            distance = self._calculate_distance(current_rgb, reference_rgb)
            if distance < min_d:
                min_d = distance
                closest_category = category

        return closest_category

    def detect(self, image_bytes: bytes) -> Dict[str, Any]:
        try:
            image_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_rgb = np.array(image_pil)
        except Exception as e:
            raise ValueError(f"Gagal membaca gambar. Error: {e}")

        skin_rgb, eye_rgb = self._extract_colors_from_landmarks(image_rgb)

        if not skin_rgb or not eye_rgb:
            raise ValueError("Tidak dapat mengekstrak warna kulit atau mata.")

        # Use only skin color for classification like in the function code
        best_season = self._classify_color(skin_rgb, self.SKIN_PALETTE)
        
        # Map to final category
        final_category = self.SEASON_MAP.get(best_season, "Unknown")

        return {
            "category": final_category,
            "detected_skin_rgb": {"r": skin_rgb[0], "g": skin_rgb[1], "b": skin_rgb[2]},
            "detected_eye_rgb": {"r": eye_rgb[0], "g": eye_rgb[1], "b": eye_rgb[2]}
        }

color_tone_service = ColorToneService()