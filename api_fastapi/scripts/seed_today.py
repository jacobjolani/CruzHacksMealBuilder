"""Seed today's menu so /api/menu/today and /api/plan return data. Idempotent for the day."""
import os
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Base, MenuDay, MenuItem

def main():
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    db = Session()
    today = date.today().isoformat()
    menu_day = db.query(MenuDay).filter(MenuDay.date == today).first()
    if menu_day:
        print(f"Menu for {today} already exists, skip seed.")
        return
    menu_day = MenuDay(date=today, scraped_at=datetime.utcnow())
    db.add(menu_day)
    db.flush()
    items = [
        ("Oatmeal", "breakfast", 150, 5, 27, 3),
        ("Eggs", "breakfast", 200, 14, 2, 15),
        ("Salad", "lunch", 300, 12, 20, 18),
        ("Grilled Chicken", "lunch", 400, 35, 0, 22),
        ("Pasta", "dinner", 450, 15, 60, 12),
        ("Salmon", "dinner", 380, 34, 0, 24),
    ]
    for name, period, cal, pro, carb, fat in items:
        db.add(MenuItem(menu_day_id=menu_day.id, name=name, meal_period=period, calories=cal, protein=pro, carbs=carb, fat=fat))
    db.commit()
    print(f"Seeded menu for {today} with {len(items)} items.")

if __name__ == "__main__":
    main()
