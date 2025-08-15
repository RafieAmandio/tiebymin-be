import uuid
from typing import List, Dict, Any
from collections import defaultdict
from utils import color_utils

from repositories.user_analysis_result_repository import UserAnalysisResultRepository
from repositories.product_repository import ProductRepository
from repositories.product_color_repository import ProductColorRepository
from repositories.color_analysis_repository import ColorAnalysisRepository
from repositories.product_face_shape_compatibility_repository import ProductFaceShapeCompatibilityRepository
from repositories.product_body_shape_compatibility_repository import ProductBodyShapeCompatibilityRepository
from repositories.product_bmi_compatibility_repository import ProductBmiCompatibilityRepository

class ProductRecommendationService:
    def __init__(
        self,
        user_analysis_repo: UserAnalysisResultRepository,
        product_repo: ProductRepository,
        product_color_repo: ProductColorRepository,
        color_analysis_repo: ColorAnalysisRepository,
        face_shape_compat_repo: ProductFaceShapeCompatibilityRepository,
        body_shape_compat_repo: ProductBodyShapeCompatibilityRepository,
        bmi_compat_repo: ProductBmiCompatibilityRepository
    ):
        self.user_analysis_repo = user_analysis_repo
        self.product_repo = product_repo
        self.product_color_repo = product_color_repo
        self.color_analysis_repo = color_analysis_repo
        self.face_shape_compat_repo = face_shape_compat_repo
        self.body_shape_compat_repo = body_shape_compat_repo
        self.bmi_compat_repo = bmi_compat_repo

    def get_recommendations(self, analysis_result_id: uuid.UUID) -> Dict[str, List[Dict[str, Any]]]:
        analysis_result = self.user_analysis_repo.get_by_id(analysis_result_id)
        if not analysis_result:
            return {"hijab": [], "clothes": []}

        color_analysis_details = self.color_analysis_repo.get_by_id(analysis_result.color_analysis_id)
        recommended_lab_colors = []
        if color_analysis_details and color_analysis_details.best_colour:
            for hex_code in color_analysis_details.best_colour:
                try:
                    rgb = color_utils.hex_to_rgb(hex_code)
                    recommended_lab_colors.append(color_utils.rgb_to_lab(rgb))
                except (ValueError, IndexError):
                    continue
        
        all_products = self.product_repo.get_all()
        all_product_colors = self.product_color_repo.get_all()
        face_compat_data = self.face_shape_compat_repo.get_all()
        body_compat_data = self.body_shape_compat_repo.get_all()
        bmi_compat_data = self.bmi_compat_repo.get_all()
        
        face_scores = {(item.product_id, item.face_shape_id): item.compatibility_score for item in face_compat_data}
        body_scores = {(item.product_id, item.body_shape_id): item.compatibility_score for item in body_compat_data}
        bmi_scores = {(item.product_id, item.bmi_category_id): item.compatibility_score for item in bmi_compat_data}

        product_colors_map = defaultdict(list)
        for color in all_product_colors:
            product_colors_map[color.product_id].append(color)

        ranked_hijabs = []
        ranked_clothes = []

        for product in all_products:
            product_dict = product.dict()
            product_available_colors = product_colors_map.get(product.id, [])
            
            product_color_distances = []
            if recommended_lab_colors and product_available_colors:
                for p_color in product_available_colors:
                    try:
                        product_rgb = color_utils.hex_to_rgb(p_color.hex_color)
                        product_lab = color_utils.rgb_to_lab(product_rgb)
                        min_distance = min(color_utils.calculate_delta_e(product_lab, rec_lab) for rec_lab in recommended_lab_colors)
                        product_color_distances.append({"hex": p_color.hex_color, "distance": min_distance})
                    except (ValueError, IndexError):
                        continue
            
            sorted_product_colors = sorted(product_color_distances, key=lambda c: c['distance'])
            top_5_colors = [color['hex'] for color in sorted_product_colors[:5]]
            product_dict['color_recommendations'] = top_5_colors

            if product.category.lower() == 'hijab':
                total_score = face_scores.get((product.id, analysis_result.face_shape_id), 0)
                if total_score > 0 and top_5_colors:
                    product_dict['total_compatibility_score'] = total_score
                    ranked_hijabs.append(product_dict)
            
            elif product.category.lower() == 'clothes':
                score1 = body_scores.get((product.id, analysis_result.body_shape_id), 0)
                score2 = bmi_scores.get((product.id, analysis_result.bmi_category_id), 0)
                total_score = score1 + score2
                if total_score > 0:
                    product_dict['total_compatibility_score'] = total_score
                    ranked_clothes.append(product_dict)
        
        sorted_hijabs = sorted(ranked_hijabs, key=lambda p: p['total_compatibility_score'], reverse=True)
        sorted_clothes = sorted(ranked_clothes, key=lambda p: p['total_compatibility_score'], reverse=True)

        return {
            "hijab": sorted_hijabs[:3],
            "clothes": sorted_clothes[:3]
        }