import numpy as np
from PIL import Image
import io
import cv2
import mediapipe as mp
import math
from typing import Dict, Any
import random

class ColorToneService:
    def __init__(self):
        self.SKIN_PALETTE = {
            "Clear Winter": (223, 189, 160), "Cool Winter": (211, 170, 150), "Deep Winter": (218, 153, 120),
            "Soft Summer": (228, 183, 162), "Light Summer": (209, 170, 138), "Cool Summer": (211, 163, 153),
            "Warm Spring": (229, 181, 147), "Light Spring": (215, 163, 133), "Clear Spring": (206, 159, 145),
            "Warm Autumn": (173, 114, 85), "Soft Autumn": (226, 160, 117), "Deep Autumn": (141, 92, 68),
        }
        self.EYE_PALETTE = {
            "Clear Winter": (90, 97, 97), "Cool Winter": (93, 81, 73), "Deep Winter": (53, 38, 28),
            "Soft Summer": (127, 113, 107), "Light Summer": (96, 102, 105), "Cool Summer": (77, 87, 87),
            "Warm Spring": (113, 119, 119), "Light Spring": (121, 116, 101), "Clear Spring": (79, 79, 74),
            "Warm Autumn": (77, 49, 39), "Soft Autumn": (77, 58, 47), "Deep Autumn": (42, 32, 26),
        }
        self.SEASON_MAP = {
            "Clear Winter": "True Winter", "Cool Winter": "Cool Winter", "Deep Winter": "Deep Winter",
            "Soft Summer": "Soft Summer", "Light Summer": "Light Summer", "Cool Summer": "True Summer",
            "Warm Spring": "Warm Spring", "Light Spring": "Light Spring", "Clear Spring": "True Spring",
            "Warm Autumn": "True Autumn", "Soft Autumn": "Soft Autumn", "Deep Autumn": "Deep Autumn",
        }

    def _calculate_distance(self, rgb1, rgb2):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

    def _extract_colors_from_landmarks(self, image_rgb: np.ndarray) -> tuple:
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5
        )
        results = face_mesh.process(image_rgb)
        face_mesh.close()

        if not results.multi_face_landmarks:
            raise ValueError("Wajah tidak terdeteksi dalam gambar.")

        face_landmarks = results.multi_face_landmarks[0]
        image_shape = image_rgb.shape
        
        cheek_indices = [117, 123, 187, 205, 36, 101, 118, 347, 330, 266, 425, 411, 352, 346]
        iris_indices = [469, 470, 471, 472, 474, 475, 476, 477]

        cheek_points = np.array([
            [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
            for i in cheek_indices
        ])
        
        iris_points = np.array([
            [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
            for i in iris_indices
        ])

        mask = np.zeros(image_shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [cheek_points], 255)
        mean_skin_color_bgr = cv2.mean(image_rgb, mask=mask)
        skin_rgb = (int(mean_skin_color_bgr[2]), int(mean_skin_color_bgr[1]), int(mean_skin_color_bgr[0]))

        mask.fill(0)
        cv2.fillPoly(mask, [iris_points], 255)
        mean_eye_color_bgr = cv2.mean(image_rgb, mask=mask)
        eye_rgb = (int(mean_eye_color_bgr[2]), int(mean_eye_color_bgr[1]), int(mean_eye_color_bgr[0]))

        return skin_rgb, eye_rgb

    def detect(self, image_bytes: bytes) -> Dict[str, Any]:
        try:
            image_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_rgb = np.array(image_pil)
        except Exception as e:
            raise ValueError(f"Gagal membaca gambar. Error: {e}")

        skin_rgb, eye_rgb = self._extract_colors_from_landmarks(image_rgb)

        if not skin_rgb or not eye_rgb:
            raise ValueError("Tidak dapat mengekstrak warna kulit atau mata.")
        
        # --- PERUBAHAN UNTUK DEMO ---
        # Logika analisis asli di-nonaktifkan sementara
        """
        min_combined_distance = float('inf')
        best_season = None
        skin_weight = 0.7
        eye_weight = 0.3

        for season, ref_skin_rgb in self.SKIN_PALETTE.items():
            ref_eye_rgb = self.EYE_PALETTE.get(season)
            if not ref_eye_rgb: continue

            skin_dist = self._calculate_distance(skin_rgb, ref_skin_rgb)
            eye_dist = self._calculate_distance(eye_rgb, ref_eye_rgb)
            combined_distance = (skin_dist * skin_weight) + (eye_dist * eye_weight)

            if combined_distance < min_combined_distance:
                min_combined_distance = combined_distance
                best_season = season
        
        final_category = self.SEASON_MAP.get(best_season, "Unknown")
        """

        # Logika baru untuk memilih kategori secara acak
        possible_seasons = list(self.SEASON_MAP.values())
        final_category = random.choice(possible_seasons)
        # --- AKHIR PERUBAHAN ---

        return {
            "category": final_category,
            "detected_skin_rgb": {"r": skin_rgb[0], "g": skin_rgb[1], "b": skin_rgb[2]},
            "detected_eye_rgb": {"r": eye_rgb[0], "g": eye_rgb[1], "b": eye_rgb[2]}
        }

color_tone_service = ColorToneService()