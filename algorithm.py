import requests
from bs4 import BeautifulSoup

def get_menu():
    """Fetches and parses the Berkeley Dining menu."""
    url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

    soup = BeautifulSoup(response.content, "html.parser")
    menu_sections = soup.find_all("div", class_="meal-menu")
    all_menu_items = []

    for section in menu_sections:
        meal_name = section.find("h2").text.strip()
        items = section.find_all("div", class_="menu-item")
        for item in items:
            item_name = item.find("div", class_="item-name").text.strip()
            nutrition_div = item.find("div", class_="nutrition-info")
            nutrition_data = {"calories": 0, "carbs": 0, "protein": 0, "fat": 0}

            if nutrition_div:
                lines = nutrition_div.text.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("Calories:"):
                        match = line.split("Calories: ")[1].split()[0]
                        if match.isdigit():
                            nutrition_data["calories"] = int(match)
                    elif line.startswith("Carbs:"):
                        match = line.split("Carbs: ")[1].split("g")[0]
                        if match.isdigit():
                            nutrition_data["carbs"] = int(match)
                    elif line.startswith("Protein:"):
                        match = line.split("Protein: ")[1].split("g")[0]
                        if match.isdigit():
                            nutrition_data["protein"] = int(match)
                    elif line.startswith("Fat:"):
                        match = line.split("Fat: ")[1].split("g")[0]
                        if match.isdigit():
                            nutrition_data["fat"] = int(match)

            all_menu_items.append({"name": item_name, "nutrition": nutrition_data, "meal": meal_name})

    return all_menu_items

def recommend_meals(menu, goal, calories_goal=0, protein_goal=0, fat_goal=0, carbs_goal=0):
    """Recommends meals based on the user's goal and macro limits."""
    filtered_meals = []
    total_carbs = 0
    total_protein = 0
    total_fat = 0
    total_calories = 0

    filtered_meals = [
        item
        for item in menu
        if (
            (calories_goal == 0 or item["nutrition"]["calories"] <= calories_goal)
            and (protein_goal == 0 or item["nutrition"]["protein"] <= protein_goal)
            and (fat_goal == 0 or item["nutrition"]["fat"] <= fat_goal)
            and (carbs_goal == 0 or item["nutrition"]["carbs"] <= carbs_goal)
        )
    ]

    if "carbs" in goal.lower():
        filtered_meals.sort(key=lambda x: x["nutrition"]["carbs"], reverse=True)
    elif "protein" in goal.lower():
        filtered_meals.sort(key=lambda x: x["nutrition"]["protein"], reverse=True)
    elif "fat" in goal.lower():
        filtered_meals.sort(key=lambda x: x["nutrition"]["fat"], reverse=True)
    elif "calories" in goal.lower():
        filtered_meals.sort(key=lambda x: x["nutrition"]["calories"], reverse=True)

    selected_meals = []
    max_meals = 5

    for i in range(min(max_meals, len(filtered_meals))):
        meal = filtered_meals[i]
        total_carbs += meal["nutrition"]["carbs"]
        total_protein += meal["nutrition"]["protein"]
        total_fat += meal["nutrition"]["fat"]
        total_calories += meal["nutrition"]["calories"]
        selected_meals.append(meal)

    return {"meals": selected_meals, "totals": {"carbs": total_carbs, "protein": total_protein, "fat": total_fat, "calories": total_calories}}

def generate_meal_plan(goal, calories_goal=0, protein_goal=0, fat_goal=0, carbs_goal=0):
    """Generates and prints the meal plan."""
    menu = get_menu()
    meal_plan = recommend_meals(menu, goal, calories_goal, protein_goal, fat_goal, carbs_goal)

    print("Recommended Meal Plan:")
    if not meal_plan["meals"]:
        print("No meals found matching your goal.")
        return

    for meal in meal_plan["meals"]:
        print(
            f"{meal['name']} ({meal['meal']}) - Carbs: {meal['nutrition']['carbs']}g, "
            f"Protein: {meal['nutrition']['protein']}g, Fat: {meal['nutrition']['fat']}g, "
            f"Calories: {meal['nutrition']['calories']}cal"
        )
    print(
        f"Total: Carbs: {meal_plan['totals']['carbs']}g, Protein: {meal_plan['totals']['protein']}g, "
        f"Fat: {meal_plan['totals']['fat']}g, Calories: {meal_plan['totals']['calories']}cal"
    )

if __name__ == "__main__":
    goal = input("Enter your macro goal (e.g., eat more carbs): ")
    calories_goal = int(input("Max Calories (or 0 for no limit): ") or 0)
    protein_goal = int(input("Max Protein (g) (or 0 for no limit): ") or 0)
    fat_goal = int(input("Max Fat (g) (or 0 for no limit): ") or 0)
    carbs_goal = int(input("Max Carbs (g) (or 0 for no limit): ") or 0)

    generate_meal_plan(goal, calories_goal, protein_goal, fat_goal, carbs_goal)