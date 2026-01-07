import pytest
from app import app, db
from models import User

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
def test_user(client):
    """Create a test user."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        return user

def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/register', 
                          json={'username': 'newuser', 'email': 'newuser@example.com', 'password': 'password123'},
                          content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Registration successful'

def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username."""
    response = client.post('/register',
                          json={'username': 'testuser', 'email': 'different@example.com', 'password': 'password123'},
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post('/login',
                          json={'username': 'testuser', 'password': 'testpass123'},
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Login successful'

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/login',
                          json={'username': 'nonexistent', 'password': 'wrongpass'},
                          content_type='application/json')
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data

def test_logout_requires_auth(client):
    """Test that logout requires authentication."""
    response = client.post('/logout')
    assert response.status_code == 401


