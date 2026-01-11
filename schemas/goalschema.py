from pydantic import BaseModel, Field
from datetime import date
from typing import List


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    total_days: int = Field(gt=0)
    start_date: date


class SubGoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    weight: float = Field(default=1.0, gt=0)


class GoalResponse(BaseModel):
    id: int
    title: str
    total_days: int
    start_date: date
    current_streak: int
    longest_streak: int

    class Config:
        from_attributes = True


class SubGoalResponse(BaseModel):
    id: int
    name: str
    weight: float

    class Config:
        from_attributes = True
