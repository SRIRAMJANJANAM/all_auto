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
        print("[get_api_logs] Locating bot cards...")
        bot_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
        )
        print(f"[get_api_logs] Found {len(bot_cards)} bot cards")

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
                    if not safe_click(driver, (By.ID, "integrations-icon")):
                        print(f"[get_api_logs] Failed to click Integrations icon on bot {index}")
                        break
                    time.sleep(1)

                    # Click on API Logs tab
                    if not safe_click(driver, (By.XPATH, "//a[3]//span[text()='API Logs']")):
                        print(f"[get_api_logs] Failed to click API Logs tab on bot {index}")
                        break
                    time.sleep(2)

                    # Open Filter dropdown
                    if not safe_click(driver, (By.CSS_SELECTOR, "[title='Filter']")):
                        print(f"[get_api_logs] Failed to open Filter dropdown on bot {index}")
                        break
                    time.sleep(1)

                    # Click on Response Code filter
                    if not safe_click(driver, (By.XPATH, "//span[text()='Response Code']")):
                        print(f"[get_api_logs] Failed to click Response Code filter on bot {index}")
                        break
                    time.sleep(1)

                    # Select required response codes
                    for code in RESPONSE_CODES:
                        try:
                            code_elem = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, f"//div[contains(@class,'css-1pcexqc-container')]//div[text()='{code}']")
                                )
                            )
                            code_elem.click()
                            print(f"[get_api_logs] Selected response code filter: {code}")
                            time.sleep(1)
                        except TimeoutException:
                            continue
                            # Don't break, continue with other codes

                    # Apply filter
                    if not safe_click(driver, (By.XPATH, "//button[text()='Apply']")):
                        print(f"[get_api_logs] Failed to click Apply button on bot {index}")
                        break
                    time.sleep(5)  # Wait longer for filter to apply and data to load

                    # Extract response codes (up to 100)
                    print(f"[get_api_logs] Extracting response codes from logs on bot {index}...")
                    for i in range(1, 101):
                        try:
                            # Adjusted XPath might be needed here depending on actual page structure
                            path = f"//ul[1]/li/div[2]/div[{i}]/div/div[1]/span"
                            span = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, path)))
                            text = span.text.strip()
                            if text:
                                codes.append(text)
                        except TimeoutException:
                            print(f"[get_api_logs] No more response code elements found after {i-1} rows")
                            break

                    # Go back to Bots page
                    if not safe_click(driver, (By.XPATH, "//span[text()='Bots']")):
                        print(f"[get_api_logs] Failed to navigate back to Bots page from bot {index}")
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
                    time.sleep(2)

                    break  # Break retry loop on success

                except StaleElementReferenceException:
                    print(f"[get_api_logs] StaleElementReferenceException on bot card {index}, retrying...")
                    time.sleep(1)
                    retries -= 1
                except Exception as inner_e:
                    print(f"[get_api_logs] Error on bot card {index}: {inner_e}")
                    traceback.print_exc()
                    break

        filtered = [c for c in set(codes) if c in {str(rc) for rc in RESPONSE_CODES}]
        print(f"[get_api_logs] Filtered response codes found: {filtered}")
        return filtered

    except Exception as e:
        print(f"[get_api_logs] Extraction error: {e}")
        traceback.print_exc()
        return []


def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/1e6GuGWpFrQd_IUwpCMY7XIX3acclhry0w6Chfrs8DWk/export?format=csv"
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
            print(f"[main] Processing account: {email}")
            if switch_account(driver, email):
                # After switching, page fully loaded, scrape logs
                logs = get_api_logs_from_current_account(driver)
                results.append(", ".join(logs) if logs else "")
            else:
                results.append("")

        # Send results to Google Apps Script endpoint
        apps_script_url = "https://script.google.com/macros/s/AKfycbzH689HifaD0E2BPpNuY3hVYnDJTHldeT78FMkF_oxK8DvLVn3zTY0qTfj6VUyZXF2_/exec"
        payload = {"responses": results}
        try:
            print(f"[main] Sending payload: {payload}")
            response = requests.post(apps_script_url, json=payload)
            print(f"[main] Data sent. Status code: {response.status_code}")
            print(f"[main] Response text: {response.text}")
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








































































# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import (
#     TimeoutException,
#     StaleElementReferenceException,
#     ElementClickInterceptedException,
# )
# import pandas as pd
# import requests
# import time
# import traceback
# import os

# MAIN_EMAIL = "support@xbotic.in"
# MAIN_PASSWORD = "Test@123"
# RESPONSE_CODES = [400, 401, 429]

