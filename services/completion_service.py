from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.models import SubGoals, SubGoalDailyCompletion, Users


def complete_subgoal(
    db: Session,
    user: Users,
    subgoal_id: int,
    completed_on: date | None,
):
    subgoal = (
        db.query(SubGoals)
        .join(SubGoals.goal)
        .filter(
            SubGoals.id == subgoal_id,
            SubGoals.goal.has(user_id=user.id),
        )
        .first()
    )

    if not subgoal:
        raise HTTPException(status_code=404, detail="Sub-goal not found")

    day = completed_on or date.today()

    existing = (
        db.query(SubGoalDailyCompletion)
        .filter(
            SubGoalDailyCompletion.subgoal_id == subgoal.id,
            SubGoalDailyCompletion.completed_on == day,
        )
        .first()
    )

    if existing:
        return {"message": "Already completed for this day"}

    completion = SubGoalDailyCompletion(
        subgoal_id=subgoal.id,
        completed_on=day,
    )
    db.add(completion)
    db.commit()

    return {"message": "Sub-goal marked as completed"}
