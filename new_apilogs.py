from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
import pandas as pd
import requests
import time
import traceback

MAIN_EMAIL = "support@xbotic.in"
MAIN_PASSWORD = "Test@123"
RESPONSE_CODES = [400, 401, 429]


def safe_click(driver, locator, retries=3, delay=0.5):
    """Click element safely with retries, scrolling, and JS fallback."""
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
            print(f"[safe_click] Click issue, retrying... ({attempt+1}/{retries}) for {locator}")
            time.sleep(1)
        except TimeoutException:
            print(f"[safe_click] Element not clickable: {locator}")
            return False
    return False


def switch_account(driver, email):
    try:
        print(f"[switch_account] Switching to account: {email}")
        # Open switch account modal
        if not safe_click(driver, (By.XPATH, "//div[contains(text(),'Switch Account')]")):
            print(f"[switch_account] Cannot open 'Switch Account' panel for {email}")
            return False

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Choose Account')]"))
        )
        print("[switch_account] 'Choose Account' modal is visible.")

        email_input = driver.find_element(By.XPATH, "//input[@placeholder='Type an account email address']")
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(1)

        # Click search button if exists (button type='button' inside form)
        try:
            driver.find_element(By.XPATH, "//form//button[@type='button']").click()
            time.sleep(1)
        except Exception:
            pass

        print(f"[switch_account] Searched for email: {email}")

        dropdown = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-baseweb='select']"))
        )
        dropdown.click()
        print("[switch_account] Dropdown clicked, now waiting for listbox.")

        options_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul[role='listbox']"))
        )

        options = options_container.find_elements(By.CSS_SELECTOR, "li[role='option']")
        print(f"[switch_account] Options found: {[opt.text for opt in options]}")

        selected_option = next((opt for opt in options if email in opt.text), None)
        if not selected_option:
            username = email.split('@')[0]
            selected_option = next((opt for opt in options if username in opt.text), None)

        if not selected_option:
            print(f"[switch_account] No matching option for '{email}'")
            driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", selected_option)
        time.sleep(0.5)
        selected_text = selected_option.text
        selected_option.click()
        time.sleep(1)
        print(f"[switch_account] Selected: {selected_text}")

        # Handle Continue button if it appears after selecting account
        try:
            continue_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Continue')]"))
            )
            if continue_btn.get_attribute("disabled"):
                print(f"[switch_account] Continue button disabled for {email}")
                driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
                return False
            continue_btn.click()
            print("[switch_account] Continue button clicked.")
        except TimeoutException:
            print("[switch_account] No Continue button, proceeding.")

        # Wait for Bots page to load fully
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "addBotButton")))
        print(f"[switch_account] Successfully switched to {email} and bots page loaded.")
        return True

    except Exception as e:
        print(f"[switch_account] Error for {email}: {e}")
        traceback.print_exc()
        try:
            driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
        except:
            pass
        return False


def get_api_logs_from_current_account(driver):
    codes = []
    try:
        bot_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
        )

        for index in range(len(bot_cards)):
            retries = 3
            while retries > 0:
                try:
                    cards = driver.find_elements(By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']")
                    if index >= len(cards):
                        break
                    card = cards[index]
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", card)
                    time.sleep(2)

                    # Click on Integrations icon
                    safe_click(driver, (By.ID, "integrations-icon"))
                    time.sleep(1)

                    # Click on API Logs tab
                    safe_click(driver, (By.XPATH, "//a[3]//span[text()='API Logs']"))
                    time.sleep(2)

                    # Open Filter dropdown
                    safe_click(driver, (By.CSS_SELECTOR, "[title='Filter']"))
                    time.sleep(1)

                    # Click on Response Code filter
                    safe_click(driver, (By.XPATH, "//span[text()='Response Code']"))
                    time.sleep(1)

                    # Select required response codes
                    for code in RESPONSE_CODES:
                        try:
                            code_elem = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, f"//div[contains(@class,'css-1pcexqc-container')]//div[text()='{code}']")
                                )
                            )
                            code_elem.click()
                            time.sleep(0.5)
                        except TimeoutException:
                            # Some codes may not be present
                            pass

                    # Apply filter
                    safe_click(driver, (By.XPATH, "//button[text()='Apply']"))
                    time.sleep(2)

                    # Extract response codes (up to 100)
                    for i in range(1, 101):
                        try:
                            path = f"//ul[1]/li/div[2]/div[{i}]/div/div[1]/span"
                            span = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, path)))
                            text = span.text.strip()
                            if text:
                                codes.append(text)
                        except TimeoutException:
                            break

                    # Go back to Bots page
                    safe_click(driver, (By.XPATH, "//span[text()='Bots']"))
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
                    time.sleep(2)

                    break  # Break retry loop on success

                except StaleElementReferenceException:
                    print(f"[get_api_logs] StaleElementReferenceException on bot card {index}, retrying...")
                    time.sleep(1)
                    retries -= 1
                except Exception as inner_e:
                    print(f"[get_api_logs] Error on bot card {index}: {inner_e}")
                    break

        filtered = [c for c in set(codes) if c in {str(rc) for rc in RESPONSE_CODES}]
        return filtered

    except Exception as e:
        print(f"[get_api_logs] Extraction error: {e}")
        traceback.print_exc()
        return []


def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/1--zS0qUUxv-MUXa7yFygzR3NkDFmkdGZvuWQ9CQBKGM/export?format=csv"
    df = pd.read_csv(sheet_url).dropna(subset=["ID"])
    accounts = df["ID"].tolist()

    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://xbotic.cbots.live/admin/login")

    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(MAIN_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(MAIN_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "addBotButton")))
        print(f"[main] Login successful for main account {MAIN_EMAIL}")

        results = []
        for email in accounts:
            if not email or not isinstance(email, str) or not email.strip():
                print(f"[main] Skipping invalid email: {email}")
                results.append("")
                continue
            if switch_account(driver, email):
                # After switching, page fully loaded, scrape logs
                logs = get_api_logs_from_current_account(driver)
                results.append(", ".join(logs) if logs else "")
            else:
                results.append("")

        # Send results to Google Apps Script endpoint
        apps_script_url = "https://script.google.com/macros/s/AKfycbyTeV4G-4Wi7UG6wQXlkYc-2_-hXInQ2Bsp4xkeo6Onh9LhEdKIxyeyoC8r-fW2YkRg/exec"
        payload = {"responses": results}
        try:
            response = requests.post(apps_script_url, json=payload)
            print(f"[main] Data sent. Status code: {response.status_code}")
        except Exception as e:
            print(f"[main] Failed to send: {e}")

    except Exception as e:
        print(f"[main] Login failed: {e}")
        traceback.print_exc()
    finally:
        driver.quit()
        print("[main] Browser closed.")


if __name__ == "__main__":
    main()
