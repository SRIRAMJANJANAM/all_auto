from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

options = webdriver.ChromeOptions()
options.add_argument(r"--user-data-dir=D:\ChromeAutomation\Profile1")

driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")

print("📱 Login completed? Waiting...")
time.sleep(20)

print("🤖 Auto-reply started (WhatsApp Business)...")

while True:
    try:
        # 🔥 Find unread chat badges (green numbers)
        unread_badges = driver.find_elements(
            By.XPATH,
            "//span[contains(@class,'unread')] | //span[text() and number(text())>=1]"
        )

        for badge in unread_badges:
            try:
                badge.click()
                time.sleep(1)

                # Get chat title (number or name)
                chat_title = driver.find_element(
                    By.XPATH,
                    "//header//span[@dir='auto']"
                ).text

                print(f"📩 New message from: {chat_title}")

                message_box = driver.find_element(
                    By.XPATH,
                    "//footer//div[@contenteditable='true']"
                )
                message_box.click()
                message_box.send_keys("Hi")
                message_box.send_keys(Keys.ENTER)

                print("✅ Replied: Hi")

            except Exception:
                pass

        time.sleep(3)

    except Exception:
        time.sleep(3)
