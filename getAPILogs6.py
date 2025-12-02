from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

import pandas as pd
import requests
import time


def get_initials(text):
    words = text.split()
    if len(words) == 1:
        return words[0][0].upper()
    elif len(words) > 1:
        return words[0][0].upper() + words[1][0].upper()
    return ""


def get_api_logs(email, password, response_codes=[400, 401, 429]):
    driver = webdriver.Chrome()
    driver.get("https://xbotic.cbots.live/admin/login")

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
            print(f"Login successful for {email}")
        except TimeoutException:
            print(f"Login unsuccessful for {email}")
            driver.save_screenshot(f"login_failed_{email.replace('@','_at_')}.png")
            driver.quit()
            return []

        codes = []
        bot_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
        )

        for index in range(len(bot_cards)):
            try:
                cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//section[@data-baseweb='card' and @data-qa='bot-card']"))
                )
                if index >= len(cards):
                    print(f"Bot card index {index} out of range, stopping loop.")
                    break

                card = cards[index]
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(card))
                card.click()
                time.sleep(2)

                # Go to integrations
                integrations_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "integrations-icon"))
                )
                integrations_button.click()

                # Click API Logs
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[3]//span[text()='API Logs']"))
                ).click()

                # Click filter
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[title='Filter']"))).click()

                # Choose "Response Code"
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Response Code']"))).click()

                # Select response codes
                for code in response_codes:
                    try:
                        code_elem = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located(
                                (By.XPATH, f"//div[@class='css-1pcexqc-container']//div[text()='{code}']")
                            )
                        )
                        code_elem.click()
                    except TimeoutException:
                        continue

                # Apply filter
                driver.find_element(By.XPATH, "//button[text()='Apply']").click()
                time.sleep(2)

                # Extract response codes from UI
                entries = driver.find_elements(By.XPATH, "(//ul[contains(@class,'List')])[1]/li")
                for entry in entries[:100]:
                    try:
                        status_span = entry.find_element(By.XPATH, ".//span[text()='400' or text()='401' or text()='429']")
                        code_text = status_span.text.strip()
                        if code_text in map(str, response_codes):
                            codes.append(code_text)
                    except Exception:
                        continue

                # Go back to bots page
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Bots']"))).click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
                time.sleep(2)

            except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
                print(f"Error with bot card index {index}: {e}")
                try:
                    driver.find_element(By.XPATH, "//span[text()='Bots']").click()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "addBotButton")))
                except:
                    pass
                continue

        # Logout
        try:
            acc_text = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/div/div/div/div/section/div/div[2]/div[2]/div/div[1]/h1").text
            initials = get_initials(acc_text)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{initials}']")))
            driver.find_element(By.XPATH, f"//div[text()='{initials}']").click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Logout']")))
            driver.find_element(By.XPATH, "//span[text()='Logout']").click()
            print("Logout successful")
        except Exception:
            print("Logout skipped")

        driver.quit()

        allowed = set(str(c) for c in response_codes)
        filtered = list(set(c for c in codes if c in allowed))
        return filtered

    except Exception as e:
        print(f"Error during processing for {email}: {e}")
        driver.quit()
        return []


def get_logs_from_accounts(accounts):
    results = []

    for account in accounts:
        email = account.get("email")
        password = account.get("password")
        response_codes = account.get("response_codes", [400, 401, 429])

        if not email or not password:
            print(f"Skipping account with missing credentials.")
            results.append("")
            continue

        print(f"[*] Processing account: {email}")
        try:
            codes = get_api_logs(email, password, response_codes)
            results.append(", ".join(codes) if codes else "")
        except Exception as e:
            print(f"Error processing account {email}: {e}")
            results.append("")

    return results


# === Read accounts from Google Sheet ===
sheet_url = "https://docs.google.com/spreadsheets/d/1MebYL8mSW0jTLihhzX0EXsSP971zrOr8rEpe1r8v1To/export?format=csv"
df = pd.read_csv(sheet_url).dropna(subset=["ID", "Password"])

accounts = [{
    "email": row["ID"],
    "password": row["Password"],
    "response_codes": [400, 401, 429]
} for _, row in df.iterrows()]

# === Run log extraction ===
output_column = get_logs_from_accounts(accounts)

# Pad output if needed
output_column += [""] * (len(df) - len(output_column))

# === Send data to Apps Script ===
apps_script_url = "https://script.google.com/macros/s/AKfycbzccIJjLH_04LF4N4PK5wNLT5IRPFy75_k5XbBPwe_rquXcvJqB2h6SH-XjQKHH_U8CAQ/exec"
payload = {
    "responses": output_column
}

print("Collected response codes:", output_column)

try:
    res = requests.post(apps_script_url, json=payload)
    print("Status code:", res.status_code)
except Exception as e:
    print("Failed to send data:", e)











# import requests

# def test_google_apps_script_update():
#     apps_script_url = "https://script.google.com/macros/s/AKfycby30AjjdfdLqJyY60i9yTPNFZ-TtKtKjFuW09TuaJ-P_w0sB-9_s8gHm4KmaitO-B4j/exec"  # Replace with your Apps Script Web App URL

#     test_payload = {
#         "responses": [
#             "400, 401, 429",
#             "200, 201",
#             "500, 503",
#             "",  # Empty string to test padding
#         ]
#     }

#     try:
#         response = requests.post(apps_script_url, json=test_payload)
#         print("Status Code:", response.status_code)
#         print("Response Text:", response.text)

#         if response.status_code == 200 and "successfully" in response.text:
#             print(" Test passed: Sheet updated successfully")
#         else:
#             print(" Test failed: Unexpected response")
#     except Exception as e:
#         print(" Test failed with exception:", e)


# if __name__ == "__main__":
#     test_google_apps_script_update()
