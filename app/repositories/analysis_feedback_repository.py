import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel
from schemas.analysis_feedback import AnalysisFeedback, AnalysisFeedbackCreate
from db.supabase_db import supabase

class AnalysisFeedbackRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[AnalysisFeedback]:
        pass

    @abstractmethod
    def get_by_id(self, feedback_id: uuid.UUID) -> Optional[AnalysisFeedback]:
        pass

    @abstractmethod
    def create(self, feedback_data: AnalysisFeedbackCreate) -> AnalysisFeedback:
        pass

    @abstractmethod
    def update(self, feedback_id: uuid.UUID, feedback_data: AnalysisFeedbackCreate) -> Optional[AnalysisFeedback]:
        pass

    @abstractmethod
    def delete(self, feedback_id: uuid.UUID) -> bool:
        pass

class SupabaseAnalysisFeedbackRepository(AnalysisFeedbackRepository):
    TABLE_NAME = "analysis_feedback"

    def _prepare_data(self, pydantic_model: BaseModel) -> dict:
        data_dict = pydantic_model.dict(exclude_none=True)
        for key, value in data_dict.items():
            if isinstance(value, uuid.UUID):
                data_dict[key] = str(value)
        return data_dict

    def get_all(self) -> List[AnalysisFeedback]:
        response = supabase.table(self.TABLE_NAME).select("*").order("created_at", desc=True).execute()
        return [AnalysisFeedback(**item) for item in response.data] if response.data else []

    def get_by_id(self, feedback_id: uuid.UUID) -> Optional[AnalysisFeedback]:
        response = supabase.table(self.TABLE_NAME).select("*").eq("id", str(feedback_id)).execute()
        return AnalysisFeedback(**response.data[0]) if response.data else None

    def create(self, feedback_data: AnalysisFeedbackCreate) -> AnalysisFeedback:
        data_to_insert = self._prepare_data(feedback_data)
        response = supabase.table(self.TABLE_NAME).insert(data_to_insert).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create analysis feedback.")
        return AnalysisFeedback(**response.data[0])

    def update(self, feedback_id: uuid.UUID, feedback_data: AnalysisFeedbackCreate) -> Optional[AnalysisFeedback]:
        data_to_update = self._prepare_data(feedback_data)
        response = supabase.table(self.TABLE_NAME).update(data_to_update).eq("id", str(feedback_id)).execute()
        return AnalysisFeedback(**response.data[0]) if response.data else None

    def delete(self, feedback_id: uuid.UUID) -> bool:
        response = supabase.table(self.TABLE_NAME).delete().eq("id", str(feedback_id)).execute()
        return bool(response.data)