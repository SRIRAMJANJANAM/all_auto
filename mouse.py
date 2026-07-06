import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize camera and hand detector
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

screen_width, screen_height = pyautogui.size()

# Timing for clicks
last_left_click_time = 0
left_click_cooldown = 0.3
last_tap_time = 0
tap_count = 0
double_click_max_delay = 0.4  # seconds

def finger_is_up(lm, tip, pip):
    # For flipped image, finger is up if tip.y < pip.y
    return lm[tip].y < lm[pip].y

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm = hand_landmarks.landmark

            # Check finger states
            index_up = finger_is_up(lm, 8, 6)
            middle_up = finger_is_up(lm, 12, 10)

            # Calculate finger positions in screen coords
            x_index = int(lm[8].x * screen_width)
            y_index = int(lm[8].y * screen_height)
            x_middle = int(lm[12].x * screen_width)
            y_middle = int(lm[12].y * screen_height)

            current_time = time.time()

            # Movement: If both index and middle fingers up, move mouse to average position
            if index_up and middle_up:
                move_x = (x_index + x_middle) // 2
                move_y = (y_index + y_middle) // 2
                pyautogui.moveTo(move_x, move_y)

            # Left click: Only index finger up, detect taps
            elif index_up and not middle_up:
                # Detect tap: mouse click on finger down event
                # We'll detect a "tap" if index finger goes up and down quickly
                # For simplicity, here we trigger click once when detected
                if (current_time - last_left_click_time) > left_click_cooldown:
                    # Check if this is a double tap
                    if (current_time - last_tap_time) < double_click_max_delay:
                        tap_count += 1
                    else:
                        tap_count = 1
                    last_tap_time = current_time

                    if tap_count == 2:
                        pyautogui.doubleClick()
                        print("Double Click")
                        tap_count = 0
                    else:
                        pyautogui.click()
                        print("Left Click")
                    
                    last_left_click_time = current_time

            # Right click: Only middle finger up
            elif middle_up and not index_up:
                if (current_time - last_left_click_time) > left_click_cooldown:
                    pyautogui.rightClick()
                    print("Right Click")
                    last_left_click_time = current_time

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Virtual Mouse Comfortable", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
