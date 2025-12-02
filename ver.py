from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)
import pandas as pd
import requests
import time
import traceback
import os

MAIN_EMAIL = "support@xbotic.in"
MAIN_PASSWORD = "Test@123"
RESPONSE_CODES = [400, 401, 429]

def safe_click(driver, locator, retries=3, delay=0.5):
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(locator))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            time.sleep(delay)
            try:
                element.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", element)
            return True
        except (ElementClickInterceptedException, StaleElementReferenceException):
            print(f"[safe_click] Retry {attempt+1}/{retries} for {locator}")
            time.sleep(1)
        except TimeoutException:
            print(f"[safe_click] Element not clickable: {locator}")
            return False
    return False

def take_screenshot(driver, name="error"):
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)
    filename = f"{name}_{int(time.time())}.png"
    path = os.path.join(folder, filename)
    driver.save_screenshot(path)
    print(f"[screenshot] Saved: {path}")

def click_reauthorize(driver):
    try:
        print("[click_reauthorize] Starting reauthorize flow...")
        if not safe_click(driver, (By.CSS_SELECTOR, "div.e-nk.e-r1.e-r0.e-f0.e-rj")):
            print("[click_reauthorize] Failed outer div")
            return False

        if not safe_click(driver, (By.CSS_SELECTOR,
            "div.e-nk.e-r1.e-r0.e-f0.e-rj > div > span[style*='cursor: pointer']")):
            print("[click_reauthorize] Failed span click")
            return False

        time.sleep(1)
        if not safe_click(driver, (By.XPATH, "//div[contains(@class,'e-t6')]//span[text()='Reauthorize']")):
            print("[click_reauthorize] Failed menu option")
            return False

        time.sleep(1)
        if not safe_click(driver, (By.XPATH, "//button[text()='ReAuthorize']")):
            print("[click_reauthorize] Failed final button")
            return False

        print("[click_reauthorize] Checking for new windows/tabs...")
        time.sleep(3)
        
        original_window = driver.current_window_handle
        if len(driver.window_handles) > 1:
            print("[click_reauthorize] New window/tab detected, switching to it")
            new_window = [window for window in driver.window_handles if window != original_window][0]
            driver.switch_to.window(new_window)

        print("[click_reauthorize] Waiting for Google account selection page...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        print(f"[click_reauthorize] Current URL: {driver.current_url}")
        print(f"[click_reauthorize] Page title: {driver.title}")

        # Click on the specific account instead of entering credentials
        try:
            # Wait for and click on the ORAI Robotics account
            account_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@data-identifier, 'orairobotictech@gmail.com')]"))
            )
            print("[click_reauthorize] Found ORAI Robotics account, clicking it")
            account_element.click()
            time.sleep(3)
            
        except TimeoutException:
            print("[click_reauthorize] Account selection not found, trying alternative selectors")
            take_screenshot(driver, "account_selection_not_found")
            
            # Try alternative selectors for the account
            for selector in [
                (By.XPATH, "//div[contains(text(), 'ORAI Robotics')]"),
                (By.XPATH, "//div[contains(text(), 'orairobotictech@gmail.com')]"),
                (By.XPATH, "//li[contains(@class, 'aZvCDf')]"),
                (By.XPATH, "//div[@role='link' and contains(@data-identifier, 'orairobotictech')]")
            ]:
                try:
                    account_element = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable(selector)
                    )
                    print(f"[click_reauthorize] Found account using alternative selector: {selector}")
                    account_element.click()
                    time.sleep(3)
                    break
                except TimeoutException:
                    continue
            else:
                print("[click_reauthorize] Could not find account element")
                return False

        # Handle security warning page if it appears
        try:
            # Check if we're on the security warning page
            advanced_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Advanced')]"))
            )
            print("[click_reauthorize] Found Advanced link, clicking it")
            advanced_link.click()
            time.sleep(2)
            
            # Click the "Go to cbots.live (unsafe)" link
            unsafe_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Go to cbots.live')]"))
            )
            print("[click_reauthorize] Found unsafe link, clicking it")
            unsafe_link.click()
            time.sleep(2)
            
            # Click the Continue button
            continue_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Continue']/.. | //div[contains(text(), 'Continue')]"))
            )
            print("[click_reauthorize] Found Continue button, clicking it")
            continue_button.click()
            time.sleep(5)
            
        except TimeoutException:
            print("[click_reauthorize] No security warning page detected, proceeding")
        
        # Wait for redirect back to the main application
        WebDriverWait(driver, 20).until(
            lambda d: "cbots.live" in d.current_url or "admin" in d.current_url or d.current_url == "about:blank"
        )
        
        print("[click_reauthorize] Reauthorization completed successfully!")
        
        # Switch back to the original window if needed
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)
        else:
            driver.switch_to.window(original_window)
        
        return True

    except Exception:
        print("[click_reauthorize] Exception occurred")
        traceback.print_exc()
        take_screenshot(driver, "click_reauthorize_exception")
        return False