# def safe_click(driver, locator, retries=3, delay=0.5):
#     for attempt in range(retries):
#         try:
#             element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(locator))
#             driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#             time.sleep(delay)
#             try:
#                 element.click()
#             except ElementClickInterceptedException:
#                 driver.execute_script("arguments[0].click();", element)
#             return True
#         except (ElementClickInterceptedException, StaleElementReferenceException):
#             print(f"[safe_click] Retry {attempt+1}/{retries} for {locator}")
#             time.sleep(1)
#         except TimeoutException:
#             print(f"[safe_click] Element not clickable: {locator}")
#             return False
#     return False

# def take_screenshot(driver, name="error"):
#     folder = "screenshots"
#     os.makedirs(folder, exist_ok=True)
#     filename = f"{name}_{int(time.time())}.png"
#     path = os.path.join(folder, filename)
#     driver.save_screenshot(path)
#     print(f"[screenshot] Saved: {path}")

# def click_reauthorize(driver):
#     try:
#         print("[click_reauthorize] Starting reauthorize flow...")
#         # 1. Click outer div
#         if not safe_click(driver, (By.CSS_SELECTOR, "div.e-nk.e-r1.e-r0.e-f0.e-rj")):
#             print("[click_reauthorize] Failed outer div")
#             return False

#         # 2. Click the 3-dot span
#         if not safe_click(driver, (By.CSS_SELECTOR,
#             "div.e-nk.e-r1.e-r0.e-f0.e-rj > div > span[style*='cursor: pointer']")):
#             print("[click_reauthorize] Failed span click")
#             return False

#         time.sleep(1)

#         # 3. Click "Reauthorize" in dropdown
#         if not safe_click(driver, (By.XPATH, "//div[contains(@class,'e-t6')]//span[text()='Reauthorize']")):
#             print("[click_reauthorize] Failed menu option")
#             return False

#         time.sleep(1)

#         # 4. Click final confirmation ReAuthorize button
#         if not safe_click(driver, (By.XPATH, "//button[text()='ReAuthorize']")):
#             print("[click_reauthorize] Failed final button")
#             return False

#         print("[click_reauthorize] Reauthorization completed!")
#         return True

#     except Exception:
#         print("[click_reauthorize] Exception occurred")
#         traceback.print_exc()
#         take_screenshot(driver, "click_reauthorize_exception")
#         return False

# def switch_account(driver, email):
#     try:
#         print(f"[switch_account] Switching to {email}")
#         if not safe_click(driver, (By.XPATH, "//div[contains(text(),'Switch Account')]")):
#             return False

#         WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Choose Account')]")))
#         email_input = driver.find_element(By.XPATH, "//input[@placeholder='Type an account email address']")
#         email_input.clear()
#         email_input.send_keys(email)
#         time.sleep(1)

#         # Optional continue button
#         try:
#             driver.find_element(By.XPATH, "//form//button[@type='button']").click()
#             time.sleep(1)
#         except:
#             pass

#         dropdown = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-baseweb='select']")))
#         dropdown.click()
#         options = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']")))
#         selected = next((opt for opt in options if email in opt.text or email.split('@')[0] in opt.text), None)
#         if not selected:
#             print(f"[switch_account] No match for {email}")
#             safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Close']"))
#             return False

#         driver.execute_script("arguments[0].scrollIntoView({block:'center'});", selected)
#         time.sleep(0.5)
#         selected.click()
#         time.sleep(1)

#         try:
#             continue_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Continue')]")))
#             if continue_btn.get_attribute("disabled"):
#                 safe_click(driver, (By.CSS_SELECTOR, "button[aria-label='Close']"))
#                 return False
#             continue_btn.click()
#         except TimeoutException:
#             pass

#         WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "addBotButton")))
#         return True

#     except Exception:
#         print(f"[switch_account] Exception for {email}")
#         traceback.print_exc()
#         take_screenshot(driver, f"switch_account_error_{email}")
#         return False

# def get_api_logs_from_current_account(driver):
#     found_codes = []
#     try:
#         bot_cards = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card'][@data-qa='bot-card']")))
#         for idx in range(len(bot_cards)):
#             retries = 3
#             while retries > 0:
#                 try:
#                     cards = driver.find_elements(By.XPATH, "//section[@data-baseweb='card'][@data-qa='bot-card']")
#                     if idx >= len(cards): break
#                     card = cards[idx]
#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
#                     time.sleep(0.5)
#                     card.click()
#                     time.sleep(2)

#                     if not safe_click(driver, (By.ID, "integrations-icon")): break
#                     time.sleep(1)

