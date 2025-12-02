from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchWindowException
)
import pandas as pd
import time
import traceback
import re
import os
from datetime import datetime

MAIN_EMAIL = "support@xbotic.in"
MAIN_PASSWORD = "Test@123"

# CSV file to store execution results
RESULTS_FILE = "execution_results.csv"

def initialize_results_file():
    """Initialize the results CSV file with headers if it doesn't exist"""
    if not os.path.exists(RESULTS_FILE):
        df = pd.DataFrame(columns=[
            'timestamp', 
            'account_email', 
            'switch_status', 
            'reauthorization_status',
            'error_message'
        ])
        df.to_csv(RESULTS_FILE, index=False)
        print(f"[initialize_results_file] Created new results file: {RESULTS_FILE}")

def save_result(account_email, switch_status, reauthorization_status, error_message=""):
    """Save execution result to CSV file"""
    try:
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'account_email': account_email,
            'switch_status': switch_status,
            'reauthorization_status': reauthorization_status,
            'error_message': error_message
        }
        
        # Append to CSV
        df = pd.DataFrame([result])
        df.to_csv(RESULTS_FILE, mode='a', header=False, index=False)
        print(f"[save_result] Saved result for {account_email}: Switch={switch_status}, Reauth={reauthorization_status}")
        
    except Exception as e:
        print(f"[save_result] Error saving result: {e}")

def extract_emails(text):
    return re.findall(r'[\w\.-]+@[\w\.-]+', text)

