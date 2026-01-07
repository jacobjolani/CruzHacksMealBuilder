import pytest
from app import app, db
from models import User, MenuItem

@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def authenticated_user(client):
    """Create and login a test user."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        
        # Login
        client.post('/login',
                   json={'username': 'testuser', 'password': 'testpass123'},
                   content_type='application/json')
        return user

@pytest.fixture
def sample_menu_items(client):
    """Create sample menu items for testing."""
    with app.app_context():
        items = [
            MenuItem(food_name='Test Food 1', calories=200, fat=10, carbs=20, protein=15, meal_type='brunch'),
            MenuItem(food_name='Test Food 2', calories=300, fat=15, carbs=30, protein=20, meal_type='dinner'),
        ]
        for item in items:
            db.session.add(item)
        db.session.commit()
        return items

def test_generate_meal_requires_auth(client):
    """Test that meal generation requires authentication."""
    response = client.post('/generate_meal',
                         json={'goal': 'protein', 'target_amount': 50},
                         content_type='application/json')
    assert response.status_code == 401

def test_generate_meal_success(client, authenticated_user, sample_menu_items):
    """Test successful meal plan generation."""
    response = client.post('/generate_meal',
                         json={'goal': 'protein', 'target_amount': 20},
                         content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'meal_plan' in data
    assert 'total_nutrition' in data

def test_get_meal_plans_requires_auth(client):
    """Test that getting meal plans requires authentication."""
    response = client.get('/api/meal_plans')
    assert response.status_code == 401

def test_get_meal_plans_success(client, authenticated_user):
    """Test getting user's meal plans."""
    response = client.get('/api/meal_plans')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_get_user_info_requires_auth(client):
    """Test that getting user info requires authentication."""
    response = client.get('/api/user')
    assert response.status_code == 401

def test_get_user_info_success(client, authenticated_user):
    """Test getting current user info."""
    response = client.get('/api/user')
    assert response.status_code == 200
    data = response.get_json()
    assert 'username' in data
    assert 'email' in data


