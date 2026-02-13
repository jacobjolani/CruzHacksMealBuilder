from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class MenuDay(Base):
    __tablename__ = "menu_days"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), unique=True, nullable=False, index=True)
    source_url = Column(String(512), nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    menu_items = relationship("MenuItem", back_populates="menu_day", cascade="all, delete-orphan")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_day_id = Column(Integer, ForeignKey("menu_days.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(256), nullable=False, index=True)
    meal_period = Column(String(32), nullable=False, index=True)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    tags = Column(Text, nullable=True)

    menu_day = relationship("MenuDay", back_populates="menu_items")

    __table_args__ = (
        Index("ix_menu_items_menu_day_period", "menu_day_id", "meal_period"),
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    daily_calories = Column(Float, nullable=True)
    daily_protein = Column(Float, nullable=True)
    daily_carbs = Column(Float, nullable=True)
    daily_fat = Column(Float, nullable=True)
    preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_user_profiles_session_updated", "session_id", "updated_at"),
    )


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_day_id = Column(Integer, ForeignKey("menu_days.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(128), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    totals_calories = Column(Float, nullable=False)
    totals_protein = Column(Float, nullable=False)
    totals_carbs = Column(Float, nullable=False)
    totals_fat = Column(Float, nullable=False)
    meals = Column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_meal_plans_session_created", "session_id", "created_at"),
    )
