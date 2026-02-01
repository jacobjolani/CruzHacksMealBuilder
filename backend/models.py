from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from backend.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal = Column(String(50), nullable=False, index=True)
    target_amount = Column(Float, nullable=False)
    meal_items = Column(JSON, nullable=False)
    total_nutrition = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="meal_plans")

    __table_args__ = (
        # Hot query: "all meal plans for user ordered by created_at desc"
        Index("ix_meal_plans_user_id_created_at", "user_id", "created_at"),
    )


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True)
    food_name = Column(String(200), nullable=False, index=True)
    calories = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    meal_type = Column(String(20), nullable=True, index=True)  # 'brunch' or 'dinner'

