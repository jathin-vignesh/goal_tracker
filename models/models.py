"""
Database ORM models for the Goal Progress Tracking application.

Includes:
- Users (password + SSO)
- User authentication providers (Google, Microsoft, etc.)
- Goals
- Sub-goals with weightage
- Daily sub-goal completion (streak & progress source of truth)
"""

# pylint: disable=too-few-public-methods,not-callable

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Boolean,
    Float,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship

from db import Base

class Users(Base):
    """User accounts (password-based and/or SSO)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=True)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )

    auth_providers = relationship(
        "UserAuthProviders",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    goals = relationship(
        "Goals",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class UserAuthProviders(Base):
    """Maps users to external authentication providers (SSO)."""

    __tablename__ = "user_auth_providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider = Column(String(50), nullable=False)  # google, microsoft
    provider_user_id = Column(String(255), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uix_provider_identity",
        ),
        UniqueConstraint(
            "user_id",
            "provider",
            name="uix_user_provider",
        ),
    )

    user = relationship("Users", back_populates="auth_providers")

class Goals(Base):
    """Goals created by users."""

    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(String(255), nullable=False)
    total_days = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)

    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint("total_days > 0", name="chk_goal_total_days"),
    )

    user = relationship("Users", back_populates="goals")

    subgoals = relationship(
        "SubGoals",
        back_populates="goal",
        cascade="all, delete-orphan",
    )

class SubGoals(Base):
    """Sub-goals belonging to a goal, with relative weightage."""

    __tablename__ = "subgoals"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(
        Integer,
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(String(255), nullable=False)
    weight = Column(Float, nullable=False, default=1.0)

    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "goal_id",
            "name",
            name="uix_goal_subgoal_name",
        ),
        CheckConstraint("weight > 0", name="chk_subgoal_weight"),
    )

    goal = relationship("Goals", back_populates="subgoals")

    daily_completions = relationship(
        "SubGoalDailyCompletion",
        back_populates="subgoal",
        cascade="all, delete-orphan",
    )

class SubGoalDailyCompletion(Base):
    """Tracks daily completion of sub-goals (source of truth)."""

    __tablename__ = "subgoal_daily_completion"

    id = Column(Integer, primary_key=True, index=True)
    subgoal_id = Column(
        Integer,
        ForeignKey("subgoals.id", ondelete="CASCADE"),
        nullable=False,
    )

    completed_on = Column(Date, nullable=False)
    completed = Column(Boolean, nullable=False, default=True)
    completed_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "subgoal_id",
            "completed_on",
            name="uix_subgoal_completed_day",
        ),
    )

    subgoal = relationship("SubGoals", back_populates="daily_completions")
