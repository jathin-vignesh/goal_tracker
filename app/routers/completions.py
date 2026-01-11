from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from utils.dependencies import get_current_user
from models.models import Users
from schemas.completionschema import SubGoalCompleteRequest
from services.completion_service import complete_subgoal

router = APIRouter(prefix="/subgoals")

@router.post("/{subgoal_id}/complete")
def complete_subgoal_route(
    subgoal_id: int,
    payload: SubGoalCompleteRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return complete_subgoal(
        db,
        current_user,
        subgoal_id,
        payload.completed_on,
    )
