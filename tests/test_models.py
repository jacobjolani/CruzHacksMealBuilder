import pytest
from app import app, db
from models import User, MealPlan, MenuItem

@pytest.fixture
def app_context():
    """Create app context for testing."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield
        db.drop_all()

def test_user_creation(app_context):
    """Test user model creation."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    assert user.id is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')

def test_meal_plan_creation(app_context):
    """Test meal plan model creation."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    meal_plan = MealPlan(
        user_id=user.id,
        goal='protein',
        target_amount=50.0,
        meal_items=[{'food_name': 'Test Food'}],
        total_nutrition={'protein': 50, 'calories': 200}
    )
    db.session.add(meal_plan)
    db.session.commit()
    
    assert meal_plan.id is not None
    assert meal_plan.user_id == user.id
    assert meal_plan.goal == 'protein'
    assert len(meal_plan.meal_items) == 1

def test_menu_item_creation(app_context):
    """Test menu item model creation."""
    item = MenuItem(
        food_name='Test Food',
        calories=200.0,
        fat=10.0,
        carbs=20.0,
        protein=15.0,
        meal_type='brunch'
    )
    db.session.add(item)
    db.session.commit()
    
    assert item.id is not None
    assert item.food_name == 'Test Food'
    assert item.calories == 200.0


