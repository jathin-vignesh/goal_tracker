from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.models import Goals, SubGoals, Users
from sqlalchemy.exc import IntegrityError

def create_goal(db: Session, user: Users, payload):
    goal = Goals(
        user_id=user.id,
        title=payload.title,
        total_days=payload.total_days,
        start_date=payload.start_date,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def create_subgoal(db: Session, user: Users, goal_id: int, payload):
    goal = (
        db.query(Goals)
        .filter(Goals.id == goal_id, Goals.user_id == user.id)
        .first()
    )

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )

    subgoal = SubGoals(
        goal_id=goal.id,
        name=payload.name,
        weight=payload.weight,
    )

    db.add(subgoal)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sub-goal with this name already exists for this goal"
        )

    db.refresh(subgoal)
    return subgoal


def get_user_goals(db: Session, user: Users):
    return (
        db.query(Goals)
        .filter(Goals.user_id == user.id)
        .all()
    )
