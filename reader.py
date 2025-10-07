import mss
import numpy as np
import pytesseract
import pyttsx3
import pyautogui
import cv2
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)
    print(f"Using voice: {voices[0].name}")

def speak(text):
    """Speak text safely in main thread."""
    engine.say(text)
    engine.runAndWait()

print("Script started. Move your mouse over text to read it.")

# Screen capture setup
with mss.mss() as sct:
    monitor = sct.monitors[0]
    screen_width = monitor['width']
    screen_height = monitor['height']

    last_text = ""
    accumulated_text = ""
    stable_counter = 0
    last_ocr_time = 0
    ocr_interval = 0.7  # seconds between OCR captures

    while True:
        x, y = pyautogui.position()
        width, height = 600, 250  # larger capture region
        top = max(0, y - height // 2)
        left = max(0, x - width // 2)
        if top + height > screen_height:
            height = screen_height - top
        if left + width > screen_width:
            width = screen_width - left
        region = {'top': top, 'left': left, 'width': width, 'height': height}

        # Only run OCR at defined interval
        if time.time() - last_ocr_time >= ocr_interval:
            last_ocr_time = time.time()
            try:
                img = np.array(sct.grab(region))
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (3, 3), 0)
                gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                kernel = np.ones((2, 2), np.uint8)
                gray = cv2.dilate(gray, kernel, iterations=1)

                # OCR
                text = pytesseract.image_to_string(gray, config='--oem 1 --psm 6').strip()

                # Skip short fragments
                if len(text) < 4:
                    continue

                # Accumulate and stabilize text
                if text == last_text:
                    stable_counter += 1
                    accumulated_text += " " + text
                else:
                    stable_counter = 0
                    accumulated_text = text
                    last_text = text

                # Speak only if text is stable
                if stable_counter >= 3:
                    final_text = accumulated_text.strip()
                    if final_text:
                        print(f"Speaking: {final_text}")
                        speak(final_text)
                    accumulated_text = ""
                    stable_counter = 0

            except Exception as e:
                print(f"OCR Error: {e}")

        time.sleep(0.05)  # small loop delay for CPU efficiency
