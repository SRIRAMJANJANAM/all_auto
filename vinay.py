from turtle import *
import turtle
import random
import time

t = turtle.Turtle()
turtle.speed(20)
screen = turtle.Screen()
screen.setup(width=800, height=600)  # Full size
screen.bgcolor("black")

# Background and main pen settings
turtle.bgcolor("black")
turtle.color("#C0C0C0")  # silver
turtle.pensize(5)

# Head and features
turtle.left(60)
turtle.fd(50)
turtle.left(15)
turtle.circle(100, 90)
turtle.fd(30)
turtle.pensize(10)
turtle.penup()
turtle.right(90)
turtle.fd(20)
turtle.pendown()

turtle.right(40)
turtle.circle(-50, 90)
turtle.fd(20)
turtle.left(150)

# Second head curve
turtle.color("#D3D3D3")  # light gray
turtle.penup()
turtle.fd(40)
turtle.left(20)
turtle.pendown()
turtle.circle(50, 90)

# Third head curve
turtle.color("#A9A9A9")  # dark gray
turtle.penup()
goto(0, 0)
turtle.pensize(5)
turtle.pendown()
turtle.left(30)
turtle.fd(120)
turtle.circle(60, 270)

# Eyes
turtle.color("white")
turtle.penup()
turtle.forward(30)
turtle.right(50)
turtle.forward(135)
turtle.pendown()
turtle.pensize(8)
turtle.circle(50, 90)
turtle.left(95)
turtle.penup()
turtle.circle(60, 75)

# Eyebrows
turtle.penup()
turtle.forward(15)
turtle.left(90)
turtle.pensize(2)
turtle.pendown()
turtle.circle(70, 90)

# Ears
turtle.pensize(5)
turtle.penup()
turtle.forward(75)
turtle.right(90)
turtle.forward(20)
turtle.pendown()
turtle.color("#B0C4DF")  # light steel blue
turtle.circle(90, 90)
turtle.forward(20)

turtle.circle(30, 170)
turtle.right(180)
turtle.circle(28, 180)
turtle.right(160)
turtle.circle(25, 180)
turtle.right(160)
turtle.circle(22, 160)
turtle.forward(20)
turtle.circle(60, 45)

# Trunk
turtle.penup()
goto(0, 0)
turtle.left(130)
turtle.fd(140)
turtle.right(250)
turtle.backward(20)
turtle.circle(80, 20)
turtle.circle(20, 40)

turtle.right(110)
turtle.penup()
turtle.fd(20)
turtle.pendown()

turtle.pensize(10)
turtle.color("#708090")  # slate gray
turtle.forward(50)
turtle.circle(100, 80)
turtle.pensize(9)
turtle.circle(150, 50)
turtle.pensize(7)
turtle.circle(100, 60)
turtle.pensize(5)
turtle.circle(90, 60)
turtle.pensize(4)
turtle.circle(40, 60)
turtle.circle(10, 90)

# Head outline
turtle.color("#C0C0C0")
turtle.penup()
goto(0, 0)
goto(-90, 290)
turtle.right(230)
turtle.pendown()

turtle.circle(-100, 50)
turtle.circle(200, 20)
turtle.circle(50, 30)
turtle.right(180)
turtle.circle(50, 30)
turtle.circle(200, 20)
turtle.circle(-100, 40)

turtle.right(95)
turtle.penup()
turtle.fd(40)
turtle.right(90)
turtle.pendown()
turtle.circle(100, 40)
turtle.penup()
turtle.circle(35, 120)
turtle.right(30)
turtle.pendown()
turtle.pensize(1)
turtle.circle(60, 50)

# Tongue / mouth details
turtle.penup()
goto(-70, 90)

turtle.fillcolor("#FF69B4")  # hot pink
turtle.begin_fill()
turtle.circle(20, 180)
turtle.end_fill()

turtle.penup()
turtle.left(75)
turtle.fillcolor("#FF1493")  # deep pink
turtle.begin_fill()
turtle.circle(70, 35)
turtle.end_fill()

turtle.left(180)
turtle.backward(10)
turtle.pendown()
turtle.left(6)
turtle.pensize(5)
turtle.color("#DC143C")  # crimson red
turtle.circle(-80, 40)
turtle.penup()
goto(0, 0)

# Add ORAI birthday wishes



turtle.color("red")
turtle.goto(490, 260) # Adjust X for margin from right, Y for top
turtle.write("Best Wishes from ORAI", align="right", font=("Arial", 20, "normal"))

# Add some celebratory elements
def draw_star(x, y, size, color):
    turtle.penup()
    turtle.goto(x, y)
    turtle.pendown()
    turtle.color(color)
    turtle.begin_fill()
    for _ in range(5):
        turtle.forward(size)
        turtle.right(144)
    turtle.end_fill()

# Draw some stars around the text
draw_star(-150, 280, 15, "green")
draw_star(150, 280, 15, "green")
draw_star(-180, 250, 10, "red")
draw_star(180, 250, 10, "red")

turtle.penup()
goto(0, 420)
turtle.right(90)

turtle.color("navy")
turtle.fillcolor("navy")
turtle.begin_fill()
turtle.fd(100)
turtle.right(50)
turtle.pendown()
turtle.fd(510)
turtle.left(90)
turtle.right(165)
turtle.end_fill()

turtle.done()






















# def click_reauthorize(driver):
#     try:
#         print("[click_reauthorize] Starting reauthorize flow...")
#         original_window = driver.current_window_handle

