from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from functools import wraps
import json
import random
import os
import hashlib
import time
import logging
from logging.handlers import RotatingFileHandler
from models import db, User, MealPlan, MenuItem
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, InternalServerError

# Get the path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the templates folder
template_folder = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_folder)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///meal_planner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Logging configuration
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/meal_planner.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Meal Planner startup')

# Simple in-memory cache (can be replaced with Redis)
cache = {}
CACHE_TTL = 300  # 5 minutes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Cache decorator
def cached(timeout=CACHE_TTL):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = hashlib.md5(
                f"{f.__name__}_{str(args)}_{str(kwargs)}".encode()
            ).hexdigest()
            
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < timeout:
                    return cached_data
            
            result = f(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            return result
        return decorated_function
    return decorator

# Load menu data with caching
@cached(timeout=3600)  # Cache for 1 hour
def load_menu_from_db():
    """Load menu from database instead of JSON files"""
    items = MenuItem.query.all()
    return [{
        'food_name': item.food_name,
        'calories': item.calories,
        'fat': item.fat,
        'carbs': item.carbs,
        'protein': item.protein
    } for item in items]

def load_menu(brunch_file, dinner_file):
    """Load menu with fallback to JSON files if database is empty"""
    try:
        menu = load_menu_from_db()
        if menu:
            return menu
    except Exception as e:
        print(f"Error loading from database: {e}")
    
    # Fallback to JSON files
    brunch_path = os.path.join(current_dir, brunch_file)
    dinner_path = os.path.join(current_dir, dinner_file)
    
    with open(brunch_path, 'r') as f_brunch:
        brunch_menu = json.load(f_brunch)
    with open(dinner_path, 'r') as f_dinner:
        dinner_menu = json.load(f_dinner)
    return brunch_menu + dinner_menu

# Calculate nutrition
def calculate_nutrition(meal_items):
    total_calories = 0
    total_fat = 0
    total_carbs = 0
    total_protein = 0

    for item in meal_items:
        total_calories += float(item.get('calories', 0))
        total_fat += float(item.get('fat', 0))
        total_carbs += float(item.get('carbs', 0))
        total_protein += float(item.get('protein', 0))

    return {
        'calories': total_calories,
        'fat': total_fat,
        'carbs': total_carbs,
        'protein': total_protein,
    }

# Generate meal plan with caching
@cached(timeout=300)
def generate_meal_plan(menu, goal, target_amount):
    goal = goal.lower()
    possible_meals = []

    for item in menu:
        if goal in ["carbs", "carbohydrates"] and float(item.get('carbs', 0)) > 0:
            possible_meals.append(item)
        elif goal in ["protein"] and float(item.get('protein', 0)) > 0:
            possible_meals.append(item)
        elif goal in ["fat", "fats"] and float(item.get('fat', 0)) > 0:
            possible_meals.append(item)
        elif goal in ["calories", "calories"] and float(item.get('calories', 0)) > 0:
            possible_meals.append(item)

    if not possible_meals:
        return "No suitable meals found for your goal."

    meal_plan = []
    current_nutrition = {'calories': 0, 'fat': 0, 'carbs': 0, 'protein': 0}
    num_items = 0

    while True:
        chosen_meal = random.choice(possible_meals)
        meal_plan.append(chosen_meal)
        current_nutrition = calculate_nutrition(meal_plan)
        num_items += 1

        if goal in ["carbs", "carbohydrates"] and abs(current_nutrition['carbs'] - target_amount) <= 10:
            break
        elif goal in ["protein"] and abs(current_nutrition['protein'] - target_amount) <= 10:
            break
        elif goal in ["fat", "fats"] and abs(current_nutrition['fat'] - target_amount) <= 10:
            break
        elif goal in ["calories", "calories"] and abs(current_nutrition['calories'] - target_amount) <= 50:
            break

        if num_items >= 4:
            break

    meal_plan_details = []
    for item in meal_plan:
        meal_plan_details.append(f"{item['food_name']} (Calories: {item['calories']}g, Fat: {item['fat']}g, Carbs: {item['carbs']}g, Protein: {item['protein']}g)")

    return {
        "meal_plan": meal_plan_details,
        "total_nutrition": current_nutrition,
        "meal_items": meal_plan
    }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results.html')
@login_required
def results():
    return render_template('Results.html')

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Server Error: {error}')
    return jsonify({'error': 'Internal server error', 'message': 'An error occurred'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'message': str(e.description)}), 429

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        app.logger.error(f'Database health check failed: {e}')
        db_status = 'unhealthy'
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'database': db_status,
        'cache': 'healthy',
        'timestamp': time.time()
    }), 200 if db_status == 'healthy' else 503

