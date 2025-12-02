from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException,
    WebDriverException,
)
import pandas as pd
import requests
import time
import traceback
import re

MAIN_EMAIL = "support@xbotic.in"
MAIN_PASSWORD = "Test@123"
RESPONSE_CODES = [400, 401, 429]

def extract_emails(text):
    return re.findall(r'[\w\.-]+@[\w\.-]+', text)

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


def ensure_main_page(driver, max_attempts=3):
    """Ensure we're on the main page (with or without bots)."""
    for attempt in range(max_attempts):
        try:
            # Check if we're on a page with the "addBotButton" (has bots)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
            return True
        except TimeoutException:
            try:
                # Check if we're on a page with the "createFirstBotButton" (no bots)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "createFirstBotButton")))
                print("[ensure_main_page] Account has no bots")
                return True
            except TimeoutException:
                if attempt < max_attempts - 1:
                    print(f"[ensure_main_page] Not on main page, attempting to navigate... (Attempt {attempt+1}/{max_attempts})")
                    
                    # Try to click Bots in sidebar
                    if safe_click(driver, (By.XPATH, "//span[text()='Bots']")):
                        time.sleep(2)
                        continue
                    
                    # If still not on main page, navigate directly
                    try:
                        driver.get("https://xbotic.cbots.live/admin/bots")
                        time.sleep(3)
                        continue
                    except WebDriverException:
                        print("[ensure_main_page] Navigation failed, retrying...")
                        time.sleep(2)
                else:
                    print("[ensure_main_page] Could not navigate to main page after multiple attempts")
                    return False
    return False


def switch_account(driver, email):
    try:
        print(f"[switch_account] Switching to account: {email}")
        
        # Ensure we're on the main page before switching accounts
        if not ensure_main_page(driver):
            print("[switch_account] Could not ensure main page")
            return False
        
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
            search_btn = driver.find_element(By.XPATH, "//form//button[@type='button']")
            if search_btn.is_enabled():
                search_btn.click()
                time.sleep(1)
        except Exception:
            pass

        print(f"[switch_account] Searched for email: {email}")

        # Wait for dropdown to be populated
        time.sleep(2)
        
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

        # Only match exact email
        selected_option = None
        for opt in options:
            opt_text = opt.text.strip()
            emails_found = extract_emails(opt_text)
            emails_lower = [e.lower() for e in emails_found]
            if email.lower() in emails_lower:
                selected_option = opt
                break

        if not selected_option:
            print(f"[switch_account] No exact email match for '{email}'")
            try:
                driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
            except:
                pass
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", selected_option)
        time.sleep(0.5)
        selected_text = selected_option.text
        selected_option.click()
        time.sleep(1)
        print(f"[switch_account] Selected: {selected_text}")

        # Handle Continue button if it appears after selecting account
        try:
            continue_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Continue')]"))
            )
            if continue_btn.get_attribute("disabled"):
                print(f"[switch_account] Continue button disabled for {email}")
                driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
                return False
            continue_btn.click()
            print("[switch_account] Continue button clicked.")
            time.sleep(2)
        except TimeoutException:
            print("[switch_account] No Continue button, proceeding.")

        # Wait for Bots page to load fully (with or without bots)
        try:
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "addBotButton")),
                    EC.presence_of_element_located((By.ID, "createFirstBotButton"))
                )
            )
            print(f"[switch_account] Successfully switched to {email} and bots page loaded.")
            return True
        except TimeoutException:
            print(f"[switch_account] Page didn't load properly for {email}, trying to recover...")
            # Try to navigate back to main page
            try:
                driver.get("https://xbotic.cbots.live/admin/bots")
                WebDriverWait(driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.ID, "addBotButton")),
                        EC.presence_of_element_located((By.ID, "createFirstBotButton"))
                    )
                )
                print(f"[switch_account] Recovered and successfully switched to {email}")
                return True
            except:
                print(f"[switch_account] Could not recover after switching to {email}")
                return False

    except Exception as e:
        print(f"[switch_account] Error for {email}: {e}")
        traceback.print_exc()
        try:
            driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
        except:
            pass
        return False  