#                     if not safe_click(driver, (By.XPATH, "//a[3]//span[text()='API Logs']")): break
#                     time.sleep(2)

#                     if not safe_click(driver, (By.CSS_SELECTOR, "[title='Filter']")): break
#                     time.sleep(1)
#                     if not safe_click(driver, (By.XPATH, "//span[text()='Response Code']")): break
#                     time.sleep(1)

#                     for code in RESPONSE_CODES:
#                         try:
#                             code_elem = WebDriverWait(driver, 5).until(
#                                 EC.presence_of_element_located((By.XPATH, f"//div[contains(@class,'css-1pcexqc-container')]//div[text()='{code}']")))
#                             code_elem.click()
#                             time.sleep(1)
#                         except TimeoutException:
#                             continue

#                     if not safe_click(driver, (By.XPATH, "//button[text()='Apply']")): break
#                     time.sleep(5)

#                     for i in range(1,101):
#                         try:
#                             span = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, f"//ul[1]/li/div[2]/div[{i}]/div/div[1]/span")))
#                             text = span.text.strip()
#                             if text in map(str, RESPONSE_CODES):
#                                 found_codes.append(text)
#                         except TimeoutException:
#                             break

#                     if any(int(c) in RESPONSE_CODES for c in found_codes):
#                         try:
#                             if safe_click(driver, (By.XPATH, "//a[1]//span[text()='Cloud Integrations']")):
#                                 WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Google Sheets')]")))
#                                 gs_tile = driver.find_element(By.XPATH, "//p[contains(text(),'Google Sheets')]/../../../..")
#                                 driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gs_tile)
#                                 time.sleep(1)
#                                 svg_div = WebDriverWait(gs_tile, 10).until(EC.element_to_be_clickable((By.XPATH, ".//div[@style='margin-right: 1rem;']")))
#                                 driver.execute_script("arguments[0].scrollIntoView({block:'center'});", svg_div)
#                                 time.sleep(1)
#                                 svg_div.click()
#                                 print("[cloud_integrations] Clicked SVG div.")
#                                 click_reauthorize(driver)
#                         except Exception:
#                             print("[cloud_integrations] Exception inside reauth flow")
#                             traceback.print_exc()
#                             take_screenshot(driver, "cloud_integration_exception")

#                     safe_click(driver, (By.XPATH, "//span[text()='Bots']"))
#                     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
#                     time.sleep(2)
#                     break

#                 except StaleElementReferenceException:
#                     retries -= 1
#                     time.sleep(1)
#                 except Exception:
#                     print("[get_api_logs_from_current_account] Error during bot processing")
#                     traceback.print_exc()
#                     take_screenshot(driver, "bot_log_error")
#                     break

#         return list(set(found_codes))
#     except Exception:
#         print("[get_api_logs_from_current_account] Outer exception")
#         traceback.print_exc()
#         take_screenshot(driver, "overall_error")
#         return []

# def main():
#     sheet_url = "https://docs.google.com/spreadsheets/d/1e6GuGWpFrQd_IUwpCMY7XIX3acclhry0w6Chfrs8DWk/export?format=csv"
#     df = pd.read_csv(sheet_url).dropna(subset=["ID"])
#     accounts = df["ID"].tolist()

#     driver = webdriver.Chrome()
#     driver.maximize_window()
#     driver.get("https://xbotic.cbots.live/admin/login")

#     try:
#         WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "email")))
#         driver.find_element(By.NAME, "email").send_keys(MAIN_EMAIL)
#         driver.find_element(By.NAME, "password").send_keys(MAIN_PASSWORD)
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
#         WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "addBotButton")))
#         print(f"[main] Logged in as {MAIN_EMAIL}")

#         results = []
#         for email in accounts:
#             print(f"[main] Processing {email}")
#             if switch_account(driver, email):
#                 logs = get_api_logs_from_current_account(driver)
#                 results.append(", ".join(logs) if logs else "")
#             else:
#                 results.append("")

#         apps_script_url = "https://script.google.com/macros/s/AKfycbzH689HifaD0E2BPpNuY3hVYnDJTHldeT78FMkF_oxK8DvLVn3zTY0qTfj6VUyZXF2_/exec"
#         response = requests.post(apps_script_url, json={"responses": results})
#         print(f"[main] Posted results: {response.status_code} {response.text}")

#     except Exception:
#         print("[main] Exception in main flow")
#         traceback.print_exc()
#         take_screenshot(driver, "main_error")
#     finally:
#         driver.quit()
#         print("[main] Browser closed.")

# if __name__ == "__main__":
#     main()