# API Documentation endpoint
@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation endpoint."""
    docs = {
        'title': 'Meal Planner API',
        'version': '1.0.0',
        'endpoints': {
            'POST /register': {
                'description': 'Register a new user',
                'parameters': {
                    'username': 'string (required)',
                    'email': 'string (required)',
                    'password': 'string (required)'
                },
                'response': 'User object with id'
            },
            'POST /login': {
                'description': 'Login user',
                'parameters': {
                    'username': 'string (required)',
                    'password': 'string (required)'
                },
                'response': 'User object with id'
            },
            'POST /logout': {
                'description': 'Logout user',
                'authentication': 'Required',
                'response': 'Success message'
            },
            'GET /api/user': {
                'description': 'Get current user info',
                'authentication': 'Required',
                'response': 'User object'
            },
            'POST /generate_meal': {
                'description': 'Generate a meal plan',
                'authentication': 'Required',
                'parameters': {
                    'goal': 'string (protein, carbs, fat, calories)',
                    'target_amount': 'float (required)'
                },
                'response': 'Meal plan object'
            },
            'GET /api/meal_plans': {
                'description': 'Get user meal plan history',
                'authentication': 'Required',
                'response': 'Array of meal plan objects'
            },
            'GET /health': {
                'description': 'Health check endpoint',
                'response': 'System status'
            }
        }
    }
    return jsonify(docs)

# Authentication routes
@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Input validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': 'Username must be between 3 and 20 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if '@' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        app.logger.info(f'New user registered: {username}')
        login_user(user)
        return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201
    except Exception as e:
        app.logger.error(f'Registration error: {e}')
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500

@app.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            app.logger.info(f'User logged in: {username}')
            return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
        
        app.logger.warning(f'Failed login attempt for username: {username}')
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        app.logger.error(f'Login error: {e}')
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
    })

# API endpoint for generating meal plans
@app.route('/generate_meal', methods=['POST'])
@login_required
@limiter.limit("20 per hour")
def generate_meal():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        goal = data.get('goal', '').strip().lower()
        target_amount = data.get('target_amount')
        
        # Input validation
        if not goal or not target_amount:
            return jsonify({'error': 'Goal and target_amount are required'}), 400
        
        valid_goals = ['protein', 'carbs', 'carbohydrates', 'fat', 'fats', 'calories']
        if goal not in valid_goals:
            return jsonify({'error': f'Invalid goal. Must be one of: {", ".join(valid_goals)}'}), 400
        
        try:
            target_amount = float(target_amount)
            if target_amount <= 0:
                return jsonify({'error': 'Target amount must be positive'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Target amount must be a number'}), 400
        
        menu = load_menu("Cafe3_brunch.json", "Cafe3_dinner.json")
        result = generate_meal_plan(menu, goal, target_amount)
        
        # Save meal plan to database
        if isinstance(result, dict):
            meal_plan = MealPlan(
                user_id=current_user.id,
                goal=goal,
                target_amount=target_amount,
                meal_items=result.get('meal_items', []),
                total_nutrition=result.get('total_nutrition', {})
            )
            db.session.add(meal_plan)
            db.session.commit()
            app.logger.info(f'Meal plan generated for user {current_user.id}')
        
        return jsonify(result)
    except Exception as e:
        app.logger.error(f'Meal generation error: {e}')
        db.session.rollback()
        return jsonify({'error': 'Failed to generate meal plan', 'message': str(e)}), 500

@app.route('/api/meal_plans', methods=['GET'])
@login_required
def get_meal_plans():
    plans = MealPlan.query.filter_by(user_id=current_user.id).order_by(MealPlan.created_at.desc()).all()
    return jsonify([{
        'id': plan.id,
        'goal': plan.goal,
        'target_amount': plan.target_amount,
        'total_nutrition': plan.total_nutrition,
        'created_at': plan.created_at.isoformat()
    } for plan in plans])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