def switch_account(driver, email):
    try:
        print(f"[switch_account] Switching to {email}")
        if not safe_click(driver, (By.XPATH, "//div[contains(text(),'Switch Account')]")):
            return False

        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Choose Account')]")))
        email_input = driver.find_element(By.XPATH, "//input[@placeholder='Type an account email address']")
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(1)

        try:
            driver.find_element(By.XPATH, "//form//button[@type='button']").click()
            time.sleep(1)
        except:
            pass

        dropdown = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-baseweb='select']")))
        dropdown.click()
        options = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']")))
        selected = next((opt for opt in options if email in opt.text or email.split('@')[0] in opt.text), None)
        if not selected:
            print(f"[switch_account] No match for {email}")
            safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Close']"))
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", selected)
        time.sleep(0.5)
        selected.click()
        time.sleep(1)

        try:
            continue_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Continue')]")))
            if continue_btn.get_attribute("disabled"):
                safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Close']"))
                return False
            continue_btn.click()
        except TimeoutException:
            pass

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "addBotButton")))
        return True

    except Exception:
        print(f"[switch_account] Exception for {email}")
        traceback.print_exc()
        take_screenshot(driver, f"switch_account_error_{email}")
        return False

def get_api_logs_from_current_account(driver):
    found_codes = []
    try:
        bot_cards = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card'][@data-qa='bot-card']")))
        for idx in range(len(bot_cards)):
            retries = 3
            while retries > 0:
                try:
                    cards = driver.find_elements(By.XPATH, "//section[@data-baseweb='card'][@data-qa='bot-card']")
                    if idx >= len(cards): break
                    card = cards[idx]
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
                    time.sleep(0.5)
                    card.click()
                    time.sleep(2)

                    if not safe_click(driver, (By.ID, "integrations-icon")): break
                    time.sleep(1)

                    if not safe_click(driver, (By.XPATH, "//a[3]//span[text()='API Logs']")): break
                    time.sleep(2)

                    if not safe_click(driver, (By.CSS_SELECTOR, "[title='Filter']")): break
                    time.sleep(1)
                    if not safe_click(driver, (By.XPATH, "//span[text()='Response Code']")): break
                    time.sleep(1)

                    for code in RESPONSE_CODES:
                        try:
                            code_elem = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, f"//div[contains(@class,'css-1pcexqc-container')]//div[text()='{code}']")))
                            code_elem.click()
                            time.sleep(1)
                        except TimeoutException:
                            continue

                    if not safe_click(driver, (By.XPATH, "//button[text()='Apply']")): break
                    time.sleep(5)

                    for i in range(1,101):
                        try:
                            span = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, f"//ul[1]/li/div[2]/div[{i}]/div/div[1]/span")))
                            text = span.text.strip()
                            if text in map(str, RESPONSE_CODES):
                                found_codes.append(text)
                        except TimeoutException:
                            break

                    if any(int(c) in RESPONSE_CODES for c in found_codes):
                        try:
                            if safe_click(driver, (By.XPATH, "//a[1]//span[text()='Cloud Integrations']")):
                                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Google Sheets')]")))
                                gs_tile = driver.find_element(By.XPATH, "//p[contains(text(),'Google Sheets')]/../../../..")
                                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gs_tile)
                                time.sleep(1)
                                svg_div = WebDriverWait(gs_tile, 10).until(EC.element_to_be_clickable((By.XPATH, ".//div[@style='margin-right: 1rem;']")))
                                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", svg_div)
                                time.sleep(1)
                                svg_div.click()
                                print("[cloud_integrations] Clicked SVG div.")
                                click_reauthorize(driver)
                        except Exception:
                            print("[cloud_integrations] Exception inside reauth flow")
                            traceback.print_exc()
                            take_screenshot(driver, "cloud_integration_exception")

                    safe_click(driver, (By.XPATH, "//span[text()='Bots']"))
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
                    time.sleep(2)
                    break

                except StaleElementReferenceException:
                    retries -= 1
                    time.sleep(1)
                except Exception:
                    print("[get_api_logs_from_current_account] Error during bot processing")
                    traceback.print_exc()
                    take_screenshot(driver, "bot_log_error")
                    break

        return list(set(found_codes))
    except Exception:
        print("[get_api_logs_from_current_account] Outer exception")
        traceback.print_exc()
        take_screenshot(driver, "overall_error")
        return []

def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/1e6GuGWpFrQd_IUwpCMY7XIX3acclhry0w6Chfrs8DWk/export?format=csv"
    df = pd.read_csv(sheet_url).dropna(subset=["ID"])
    accounts = df["ID"].tolist()

    # ✅ FIXED CHROME INITIALIZATION
    options = Options()
    options.add_argument("--user-data-dir=D:/ORAI/test/chrome-profile")  # Custom profile folder
    options.add_argument("--remote-debugging-port=9222")  # Fix DevToolsActivePort issue
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    driver.get("https://xbotic.cbots.live/admin/login")

    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(MAIN_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(MAIN_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "addBotButton")))
        print(f"[main] Logged in as {MAIN_EMAIL}")

        results = []
        for email in accounts:
            print(f"[main] Processing {email}")
            if switch_account(driver, email):
                logs = get_api_logs_from_current_account(driver)
                results.append(", ".join(logs) if logs else "")
            else:
                results.append("")

        apps_script_url = "https://script.google.com/macros/s/AKfycbzH689HifaD0E2BPpNuY3hVYnDJTHldeT78FMkF_oxK8DvLVn3zTY0qTfj6VUyZXF2_/exec"
        response = requests.post(apps_script_url, json={"responses": results})
        print(f"[main] Posted results: {response.status_code} {response.text}")

    except Exception:
        print("[main] Exception in main flow")
        traceback.print_exc()
        take_screenshot(driver, "main_error")
    finally:
        driver.quit()
        print("[main] Browser closed.")

if __name__ == "__main__":
    main()