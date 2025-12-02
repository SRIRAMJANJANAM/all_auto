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
import requests
import time
import traceback
import os

MAIN_EMAIL = "support@xbotic.in"
MAIN_PASSWORD = "Test@123"
RESPONSE_CODES = [400, 401, 429]

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

        if not safe_click(driver, (By.CSS_SELECTOR, "svg[data-baseweb='icon'][viewBox='0 0 24 24']")):
            print("[click_reauthorize] Failed to click SVG menu")
            return False
        time.sleep(1)

        if not safe_click(driver, (By.XPATH, "//div//span[text()='Reauthorize']")):
            print("[click_reauthorize] Failed menu option")
            return False
        time.sleep(1)

        if not safe_click(driver, (By.XPATH, "//button[text()='ReAuthorize']")):
            print("[click_reauthorize] Failed final button")
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
        except Exception:
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
            print("[switch_account] Clicking 'Continue'")
            continue_btn.click()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "addBotButton")))
            return True
        except TimeoutException:
            print("[switch_account] Continue button not available or clickable")
            safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Close']"))
            return False

    except Exception:
        print(f"[switch_account] Exception switching to {email}")
        traceback.print_exc()
        return False

def get_api_logs_from_first_bot(driver):
    codes = []
    try:
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "createFirstBotButton")))
            print("[get_api_logs] Account has no bots")
            return []
        except TimeoutException:
            pass

        bot_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
        )
        if not bot_cards:
            print("[get_api_logs] No bots found")
            return []

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", bot_cards[0])
        time.sleep(1)
        driver.execute_script("arguments[0].click();", bot_cards[0])
        time.sleep(2)

        if not safe_click(driver, (By.ID, "integrations-icon")):
            return []
        time.sleep(1)

        if not safe_click(driver, (By.XPATH, "//a[.//span[text()='API Logs']]")):
            return []
        time.sleep(2)

        if not safe_click(driver, (By.CSS_SELECTOR, "[title='Filter']")):
            return []
        time.sleep(1)

        if not safe_click(driver, (By.XPATH, "//span[text()='Response Code']")):
            return []

        for code in RESPONSE_CODES:
            try:
                code_elem = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@class,'css-1pcexqc-container')]//div[text()='{code}']"))
                )
                code_elem.click()
                time.sleep(0.5)
            except TimeoutException:
                pass

        if not safe_click(driver, (By.XPATH, "//button[text()='Apply']")):
            time.sleep(1)
            return []
        time.sleep(2)

        for i in range(1, 101):
            try:
                span = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, f"//ul[1]/li/div[2]/div[{i}]/div/div[1]/span"))
                )
                text = span.text.strip()
                if text:
                    codes.append(text)
            except TimeoutException:
                break

        filtered = [c for c in set(codes) if c in {str(rc) for rc in RESPONSE_CODES}]
        if filtered:
            if safe_click(driver, (By.XPATH, "//a[1]//span[text()='Cloud Integrations']")):
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Google Sheets')]")))
                gs_tile = driver.find_element(By.XPATH, "//p[contains(text(),'Google Sheets')]/../../../..")
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gs_tile)
                time.sleep(1)
                if safe_click(driver, (By.XPATH, ".//div[@style='margin-right: 1rem;']"), context=gs_tile):
                    print("[cloud_integrations] Clicked SVG div.")
                    click_reauthorize(driver)
                else:
                    print("[cloud_integrations] SVG not clickable; skipping reauthorization")

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

        return filtered

    except Exception as e:
        print(f"[get_api_logs] Exception: {e}")
        traceback.print_exc()
        try:
            driver.get("https://xbotic.cbots.live/admin/bots")
        except:
            pass
        return []

def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/1e6GuGWpFrQd_IUwpCMY7XIX3acclhry0w6Chfrs8DWk/export?format=csv"
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

        results = []
        for email in accounts:
            print(f"[main] Processing {email}")
            if switch_account(driver, email):
                logs = get_api_logs_from_first_bot(driver)
                results.append(", ".join(logs) if logs else "")
            else:
                results.append("")

        apps_script_url = "https://script.google.com/macros/s/AKfycbzH689HifaD0E2BPpNuY3hVYnDJTHldeT78FMkF_oxK8DvLVn3zTY0qTfj6VUyZXF2_/exec"
        response = requests.post(apps_script_url, json={"responses": results})
        print(f"[main] Posted results: {response.status_code} {response.text}")

    except Exception:
        print("[main] Exception in main flow")
        traceback.print_exc()

    finally:
        driver.quit()
        print("[main] Browser closed.")

