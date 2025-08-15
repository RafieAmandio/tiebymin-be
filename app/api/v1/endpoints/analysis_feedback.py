from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from schemas.analysis_feedback import AnalysisFeedback, AnalysisFeedbackCreate
from repositories.analysis_feedback_repository import AnalysisFeedbackRepository
from dependencies.dependencies import get_analysis_feedback_repository

router = APIRouter(prefix="/analysis-feedback", tags=["Analysis Feedback"])

@router.post("/", response_model=AnalysisFeedback, status_code=status.HTTP_201_CREATED)
def create_analysis_feedback(
    feedback_data: AnalysisFeedbackCreate,
    repo: AnalysisFeedbackRepository = Depends(get_analysis_feedback_repository)
):
    return repo.create(feedback_data)

@router.get("/", response_model=List[AnalysisFeedback])
def get_all_analysis_feedbacks(
    repo: AnalysisFeedbackRepository = Depends(get_analysis_feedback_repository)
):
    return repo.get_all()

@router.get("/{feedback_id}", response_model=AnalysisFeedback)
def get_analysis_feedback_by_id(
    feedback_id: uuid.UUID,
    repo: AnalysisFeedbackRepository = Depends(get_analysis_feedback_repository)
):
    db_feedback = repo.get_by_id(feedback_id)
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Analysis feedback not found")
    return db_feedback

@router.put("/{feedback_id}", response_model=AnalysisFeedback)
def update_analysis_feedback(
    feedback_id: uuid.UUID,
    feedback_data: AnalysisFeedbackCreate,
    repo: AnalysisFeedbackRepository = Depends(get_analysis_feedback_repository)
):
    updated_feedback = repo.update(feedback_id, feedback_data)
    if updated_feedback is None:
        raise HTTPException(status_code=404, detail="Analysis feedback not found")
    return updated_feedback

@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis_feedback(
    feedback_id: uuid.UUID,
    repo: AnalysisFeedbackRepository = Depends(get_analysis_feedback_repository)
):
    if not repo.delete(feedback_id):
        raise HTTPException(status_code=404, detail="Analysis feedback not found")
    return