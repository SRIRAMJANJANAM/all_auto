import pyautogui
import time

def prevent_idle(interval=30):
    print("🟢 Anti-idle running. Press Ctrl+C to stop.")
    try:
        while True:
            x, y = pyautogui.position()
            pyautogui.moveTo(x + 1, y)
            pyautogui.moveTo(x, y)
            pyautogui.press('shift')

            print(f"🕒 Activity simulated at {time.strftime('%H:%M:%S')}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n🔴 Anti-idle stopped.")

prevent_idle()
