from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time

# URL of the Berkeley dining menu page
url = "https://dining.berkeley.edu/menus/"

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()

# Open the URL in the browser
driver.get(url)

# List to store the results (menu items and their nutritional information)
results = []

# Find all menu items on the page using the class name "recip"
menu_items = driver.find_elements(By.CLASS_NAME, "recip")

# Loop through the menu items (redundant loop, can be optimized)
for i in range(len(driver.find_elements(By.CLASS_NAME, "recip"))):
    item = driver.find_elements(By.CLASS_NAME, "recip")[i]

# Iterate over each menu item to extract information
for item in menu_items:
    try:
        # Extract the name of the food item
        food_name = item.text.strip()

        # Scroll to the menu item to make it visible
        driver.execute_script("arguments[0].scrollIntoView(true);", item)

        # Wait until the menu item is visible
        WebDriverWait(driver, 10).until(EC.visibility_of(item))

        # Click on the menu item to open the popup
        ActionChains(driver).move_to_element(item).pause(0.5).click().perform()
        print(f"Clicked: {food_name}")

        # Wait for the popup to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.cald-popup-wrapper.show"))
        )

        # Locate the popup element
        popup = driver.find_element(By.CSS_SELECTOR, "div.cald-popup-wrapper.show")

        # Locate the section containing the recipe details
        details = popup.find_element(By.CLASS_NAME, "recipe-details-wrap")

        # Find all list items (li) within the recipe details
        li_elements = details.find_elements(By.TAG_NAME, "li")

        # Initialize default values for nutritional information
        calories = fat = carbs = protein = "N/A"

        # Loop through the list items to extract nutritional information
        for li in li_elements:
            text = li.text.strip()
            if "Calories" in text:
                calories = text.split(":")[-1].strip()
            elif "Fat" in text and "Total" in text:
                fat = text.split(":")[-1].strip()
            elif "Carbohydrate" in text:
                carbs = text.split(":")[-1].strip()
            elif "Protein" in text:
                protein = text.split(":")[-1].strip()

        # Print the extracted nutritional information for debugging
        print(f"{food_name} → Calories: {calories}, Fat: {fat}, Carbs: {carbs}, Protein: {protein}")

        # Wait for the close button in the popup to appear
        close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.cald-close"))
        )

        # Scroll to the close button and click it to close the popup
        driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", close_button)
        time.sleep(0.5)

        # Append the extracted information to the results list
        results.append({
            "food_name": food_name,
            "calories": calories,
            "fat": fat,
            "carbs": carbs,
            "protein": protein
        })

    except Exception as e:
        # Print an error message if something goes wrong
        print(f"Error processing {item.text.strip()}: {e}")
        continue

# Save the results to a JSON file
with open("menu_data.json", "w") as f:
    json.dump(results, f, indent=2)

# Close the browser
driver.quit()