if __name__ == "__main__":
    main()




























# def get_api_logs_from_first_bot(driver):
#     codes = []
#     try:
#         # Check if the account has no bots
#         try:
#             WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "createFirstBotButton")))
#             print("[get_api_logs] Account has no bots")
#             return []
#         except TimeoutException:
#             pass

#         # Click the first bot card
#         bot_cards = WebDriverWait(driver, 15).until(
#             EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
#         )
#         if not bot_cards:
#             print("[get_api_logs] No bots found")
#             return []

#         driver.execute_script("arguments[0].scrollIntoView({block:'center'});", bot_cards[0])
#         time.sleep(1)
#         driver.execute_script("arguments[0].click();", bot_cards[0])
#         time.sleep(2)

#         # Go to Integrations > API Logs
#         if not safe_click(driver, (By.ID, "integrations-icon")):
#             return []
#         time.sleep(1)

#         if not safe_click(driver, (By.XPATH, "//a[.//span[text()='API Logs']]")):
#             return []
#         time.sleep(2)

#         # STEP 1: Set rows per page to 100 BEFORE scraping
#         try:
#             print("[pagination] Expanding dropdown to select 100 rows")
#             dropdown_toggle = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-baseweb='block'][aria-haspopup='true']"))
#             )
#             dropdown_toggle.click()
#             time.sleep(1)

#             option_100 = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.XPATH, "//span[text()='100']"))
#             )
#             option_100.click()
#             time.sleep(2)
#             print("[pagination] Selected 100 rows per page")
#         except Exception as e:
#             print(f"[pagination] Failed to set rows per page: {e}")

#         # STEP 2: Directly collect response codes from table rows (without opening filter)
#         print("[get_api_logs] Collecting response codes directly from table rows")
#         for i in range(1, 101):
#             try:
#                 # Adjust this XPath if your response code column is different
#                 cell = WebDriverWait(driver, 3).until(
#                     EC.presence_of_element_located((By.XPATH, f"//ul[1]/li/div[2]/div[{i}]/div/div[1]/span"))
#                 )
#                 text = cell.text.strip()
#                 if text:
#                     codes.append(text)
#             except TimeoutException:
#                 print(f"[get_api_logs] No more rows found at position {i}, stopping")
#                 break

#         print(f"[get_api_logs] All response codes found: {codes}")

#         filtered = [c for c in set(codes) if c in {str(rc) for rc in RESPONSE_CODES}]
#         print(f"[get_api_logs] Filtered response codes: {filtered}")

#         # STEP 3: Reauthorize if needed
#         if filtered:
#             if safe_click(driver, (By.XPATH, "//a[1]//span[text()='Cloud Integrations']")):
#                 WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Google Sheets')]"))
#                 )
#                 gs_tile = driver.find_element(By.XPATH, "//p[contains(text(),'Google Sheets')]/../../../..")
#                 driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gs_tile)
#                 time.sleep(1)
#                 if safe_click(driver, (By.XPATH, "//p[contains(text(),'Google Sheets')]/../../../..//div[@style='margin-right: 1rem;']"), context=gs_tile):
#                     print("[cloud_integrations] Clicked SVG div.")
#                     click_reauthorize(driver)
#                 else:
#                     print("[cloud_integrations] SVG not clickable; skipping reauthorization")

#         # STEP 4: Navigate back to bots list
#         back_success = safe_click(driver, (By.XPATH, "//span[text()='Bots']"))
#         if not back_success:
#             back_success = safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Back']"))
#         if not back_success:
#             try:
#                 driver.get("https://xbotic.cbots.live/admin/bots")
#             except:
#                 pass

#         WebDriverWait(driver, 15).until(
#             EC.any_of(
#                 EC.presence_of_element_located((By.ID, "addBotButton")),
#                 EC.presence_of_element_located((By.ID, "createFirstBotButton"))
#             )
#         )
#         time.sleep(2)

#         return filtered

#     except Exception as e:
#         print(f"[get_api_logs] Exception: {e}")
#         traceback.print_exc()
#         try:
#             driver.get("https://xbotic.cbots.live/admin/bots")
#         except:
#             pass
#         return []
