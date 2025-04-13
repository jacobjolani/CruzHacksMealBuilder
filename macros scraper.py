from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time

url = "https://dining.berkeley.edu/menus/"
driver = webdriver.Chrome()
driver.get(url)

menu_items = driver.find_elements(By.CLASS_NAME, "recip")

for i in range(len(menu_items)):
    item = driver.find_elements(By.CLASS_NAME, "recip")[i]

for item in menu_items:
    try:
        food_name = item.text.strip()

        driver.execute_script("arguments[0].scrollIntoView(true);", item)
        WebDriverWait(driver, 10).until(EC.visibility_of(item))
        ActionChains(driver).move_to_element(item).pause(0.5).click().perform()
        print(f"Clicked: {food_name}")

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.cald-popup-wrapper.show"))
        )

        popup = driver.find_element(By.CSS_SELECTOR, "div.cald-popup-wrapper.show")
        details = popup.find_element(By.CLASS_NAME, "recipe-details-wrap")

        li_elements = details.find_elements(By.TAG_NAME, "li")

        calories = fat = carbs = protein = "N/A"
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


        print(f"{food_name} → Calories: {calories}, Fat: {fat}, Carbs: {carbs}, Protein: {protein}")

        close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.cald-close"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", close_button)
        time.sleep(0.5)


    except Exception as e:
        print(f"Error processing {item.text.strip()}: {e}")
        continue

input("Press Enter to exit")
driver.quit()