#         if not safe_click(driver, (By.CSS_SELECTOR, " div > div > span > svg[data-baseweb='icon'][viewBox='0 0 24 24']")):
#             print("[click_reauthorize] Failed to click SVG menu")
#             return False
#         time.sleep(1)

#         if not safe_click(driver, (By.XPATH, "//div//span[text()='Reauthorize']")):
#             print("[click_reauthorize] Failed menu option")
#             return False
#         time.sleep(1)

#         if not safe_click(driver, (By.XPATH, "//button[text()='ReAuthorize']")):
#             print("[click_reauthorize] Failed final button")
#             return False

#         print("[click_reauthorize] Waiting for new window/tab...")
#         time.sleep(5)

#         WebDriverWait(driver, 15).until(lambda d: len(d.window_handles) > 1)
#         new_window = [w for w in driver.window_handles if w != original_window][0]
#         driver.switch_to.window(new_window)
#         WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

#         print(f"[click_reauthorize] URL: {driver.current_url}")
#         print(f"[click_reauthorize] Title: {driver.title}")

#         try:
#             # Try to click on the ORAI account from the list
#             orai_account = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'e-ag') and .//div[text()='ORAI']]"))
#             )
#             print("[click_reauthorize] Selected ORAI account")
#             orai_account.click()
#             time.sleep(3)
#         except TimeoutException:
#             print("[click_reauthorize] ORAI account not found, trying fallback selectors")
#             fallback_selectors = [
#                 (By.XPATH, "//div[text()='ORAI']"),
#                 (By.XPATH, "//div[contains(@class, 'e-s5') and text()='ORAI']"),
#                 (By.XPATH, "//div[contains(@class, 'e-hm') and text()='ORAI']"),
#                 (By.XPATH, "//div[contains(text(), 'ORAI')]"),
#                 (By.XPATH, "//div[contains(@data-identifier, 'orairobotictech@gmail.com')]"),
#                 (By.XPATH, "//div[contains(text(), 'ORAI Robotics')]"),
#                 (By.XPATH, "//div[contains(text(), 'orairobotictech@gmail.com')]")
#             ]
#             for sel in fallback_selectors:
#                 try:
#                     element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(sel))
#                     print(f"[click_reauthorize] Using fallback selector: {sel}")
#                     element.click()
#                     time.sleep(3)
#                     break
#                 except TimeoutException:
#                     continue
#             else:
#                 print("[click_reauthorize] Could not select account")
#                 return False

#         try:
#             adv_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Advanced')]")))
#             print("[click_reauthorize] Clicking 'Advanced'")
#             adv_link.click()
#             time.sleep(2)

#             unsafe_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Go to cbots.live')]")))
#             print("[click_reauthorize] Clicking unsafe link")
#             unsafe_link.click()
#             time.sleep(2)

#             cont_btn = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable(
#                     (By.XPATH, "//button/span[text()='Continue'] | //div[text()='Continue'] | //span[text()='Continue']/ancestor::button")
#                 )
#             )
#             print("[click_reauthorize] Clicking 'Continue'")
#             cont_btn.click()
#             time.sleep(5)
#         except TimeoutException:
#             print("[click_reauthorize] No warning, attempting direct 'Continue'")
#             try:
#                 cont_btn = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable(
#                         (By.XPATH, "//button/span[text()='Continue'] | //div[text()='Continue'] | //span[text()='Continue']/ancestor::button")
#                     )
#                 )
#                 print("[click_reauthorize] Clicking 'Continue'")
#                 cont_btn.click()
#                 time.sleep(5)
#             except TimeoutException:
#                 print("[click_reauthorize] Couldn't find 'Continue'")

#         if not wait_for_redirect(driver):
#             current_url = driver.current_url
#             if "cbots.live" in current_url or "admin" in current_url:
#                 print("[click_reauthorize] Already on target page")
#             else:
#                 raise TimeoutException("Redirect not detected")

#         print("[click_reauthorize] Reauthorization complete")
#         if len(driver.window_handles) > 1:
#             driver.close()
#             driver.switch_to.window(original_window)

#         time.sleep(3)
#         return True

#     except Exception:
#         print("[click_reauthorize] Exception during reauthorize:")
#         traceback.print_exc()
#         try:
#             if driver.window_handles:
#                 driver.switch_to.window(original_window)
#         except:
#             pass
#         return False



















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

        # 1) Find last exact full-text match
        for opt in reversed(options):
            opt_text = opt.text.strip()
            if opt_text.lower() == email.lower():
                print(f"[switch_account] Found exact full-text match (last one): '{opt_text}'")
                selected = opt
                break

        # 2) If no exact full-text match, find last exact email match inside option text
        if not selected:
            for opt in reversed(options):
                opt_text = opt.text.strip()
                emails_found = extract_emails(opt_text)
                emails_lower = [e.lower() for e in emails_found]
                if email.lower() in emails_lower:
                    print(f"[switch_account] Found email match in extracted emails (last one): '{opt_text}'")
                    selected = opt
                    break

        # 3) Retry logic if still no match
        if not selected:
            print(f"[switch_account] No match for '{email}', retrying in 2 seconds...")
            time.sleep(2)
            options = driver.find_elements(By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']")
            for opt in reversed(options):
                opt_text = opt.text.strip()
                emails_found = extract_emails(opt_text)
                emails_lower = [e.lower() for e in emails_found]
                if email.lower() in emails_lower:
                    print(f"[switch_account] Retrying matched email (last one): '{opt_text}'")
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
