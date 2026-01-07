from app import app, db
from models import User, MenuItem, MealPlan
import json
import os

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if menu items already exist
        if MenuItem.query.count() > 0:
            print("Menu items already exist in database. Skipping initialization.")
            return
        
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load menu items from JSON files into database
        brunch_path = os.path.join(current_dir, 'Cafe3_brunch.json')
        dinner_path = os.path.join(current_dir, 'Cafe3_dinner.json')
        
        try:
            with open(brunch_path, 'r') as f:
                brunch_items = json.load(f)
            
            with open(dinner_path, 'r') as f:
                dinner_items = json.load(f)
            
            # Add brunch items
            for item in brunch_items:
                menu_item = MenuItem(
                    food_name=item['food_name'],
                    calories=float(item['calories']),
                    fat=float(item['fat']),
                    carbs=float(item['carbs']),
                    protein=float(item['protein']),
                    meal_type='brunch'
                )
                db.session.add(menu_item)
            
            # Add dinner items
            for item in dinner_items:
                menu_item = MenuItem(
                    food_name=item['food_name'],
                    calories=float(item['calories']),
                    fat=float(item['fat']),
                    carbs=float(item['carbs']),
                    protein=float(item['protein']),
                    meal_type='dinner'
                )
                db.session.add(menu_item)
            
            db.session.commit()
            print(f"Database initialized successfully! Added {len(brunch_items)} brunch items and {len(dinner_items)} dinner items.")
        except FileNotFoundError as e:
            print(f"Error: Could not find JSON files. {e}")
        except Exception as e:
            print(f"Error initializing database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_database()