def get_api_logs_from_first_bot(driver):
    codes = []
    try:
        # Check if account has any bots
        try:
            # Look for the "create first bot" button (no bots)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "createFirstBotButton"))
            )
            print("[get_api_logs] Account has no bots, skipping API logs extraction")
            return []
        except TimeoutException:
            # Account has bots, proceed with extraction
            pass
        
        # Get the first bot card
        bot_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
        )
        
        if not bot_cards:
            print("[get_api_logs] No bot cards found")
            return []
            
        # Click on the first bot
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", bot_cards[0])
        time.sleep(1)
        driver.execute_script("arguments[0].click();", bot_cards[0])
        time.sleep(2)

        # Click on Integrations icon
        if not safe_click(driver, (By.ID, "integrations-icon")):
            print("[get_api_logs] Could not click integrations icon")
            return []

        time.sleep(1)

        # Click on API Logs tab
        if not safe_click(driver, (By.XPATH, "//a[.//span[text()='API Logs']]")):
            print("[get_api_logs] Could not click API Logs tab")
            return []

        time.sleep(2)

        # Open Filter dropdown
        if not safe_click(driver, (By.CSS_SELECTOR, "[title='Filter']")):
            print("[get_api_logs] Could not open filter dropdown")
            return []

        time.sleep(1)

        # Click on Response Code filter
        if not safe_click(driver, (By.XPATH, "//span[text()='Response Code']")):
            print("[get_api_logs] Could not click Response Code filter")
            return []

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
                print(f"[get_api_logs] Response code {code} not found")
                pass

        # Apply filter
        if not safe_click(driver, (By.XPATH, "//button[text()='Apply']")):
            print("[get_api_logs] Could not apply filter")
            return []

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

        # Go back to Bots page using multiple methods
        back_success = False
        try:
            # Method 1: Click Bots in sidebar
            if safe_click(driver, (By.XPATH, "//span[text()='Bots']")):
                back_success = True
        except:
            pass
            
        if not back_success:
            try:
                # Method 2: Click back button if available
                if safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Back']")):
                    back_success = True
            except:
                pass
                
        if not back_success:
            try:
                # Method 3: Navigate directly to bots URL
                driver.get("https://xbotic.cbots.live/admin/bots")
                back_success = True
            except:
                pass
                
        if back_success:
            # Wait for either bot page layout
            WebDriverWait(driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "addBotButton")),
                    EC.presence_of_element_located((By.ID, "createFirstBotButton"))
                )
            )
            time.sleep(2)

        filtered = [c for c in set(codes) if c in {str(rc) for rc in RESPONSE_CODES}]
        return filtered

    except Exception as e:
        print(f"[get_api_logs] Extraction error: {e}")
        traceback.print_exc()
        # Try to go back to Bots page if something went wrong
        try:
            driver.get("https://xbotic.cbots.live/admin/bots")
            WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "addBotButton")),
                    EC.presence_of_element_located((By.ID, "createFirstBotButton"))
                )
            )
        except:
            pass
        return []


def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/10L06ApEplObnJM7UpUxPYvIw8VZdrQ8gr4fZDO3agcw/export?format=csv"
    df = pd.read_csv(sheet_url).dropna(subset=["ID"])
    accounts = df["ID"].tolist()

    # Add Chrome options to handle GPU issues
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-software-rasterizer')
    
    driver = webdriver.Chrome(options=chrome_options)
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
        problematic_accounts = []  # Track accounts that cause issues
        
        for i, email in enumerate(accounts):
            if not email or not isinstance(email, str) or not email.strip():
                print(f"[main] Skipping invalid email: {email}")
                results.append("")
                continue
                
            print(f"[main] Processing account {i+1}/{len(accounts)}: {email}")
            
            # Skip problematic accounts that we know cause GPU issues
            if email in problematic_accounts:
                print(f"[main] Skipping known problematic account: {email}")
                results.append("")
                continue
            
            if switch_account(driver, email):
                # After switching, page fully loaded, scrape logs from first bot only
                logs = get_api_logs_from_first_bot(driver)
                results.append(", ".join(logs) if logs else "")
                
                # Ensure we're back on the main page before switching to next account
                if not ensure_main_page(driver):
                    print(f"[main] Could not return to main page after processing {email}, refreshing...")
                    try:
                        driver.get("https://xbotic.cbots.live/admin/bots")
                        WebDriverWait(driver, 15).until(
                            EC.any_of(
                                EC.presence_of_element_located((By.ID, "addBotButton")),
                                EC.presence_of_element_located((By.ID, "createFirstBotButton"))
                            )
                        )
                    except:
                        print(f"[main] Could not recover, marking {email} as problematic and continuing...")
                        problematic_accounts.append(email)
                        # Try a fresh start by re-logging in
                        try:
                            driver.get("https://xbotic.cbots.live/admin/login")
                            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "email")))
                            driver.find_element(By.NAME, "email").send_keys(MAIN_EMAIL)
                            driver.find_element(By.NAME, "password").send_keys(MAIN_PASSWORD)
                            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "addBotButton")))
                            print(f"[main] Re-login successful")
                        except:
                            print(f"[main] Could not re-login, stopping execution")
                            break
            else:
                results.append("")
                problematic_accounts.append(email)
                print(f"[main] Marked {email} as problematic and continuing...")
                
                # Try to recover by going back to main page or re-logging
                try:
                    driver.get("https://xbotic.cbots.live/admin/bots")
                    WebDriverWait(driver, 15).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.ID, "addBotButton")),
                            EC.presence_of_element_located((By.ID, "createFirstBotButton"))
                        )
                    )
                except:
                    try:
                        driver.get("https://xbotic.cbots.live/admin/login")
                        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "email")))
                        driver.find_element(By.NAME, "email").send_keys(MAIN_EMAIL)
                        driver.find_element(By.NAME, "password").send_keys(MAIN_PASSWORD)
                        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "addBotButton")))
                        print(f"[main] Re-login successful after problematic account")
                    except:
                        print(f"[main] Could not recover after problematic account {email}, stopping execution")
                        break

        # Send results to Google Apps Script endpoint
        apps_script_url = "https://script.google.com/macros/s/AKfycbzHzSOlvXwQnDVAC97rAl_1avMZaIJY-c72rTUGAE7vHfHnJiCcwi4rczMh5MmCB5wA/exec"
        payload = {"responses": results}
        try:
            response = requests.post(apps_script_url, json=payload)
            print(f"[main] Data sent. Status code: {response.status_code}")
            print(f"[main] Problematic accounts: {problematic_accounts}")
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


