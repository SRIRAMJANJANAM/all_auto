from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def use_automation_profile():
    service = Service("chromedriver.exe")

    options = webdriver.ChromeOptions()

    options.add_argument(r"--user-data-dir=D:\ChromeAutomation\Profile5")
    options.add_argument("--profile-directory=Profile 5")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3")

    print("🚀 Starting Chrome with dedicated automation profile...")

    try:
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 15)
        print("✅ Chrome started successfully!")

        driver.get("https://youtu.be/a0mAojKR9Bk?si=2jd9jDLx-Buc5Elc")
        print("📺 Opened YouTube video")

        time.sleep(5)

        print("🎯 Looking for like button...")
        try:
            containers = driver.find_elements(By.CSS_SELECTOR, "ytd-menu-renderer, #top-level-buttons, #actions")
            for container in containers:
                like_buttons = container.find_elements(By.CSS_SELECTOR, "button[aria-label*='like this video']")
                if like_buttons:
                    like_button = like_buttons[0]
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_button)
                    time.sleep(1)

                    try:
                        is_pressed = like_button.get_attribute("aria-pressed")
                        if is_pressed == "true":
                            print("ℹ️ Video already liked!")
                        else:
                            like_button.click()
                            print("👍 Liked the video!")
                    except:
                        like_button.click()
                        print("👍 Liked the video!")
                    break
            else:
                print("❌ Like button not found in containers")
        except Exception as e:
            print(f"❌ Error: {e}")

        input("Press ENTER to close browser...")
        driver.quit()

    except Exception as e:
        print(f"❌ Error: {e}")

use_automation_profile()




















