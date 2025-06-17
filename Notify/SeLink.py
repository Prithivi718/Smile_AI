from os import getenv, path
from dotenv import load_dotenv
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# -------------------------- MODULE 1: Setup --------------------------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time, json, re

from bs4 import BeautifulSoup

#-------------------------- MODULE 1: Chrome Driver Setup --------------------------
def get_driver():
    options = Options()
    options.add_argument("--headless=new")  # Run in background
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # If needed: options.add_argument("--user-data-dir=C:/Users/intel/AppData/Local/Google/Chrome/User Data")

    service = Service(executable_path="C:\\Users\\intel\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
    chrome_driver = webdriver.Chrome(service=service, options=options)
    return chrome_driver

# -------------------------- MODULE 2: Manual Login with Credentials --------------------------

load_dotenv()

cookies_path= "E:\\Prithivi CSE\\Agent 101 Intern\\Smiley_AI\\Notify\\cookies.json" # Cookies Path
def manual_login_credentials(chrome_driver):

    chrome_driver.get("https://www.linkedin.com/login")
    time.sleep(3)  # Wait for page to load

    user_email = getenv("USER_EMAIL_1")
    user_password = getenv("EMAIL_PASSWORD_1")

    # 🛑 Fixing incorrect selectors: use 'id' not CSS selector like "username"
    username = chrome_driver.find_element(By.ID, "username")
    password = chrome_driver.find_element(By.ID, "password")

    username.send_keys(user_email)
    password.send_keys(user_password)


    # Submit login form
    chrome_driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)  # Allow time for redirection


from selenium.common.exceptions import WebDriverException

# SMART Login Handler
def smart_login(chrome_driver, cookie_file= cookies_path):
    chrome_driver.get("https://www.linkedin.com/")
    time.sleep(3)

    # If cookies file exists, try to load and check login status
    if path.exists(cookie_file):
        print("🔍 Trying login with cookies...")
        try:
            load_cookies(chrome_driver, cookie_file)
            chrome_driver.refresh()
            time.sleep(3)

            # Check for successful login (example: presence of "Me" profile icon)
            if "feed" in chrome_driver.current_url:
                print("✅ Logged in using cookies.")
                return

            # If still not in feed/home, cookies might be invalid
            print("⚠️ Cookies expired or invalid, switching to manual login...")

        except WebDriverException as e:
            print("❌ Error using cookies:", e)

    # Fallback to manual login
    print("🔐 Logging in manually...")
    manual_login_credentials(chrome_driver)
    time.sleep(5)

    # Save cookies for future logins
    save_cookies(chrome_driver, cookie_file)
    print("💾 Cookies saved for future logins.")


# -------------------------- MODULE 3: Save and Load Cookies --------------------------


def save_cookies(chrome_driver, filename= cookies_path):
    with open(filename, 'w') as f:
        json.dump(chrome_driver.get_cookies(), f)

def load_cookies(chrome_driver, filename= cookies_path):
    with open(filename, 'r') as f:
        cookies = json.load(f)
    for cookie in cookies:
        chrome_driver.add_cookie(cookie)


# -------------------------- MODULE 4: Navigate to Notifications --------------------------

def scrape_with_selenium_and_bs4(chrome_driver):
    chrome_driver.get("https://www.linkedin.com/notifications/?filter=all")
    time.sleep(5)
    html = chrome_driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find("div", class_="nt-card-list")
    if not container:
        print("❌ Couldn't find the notifications container.")
        return

    unread_cards = container.select("article[aria-label^='Unread notification']")
    print(f"🔔 Found {len(unread_cards)} Unread Notifications\n")

    results = []
    for idx, card in enumerate(unread_cards, start=1):
        # 1️⃣ locate the headline <a>
        headline_a = card.find("a", class_="nt-card__headline")
        if not headline_a:
            continue

        # 2️⃣ within that, first span .nt-card__text--3-line → <strong> holds the user name
        name_span = headline_a.find("span", class_="nt-card__text--3-line")
        user_name = ""
        message_content = ""

        if name_span:
            # Extract user name from <strong>
            strong = name_span.find("strong")
            user_name = strong.get_text(strip=True) if strong else ""

            # Get the full text content under nt-card__text--3-line (includes trailing text nodes)
            full_text = name_span.get_text(separator=" ", strip=True)

            # Remove user name portion
            if user_name:
                full_text = full_text.replace(user_name, "", 1).strip()

            # Now apply regex to clean up everything up to and including the first colon
            message_content = re.sub(r'^["\']?[^:]*:\s*', '', full_text)

        # store or print
        print(f"{idx}. 👤 User → {user_name}")
        print(f"   📌 Message → {message_content}\n")
        results.append({"user": user_name, "message": message_content})

    return results

# -------------------------- MODULE 6: Full Flow --------------------------

if __name__ == "__main__":
    driver = get_driver()

    #smart_login(driver)
    smart_login(driver)

    # go_to_messages(driver)
    scrape_with_selenium_and_bs4(driver)
    driver.quit()
