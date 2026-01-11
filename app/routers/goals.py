from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db import get_db
from utils.dependencies import get_current_user
from models.models import Users
from schemas.goalschema import GoalCreate, SubGoalCreate
from services.goal_service import (
    create_goal,
    create_subgoal,
    get_user_goals,
)

router = APIRouter(prefix="/goals")

@router.post("", status_code=status.HTTP_201_CREATED)
def create_goal_route(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return create_goal(db, current_user, payload)

@router.post("/{goal_id}/subgoals", status_code=status.HTTP_201_CREATED)
def create_subgoal_route(
    goal_id: int,
    payload: SubGoalCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return create_subgoal(db, current_user, goal_id, payload)

@router.get("")
def get_my_goals(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    goals = get_user_goals(db, current_user)
    return [
        {
            "id": g.id,
            "title": g.title,
            "total_days": g.total_days,
            "start_date": g.start_date,
            "current_streak": g.current_streak,
            "longest_streak": g.longest_streak,
            "subgoals": [
                {
                    "id": sg.id,
                    "name": sg.name,
                    "weight": sg.weight,
                }
                for sg in g.subgoals
            ],
        }
        for g in goals
    ]

