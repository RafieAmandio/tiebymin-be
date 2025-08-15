import uuid
from typing import List, Dict
from repositories.user_analysis_result_repository import UserAnalysisResultRepository
from repositories.color_analysis_repository import ColorAnalysisRepository
from repositories.product_color_repository import ProductColorRepository

class ColorRecommendationService:
    def __init__(
        self,
        user_analysis_repo: UserAnalysisResultRepository,
        color_analysis_repo: ColorAnalysisRepository,
        product_color_repo: ProductColorRepository
    ):
        self.user_analysis_repo = user_analysis_repo
        self.color_analysis_repo = color_analysis_repo
        self.product_color_repo = product_color_repo

    def get_recommendations(self, analysis_result_id: uuid.UUID) -> Dict[str, List[str]]:
        analysis_result = self.user_analysis_repo.get_by_id(analysis_result_id)
        
        if not analysis_result or not analysis_result.color_analysis_id:
            return {"color_recommendations": []}

        color_analysis_details = self.color_analysis_repo.get_by_id(analysis_result.color_analysis_id)
        if not color_analysis_details or not color_analysis_details.best_colour:
            return {"color_recommendations": []}

        recommended_hex_codes = {c.lstrip('#').lower() for c in color_analysis_details.best_colour}

        all_product_colors = self.product_color_repo.get_all()

        matching_product_hexes = set()
        for p_color in all_product_colors:
            normalized_product_hex = p_color.hex_color.lstrip('#').lower()
            if normalized_product_hex in recommended_hex_codes:
                matching_product_hexes.add(p_color.hex_color)
        
        return {"color_recommendations": sorted(list(matching_product_hexes))}