def safe_click(driver, locator, retries=3, delay=0.5, context=None):
    """
    Attempts to click an element safely with retries.
    If `context` is provided, the search is scoped to that element.
    """
    target = context or driver
    for attempt in range(retries):
        try:
            element = WebDriverWait(target, 15).until(
                EC.element_to_be_clickable(locator)
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            time.sleep(delay)
            try:
                element.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", element)
            return True
        except (ElementClickInterceptedException, StaleElementReferenceException):
            print(f"[safe_click] Retry {attempt + 1}/{retries} for {locator}")
            time.sleep(1)
        except TimeoutException:
            print(f"[safe_click] Element not clickable: {locator}")
            return False
    return False

def wait_for_redirect(driver, timeout=20):
    """
    Waits for a URL change indicating redirect (contains 'cbots.live', 'admin', or 'about:blank').
    """
    def _check(d):
        try:
            url = d.current_url or ""
        except (NoSuchWindowException, Exception):
            return False
        return ("cbots.live" in url) or ("admin" in url) or (url == "about:blank")

    try:
        WebDriverWait(driver, timeout).until(_check)
        return True
    except TimeoutException:
        print("[wait_for_redirect] Timeout waiting for redirect.")
        return False

def click_reauthorize(driver):
    try:
        print("[click_reauthorize] Starting reauthorize flow...")
        original_window = driver.current_window_handle
        try:
            orai_elements = driver.find_elements(By.XPATH, "//div[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'orai')]")
            
            found = False
            for orai_element in orai_elements:
                try:
                    account_text = orai_element.text.strip()
                    if account_text and len(account_text) < 50:  # Reasonable length for account name
                        print(f"[click_reauthorize] Found ORAI account: {account_text}")
                        svg_menu = orai_element.find_element(By.XPATH, "./following-sibling::span//svg[viewBox='0 0 24 24']")
                        svg_menu.click()
                        found = True
                        print("[click_reauthorize] Successfully clicked ORAI menu")
                        break
                except Exception as e:
                    continue
            if not found:
                print("[click_reauthorize] Trying fallback SVG search...")
                svgs = driver.find_elements(By.CSS_SELECTOR, "svg[data-baseweb='icon'][viewBox='0 0 24 24']")
                for svg in svgs:
                    try:
                        parent_container = svg.find_element(By.XPATH, "./ancestor::div[1]")
                        container_text = parent_container.text.lower()
                        if 'orai' in container_text:
                            svg.click()
                            found = True
                            print("[click_reauthorize] Found ORAI via fallback")
                            break
                    except:
                        continue
            
            if not found:
                print("[click_reauthorize] No ORAI-related menu found, attempting to proceed anyway")
                
        except Exception as e:
            print(f"[click_reauthorize] Exception during ORAI menu click: {e}")

        time.sleep(1)

        if not safe_click(driver, (By.XPATH, "//div//span[text()='Reauthorize']")):
            print("[click_reauthorize] Failed to find 'Reauthorize' menu option")
            return False
        time.sleep(1)

        if not safe_click(driver, (By.XPATH, "//button[text()='ReAuthorize']")):
            print("[click_reauthorize] Failed final 'ReAuthorize' button")
            return False

        print("[click_reauthorize] Waiting for new window/tab...")
        time.sleep(5)

        WebDriverWait(driver, 15).until(lambda d: len(d.window_handles) > 1)
        new_window = [w for w in driver.window_handles if w != original_window][0]
        driver.switch_to.window(new_window)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        print(f"[click_reauthorize] URL: {driver.current_url}")
        print(f"[click_reauthorize] Title: {driver.title}")

        try:
            selector = (By.XPATH, "//div[contains(@data-identifier, 'orairobotictech@gmail.com')]")
            account_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(selector)
            )
            print("[click_reauthorize] Selected ORAI Robotics account")
            account_element.click()
            time.sleep(3)
        except TimeoutException:
            print("[click_reauthorize] Account not found, trying fallback selectors")
            fallback_selectors = [
                (By.XPATH, "//div[contains(text(), 'ORAI Robotics')]"),
                (By.XPATH, "//div[contains(text(), 'orairobotictech@gmail.com')]"),
                (By.XPATH, "//li[contains(@class, 'aZvCDf')]"),
                (By.XPATH, "//div[@role='link' and contains(@data-identifier, 'orairobotictech')]")
            ]
            for sel in fallback_selectors:
                try:
                    element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(sel))
                    print(f"[click_reauthorize] Using fallback selector: {sel}")
                    element.click()
                    time.sleep(3)
                    break
                except TimeoutException:
                    continue
            else:
                print("[click_reauthorize] Could not select account")
                return False

        try:
            adv_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Advanced')]")))
            print("[click_reauthorize] Clicking 'Advanced'")
            adv_link.click()
            time.sleep(2)

            unsafe_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Go to cbots.live')]")))
            print("[click_reauthorize] Clicking unsafe link")
            unsafe_link.click()
            time.sleep(2)

            cont_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button/span[text()='Continue'] | //div[text()='Continue'] | //span[text()='Continue']/ancestor::button")
                )
            )
            print("[click_reauthorize] Clicking 'Continue'")
            cont_btn.click()
            time.sleep(5)
        except TimeoutException:
            print("[click_reauthorize] No warning, attempting direct 'Continue'")
            try:
                cont_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button/span[text()='Continue'] | //div[text()='Continue'] | //span[text()='Continue']/ancestor::button")
                    )
                )
                print("[click_reauthorize] Clicking 'Continue'")
                cont_btn.click()
                time.sleep(5)
            except TimeoutException:
                print("[click_reauthorize] Couldn't find 'Continue'")

        if not wait_for_redirect(driver):
            current_url = driver.current_url
            if "cbots.live" in current_url or "admin" in current_url:
                print("[click_reauthorize] Already on target page")
            else:
                raise TimeoutException("Redirect not detected")

        print("[click_reauthorize] Reauthorization complete")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)

        time.sleep(3)
        return True

    except Exception:
        print("[click_reauthorize] Exception during reauthorize:")
        traceback.print_exc()
        try:
            if driver.window_handles:
                driver.switch_to.window(original_window)
        except:
            pass
        return False

