from pydantic import BaseModel
from datetime import date


class SubGoalCompleteRequest(BaseModel):
    completed_on: date | None = None
