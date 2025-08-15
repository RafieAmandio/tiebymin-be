import uuid
from typing import List, Dict, Any
from utils import color_utils
from repositories.user_analysis_result_repository import UserAnalysisResultRepository
from repositories.color_analysis_repository import ColorAnalysisRepository
from repositories.product_color_repository import ProductColorRepository

class TopColorService:
    def __init__(
        self,
        user_analysis_repo: UserAnalysisResultRepository,
        color_analysis_repo: ColorAnalysisRepository,
        product_color_repo: ProductColorRepository
    ):
        self.user_analysis_repo = user_analysis_repo
        self.color_analysis_repo = color_analysis_repo
        self.product_color_repo = product_color_repo

    def get_top_5_colors(self, analysis_result_id: uuid.UUID) -> List[Dict[str, Any]]:
        analysis_result = self.user_analysis_repo.get_by_id(analysis_result_id)
        if not analysis_result or not analysis_result.color_analysis_id:
            return []

        color_analysis_details = self.color_analysis_repo.get_by_id(analysis_result.color_analysis_id)
        if not color_analysis_details or not color_analysis_details.best_colour:
            return []

        recommended_lab_colors = []
        for hex_code in color_analysis_details.best_colour:
            try:
                rgb = color_utils.hex_to_rgb(hex_code)
                recommended_lab_colors.append(color_utils.rgb_to_lab(rgb))
            except (ValueError, IndexError):
                continue
        
        if not recommended_lab_colors:
            return []

        all_product_colors = self.product_color_repo.get_all()
        
        color_distances = []
        for p_color in all_product_colors:
            try:
                product_rgb = color_utils.hex_to_rgb(p_color.hex_color)
                product_lab = color_utils.rgb_to_lab(product_rgb)
                
                # Cari jarak terdekat ke salah satu warna di palet rekomendasi
                min_distance = min(
                    color_utils.calculate_delta_e(product_lab, rec_lab) for rec_lab in recommended_lab_colors
                )
                
                color_info = p_color.dict()
                color_info['distance_score'] = min_distance
                color_distances.append(color_info)
            except (ValueError, IndexError):
                continue

        # Urutkan berdasarkan jarak terdekat (ascending) dan ambil 5 teratas
        sorted_colors = sorted(color_distances, key=lambda c: c['distance_score'])
        
        return sorted_colors[:5]