def switch_account(driver, email):
    try:
        print(f"[switch_account] Switching to {email}")
        
        # Click on Switch Account button
        if not safe_click(driver, (By.XPATH, "//div[contains(text(),'Switch Account')]")):
            print("[switch_account] Could not click 'Switch Account'")
            return False

        # Wait for Choose Account UI
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Choose Account')]"))
        )
        
        # Type the email in the input
        email_input = driver.find_element(By.XPATH, "//input[@placeholder='Type an account email address']")
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(1)
        print("[switch_account] Typed email")

        # Optional: click the form button if available
        try:
            driver.find_element(By.XPATH, "//form//button[@type='button']").click()
            time.sleep(1)
        except Exception as e:
            print(f"[switch_account] Optional form button click failed: {e}")

        # Click the dropdown to show options
        dropdown = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-baseweb='select']"))
        )
        dropdown.click()
        print("[switch_account] Clicked dropdown")

        # Get all dropdown options
        options = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']"))
        )
        print(f"[switch_account] Found {len(options)} options in dropdown.")

        # Print all emails found in each option
        print("[switch_account] All emails extracted from options:")
        all_emails_in_options = []
        for i, opt in enumerate(options):
            opt_text = opt.text.strip()
            emails_found = extract_emails(opt_text)
            print(f"  Option {i+1}: '{opt_text}' -> emails: {emails_found}")
            all_emails_in_options.extend(emails_found)

        selected = None

        # 1) Find first exact full-text match (normal order)
        for opt in options:
            opt_text = opt.text.strip()
            if opt_text.lower() == email.lower():
                print(f"[switch_account] Found exact full-text match (first one): '{opt_text}'")
                selected = opt
                break

        # 2) If no exact full-text match, find first exact email match inside option text (normal order)
        if not selected:
            for opt in options:
                opt_text = opt.text.strip()
                emails_found = extract_emails(opt_text)
                emails_lower = [e.lower() for e in emails_found]
                if email.lower() in emails_lower:
                    print(f"[switch_account] Found email match in extracted emails (first one): '{opt_text}'")
                    selected = opt
                    break

        # 3) Retry logic if still no match
        if not selected:
            print(f"[switch_account] No match for '{email}', retrying in 2 seconds...")
            time.sleep(2)
            options = driver.find_elements(By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']")
            for opt in options:
                opt_text = opt.text.strip()
                emails_found = extract_emails(opt_text)
                emails_lower = [e.lower() for e in emails_found]
                if email.lower() in emails_lower:
                    print(f"[switch_account] Retrying matched email (first one): '{opt_text}'")
                    selected = opt
                    break

        if not selected:
            print(f"[switch_account] Still no match for '{email}', closing dropdown and skipping.")
            safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Close']"))
            return False

        # Scroll into view and click matched option using JS click
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", selected)
        time.sleep(0.5)
        print(f"[switch_account] Clicking on matched option: '{selected.text.strip()}'")
        driver.execute_script("arguments[0].click();", selected)
        time.sleep(1)

        # Click Continue button if enabled
        try:
            continue_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Continue')]"))
            )
            if continue_btn.get_attribute("disabled"):
                print("[switch_account] Continue button disabled")
                safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Close']"))
                return False

            print("[switch_account] Clicking 'Continue'")
            continue_btn.click()

            # Wait for next page element as confirmation
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "addBotButton"))
            )
            return True

        except TimeoutException:
            print("[switch_account] Continue button not available or clickable")
            safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Close']"))
            return False

    except Exception as e:
        print(f"[switch_account] Exception switching to {email}")
        traceback.print_exc()
        return False

