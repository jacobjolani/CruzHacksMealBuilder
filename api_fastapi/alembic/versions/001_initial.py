"""initial schema with indexes

Revision ID: 001
Revises:
Create Date: 2025-02-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "menu_days",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("date", sa.String(10), nullable=False),
        sa.Column("source_url", sa.String(512), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_menu_days_date", "menu_days", ["date"], unique=True)

    op.create_table(
        "menu_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("menu_day_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("meal_period", sa.String(32), nullable=False),
        sa.Column("calories", sa.Float(), nullable=False),
        sa.Column("protein", sa.Float(), nullable=False),
        sa.Column("carbs", sa.Float(), nullable=False),
        sa.Column("fat", sa.Float(), nullable=False),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["menu_day_id"], ["menu_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_menu_items_menu_day_id", "menu_items", ["menu_day_id"])
    op.create_index("ix_menu_items_name", "menu_items", ["name"])
    op.create_index("ix_menu_items_meal_period", "menu_items", ["meal_period"])
    op.create_index("ix_menu_items_menu_day_period", "menu_items", ["menu_day_id", "meal_period"])

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(128), nullable=False),
        sa.Column("daily_calories", sa.Float(), nullable=True),
        sa.Column("daily_protein", sa.Float(), nullable=True),
        sa.Column("daily_carbs", sa.Float(), nullable=True),
        sa.Column("daily_fat", sa.Float(), nullable=True),
        sa.Column("preferences", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_profiles_session_id", "user_profiles", ["session_id"], unique=True)
    op.create_index("ix_user_profiles_session_updated", "user_profiles", ["session_id", "updated_at"])

    op.create_table(
        "meal_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("menu_day_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("totals_calories", sa.Float(), nullable=False),
        sa.Column("totals_protein", sa.Float(), nullable=False),
        sa.Column("totals_carbs", sa.Float(), nullable=False),
        sa.Column("totals_fat", sa.Float(), nullable=False),
        sa.Column("meals", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["menu_day_id"], ["menu_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meal_plans_menu_day_id", "meal_plans", ["menu_day_id"])
    op.create_index("ix_meal_plans_session_id", "meal_plans", ["session_id"])
    op.create_index("ix_meal_plans_session_created", "meal_plans", ["session_id", "created_at"])


def downgrade() -> None:
    op.drop_table("meal_plans")
    op.drop_table("user_profiles")
    op.drop_table("menu_items")
    op.drop_table("menu_days")
