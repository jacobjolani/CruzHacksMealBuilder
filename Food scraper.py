from bs4 import BeautifulSoup
import requests
import json
from selenium import webdriver

def main():
    url = "https://dining.berkeley.edu/menus/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    exists = set()
    menu = []

    for li in soup.find_all("li", class_="recip"):
        spans = li.find_all("span", recursive=False)
        if spans:
            food = spans[0].get_text(strip=True)
            if food not in exists:
                exists.add(food)
                menu.append(food)


    with open("berkeley_menu.json", "w") as f:
        json.dump(menu, f, indent=2)
    
if __name__ == "__main__":
    main()
