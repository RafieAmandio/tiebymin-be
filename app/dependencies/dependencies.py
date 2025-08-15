import os
from typing import Type, Optional
from sqlalchemy.orm import Session
from db.postgres_db import SessionLocal

from repositories.bmi_repository import SupabaseBMIRepository, PostgresBMIRepository
from repositories.body_shape_repository import SupabaseBodyShapeRepository
from repositories.face_shape_repository import SupabaseFaceShapeRepository
from repositories.color_analysis_repository import SupabaseColorAnalysisRepository
from repositories.product_repository import SupabaseProductRepository
from repositories.celebrity_repository import SupabaseCelebrityRepository
from repositories.product_bmi_compatibility_repository import SupabaseProductBmiCompatibilityRepository
from repositories.product_color_analysis_compatibility_repository import SupabaseProductColorAnalysisCompatibilityRepository
from repositories.product_face_shape_compatibility_repository import SupabaseProductFaceShapeCompatibilityRepository
from repositories.product_color_repository import SupabaseProductColorRepository
# from repositories.analysis_session_repository import SupabaseAnalysisSessionRepository
from repositories.user_analysis_result_repository import SupabaseUserAnalysisResultRepository
from repositories.user_photo_repository import SupabaseUserPhotoRepository
from repositories.user_repository import SupabaseUserRepository
from repositories.product_body_shape_compatibility_repository import SupabaseProductBodyShapeCompatibilityRepository
from repositories.analysis_feedback_repository import SupabaseAnalysisFeedbackRepository

def create_repository_provider(
    supabase_repo_class: Type,
    postgres_repo_class: Optional[Type] = None
):
    def get_repository():
        db_type = os.getenv("DB_TYPE", "supabase")
        if db_type == "postgres":
            if not postgres_repo_class:
                raise NotImplementedError(f"PostgreSQL not implemented for {supabase_repo_class.__name__}")
            db: Session = SessionLocal()
            return postgres_repo_class(db_session=db)
        return supabase_repo_class()
    return get_repository

get_bmi_repository = create_repository_provider(
    supabase_repo_class=SupabaseBMIRepository,
    postgres_repo_class=PostgresBMIRepository
)

get_body_shape_repository = create_repository_provider(
    supabase_repo_class=SupabaseBodyShapeRepository
)

get_face_shape_repository = create_repository_provider(
    supabase_repo_class=SupabaseFaceShapeRepository
)

get_color_analysis_repository = create_repository_provider(
    supabase_repo_class=SupabaseColorAnalysisRepository
)

get_product_repository = create_repository_provider(
    supabase_repo_class=SupabaseProductRepository
)

get_celebrity_repository = create_repository_provider(
    supabase_repo_class=SupabaseCelebrityRepository
)

get_product_bmi_compatibility_repository = create_repository_provider(
    supabase_repo_class=SupabaseProductBmiCompatibilityRepository
)

get_product_color_analysis_compatibility_repository = create_repository_provider(
    supabase_repo_class=SupabaseProductColorAnalysisCompatibilityRepository
)

get_product_face_shape_compatibility_repository = create_repository_provider(
    supabase_repo_class=SupabaseProductFaceShapeCompatibilityRepository
)

get_product_color_repository = create_repository_provider(
    supabase_repo_class=SupabaseProductColorRepository
)

get_user_analysis_result_repository = create_repository_provider(
    supabase_repo_class=SupabaseUserAnalysisResultRepository
)

get_user_photo_repository = create_repository_provider(
    supabase_repo_class=SupabaseUserPhotoRepository
)

get_user_repository = create_repository_provider(
    supabase_repo_class=SupabaseUserRepository
)

get_product_body_shape_compatibility_repository = create_repository_provider(
    supabase_repo_class=SupabaseProductBodyShapeCompatibilityRepository
)

get_analysis_feedback_repository = create_repository_provider(
    supabase_repo_class=SupabaseAnalysisFeedbackRepository
)