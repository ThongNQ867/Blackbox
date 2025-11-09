# sudo apt update
# sudo apt install -y python3-opencv python3-picamera2 python3-pip
# pip install google-genai firebase-admin
# pip install flask


import time
import cv2
from datetime import datetime
import os
import base64
from google import genai

from picamera2 import Picamera2

client = genai.Client(api_key="AIzaSyCzFmE9-9tJKacn2dwdhmkWMqprGDgb45Q")

os.makedirs("captured", exist_ok=True)
os.makedirs("results", exist_ok=True)

# ----------------------------------------
# PiCamera2 Setup
# ----------------------------------------
picam = Picamera2()
config = picam.create_still_configuration()
picam.configure(config)
picam.start()


# ----------------------------------------
# Capture a single frame with Pi Camera
# ----------------------------------------
def capture_image():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    image_path = f"captured/{timestamp}.jpg"

    frame = picam.capture_array()     # <-- PiCamera2 capture
    cv2.imwrite(image_path, frame)

    return image_path


# ----------------------------------------
# Multi-image Gemini request
# ----------------------------------------
def ask_gemini_multi(image_paths):
    parts = [{"text": """**Persona and Role:**
You are a highly engaging senior professor...
(Your long prompt stays exactly the same)
"""}]

    # Add each image
    for img_path in image_paths:
        with open(img_path, "rb") as f:
            img_bytes = f.read()

        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_bytes).decode("utf-8")
            }
        })

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[{"role": "user", "parts": parts}]
    )

    return response.text


# ----------------------------------------
# Main Loop
# ----------------------------------------
for i in range(1):
    print("Capturing 3 images...")
    imgs = []

    for i in range(10):
        img_path = capture_image()
        print("Captured:", img_path)
        imgs.append(img_path)
        time.sleep(1)

    print("Sending all images to Gemini...")
    ans = ask_gemini_multi(imgs)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    result_txt = f"results/{timestamp}.txt"

    with open(result_txt, "w", encoding="utf-8") as f:
        f.write(ans)

    print("Saved result:", result_txt)
    time.sleep(3)
