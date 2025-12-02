import speech_recognition as sr
import keyboard
import pyautogui
import time

def record_and_type_chunk(duration=20):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎙️ Listening...")
        audio = recognizer.record(source, duration=duration)
    
    try:
        text = recognizer.recognize_google(audio)
        if text.strip():
            print("📝", text)
            pyautogui.write(text + " ")
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print(f"❌ Could not request results; {e}")

print("🟢 Press Win + Shift to start live dictation...")

listening = False

while True:
    if keyboard.is_pressed('windows') and keyboard.is_pressed('shift'):
        listening = not listening
        print("🟢 Listening activated." if listening else "🛑 Listening stopped.")
        time.sleep(1)  # debounce
    
    while listening:
        record_and_type_chunk(duration=20)  # short chunks for near real-time
