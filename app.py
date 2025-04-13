from flask import Flask, render_template, jsonify, request
import json
import random
import os

# Get the path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the templates folder
template_folder = os.path.join(current_dir, 'CruzHacksMealBuilder', 'templates')

app = Flask(__name__, template_folder=template_folder)

# ... rest of your Flask code ...

# Load menu data (from JSON files)
def load_menu(brunch_file, dinner_file):
    with open(brunch_file, 'r') as f_brunch:
        brunch_menu = json.load(f_brunch)
    with open(dinner_file, 'r') as f_dinner:
        dinner_menu = json.load(f_dinner)
    return brunch_menu + dinner_menu

# calculate nutrition
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

# generate meal plan
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
        "total_nutrition": current_nutrition
    }

# Serve the HTML files
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results.html')
def results():
    return render_template('results.html')


# API endpoint for generating meal plans
@app.route('/generate_meal', methods=['POST'])
def generate_meal():
    data = request.get_json()
    goal = data['goal']
    target_amount = float(data['target_amount'])
    menu = load_menu("Cafe3_brunch.json", "Cafe3_dinner.json")
    result = generate_meal_plan(menu, goal, target_amount)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)