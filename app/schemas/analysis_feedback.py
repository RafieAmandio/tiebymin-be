import uuid
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AnalysisFeedbackBase(BaseModel):
    user_id: uuid.UUID
    analysis_result_id: uuid.UUID
    feedback_type: str = Field(..., example="accurate")
    feedback_comment: Optional[str] = None
    user_rating: int = Field(..., ge=1, le=5)

class AnalysisFeedbackCreate(AnalysisFeedbackBase):
    pass

class AnalysisFeedback(AnalysisFeedbackBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True