import json
import random

def load_menu(brunch_file, dinner_file):
    """Loads the menu data from JSON files."""
    with open(brunch_file, 'r') as f_brunch:
        brunch_menu = json.load(f_brunch)
    with open(dinner_file, 'r') as f_dinner:
        dinner_menu = json.load(f_dinner)
    return brunch_menu + dinner_menu

def calculate_nutrition(meal_items):
    """Calculates the total nutrition for a list of meal items."""
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

def generate_meal_plan(menu, goal, target_amount):
    """Generates a meal plan based on the user's goal and target amount."""
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

def main(goal, target_amount, brunch_file="Cafe3_brunch.json", dinner_file="Cafe3_dinner.json"):
    """Main function to generate and print the meal plan."""
    menu = load_menu(brunch_file, dinner_file)
    result = generate_meal_plan(menu, goal, target_amount)

    if isinstance(result, str):
        print(result)
    else:
        print("Recommended Meal Plan:")
        for item in result["meal_plan"]:
            print(f"- {item}")
        print("\nTotal Nutrition:")
        print(f"Calories: {result['total_nutrition']['calories']}g")
        print(f"Fat: {result['total_nutrition']['fat']}g")
        print(f"Carbs: {result['total_nutrition']['carbs']}g")
        print(f"Protein: {result['total_nutrition']['protein']}g")

if __name__ == "__main__":
    goal = input("Enter your nutritional goal (carbs, protein, fat, or calories): ")
    target_amount = float(input(f"Enter the target amount of {goal} (in grams or kcal): "))
    main(goal, target_amount)