def reauthorize_gsheets(driver):
    try:
        print("[reauthorize_gsheets] Starting Google Sheets reauthorization process")

        # Check if account has any bots
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "createFirstBotButton")))
            print("[reauthorize_gsheets] Account has no bots, skipping")
            return True
        except TimeoutException:
            pass

        # Find and click on the first bot
        bot_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
        )
        if not bot_cards:
            print("[reauthorize_gsheets] No bots found")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", bot_cards[0])
        time.sleep(1)
        driver.execute_script("arguments[0].click();", bot_cards[0])
        time.sleep(2)

        # Click on Cloud Integrations
        if not safe_click(driver, (By.ID, "integrations-icon")):
            return False
        time.sleep(1)

        # Try to find and click on Google Sheets in Cloud Integrations
        gs_found = False
        try:
            gs_tile = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Google Sheets')]/../../../.."))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gs_tile)
            time.sleep(1)
            if safe_click(driver, (By.XPATH, ".//div[@style='margin-right: 1rem;']"), context=gs_tile):
                print("[reauthorize_gsheets] Clicked Google Sheets menu")
                click_reauthorize(driver)
                gs_found = True
            else:
                print("[reauthorize_gsheets] SVG not clickable; will fallback to My Integrations")
        except Exception as e:
            print(f"[reauthorize_gsheets] Google Sheets integration not found: {e}")

        # If Google Sheets not found in Cloud Integrations, try My Integrations
        if not gs_found:
            print("[cloud_integrations] Falling back to 'My Integrations' tab")
            if safe_click(driver, (By.XPATH, "//button[@data-qa='My Integrations' and text()='My Integrations']")):
                print("[cloud_integrations] Switched to My Integrations")
                time.sleep(2)

                try:
                    integration_cards = driver.find_elements(
                        By.XPATH,
                        "//div[contains(@class,'e-bt')]//span[text()='View Details']/ancestor::div[contains(@class,'e-bt')]"
                    )
                    if not integration_cards:
                        print("[cloud_integrations] No 'View Details' cards found")
                    else:
                        first_card = integration_cards[0]
                        name_elem = first_card.find_element(By.XPATH, ".//p")
                        name_text = name_elem.text.strip()
                        print(f"[cloud_integrations] Found integration: {name_text}")

                        view_btn = first_card.find_element(By.XPATH, ".//span[text()='View Details']")
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", view_btn)
                        time.sleep(1)
                        view_btn.click()
                        time.sleep(2)
                        click_reauthorize(driver)

                except Exception as e:
                    print(f"[cloud_integrations] Failed during My Integrations fallback: {e}")
            else:
                print("[cloud_integrations] Could not switch to 'My Integrations' tab")

        # Return to bots page
        back_success = safe_click(driver, (By.XPATH, "//span[text()='Bots']"))
        if not back_success:
            back_success = safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Back']"))
        if not back_success:
            try:
                driver.get("https://xbotic.cbots.live/admin/bots")
            except:
                pass

        WebDriverWait(driver, 15).until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "addBotButton")),
                EC.presence_of_element_located((By.ID, "createFirstBotButton"))
            )
        )
        time.sleep(2)

        return True

    except Exception as e:
        print(f"[reauthorize_gsheets] Exception: {e}")
        traceback.print_exc()
        try:
            driver.get("https://xbotic.cbots.live/admin/bots")
        except:
            pass
        return False

def main():
    # Initialize results file
    initialize_results_file()
    
    sheet_url = "https://docs.google.com/spreadsheets/d/1Cj034YHfiDzDlTANpmOg9KN6wf4ryi7tANmRqpL8M5U/export?format=csv"
    df = pd.read_csv(sheet_url).dropna(subset=["ID"])
    accounts = df["ID"].tolist()

    options = Options()
    options.add_argument("--user-data-dir=D:/ORAI/test/chrome-profile")
    options.add_argument("--remote-debugging-port=9222")
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

        for email in accounts:
            print(f"[main] Processing {email}")
            
            # Track execution status
            switch_status = False
            reauthorization_status = False
            error_message = ""
            
            try:
                switch_status = switch_account(driver, email)
                if switch_status:
                    reauthorization_status = reauthorize_gsheets(driver)
                else:
                    error_message = "Failed to switch account"
            except Exception as e:
                error_message = str(e)
                print(f"[main] Error processing {email}: {e}")
                traceback.print_exc()
            
            # Save result to CSV
            save_result(email, switch_status, reauthorization_status, error_message)

        print("[main] All accounts processed successfully")

    except Exception:
        print("[main] Exception in main flow")
        traceback.print_exc()

    finally:
        driver.quit()
        print("[main] Browser closed.")
        print(f"[main] Results saved to: {RESULTS_FILE}")

if __name__ == "__main__":
    main()