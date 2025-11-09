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

picam = Picamera2()
config = picam.create_still_configuration()
picam.configure(config)
picam.start()


def capture_image():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    image_path = f"captured/{timestamp}.jpg"

    frame = picam.capture_array()     # PiCamera2 capture
    cv2.imwrite(image_path, frame)

    return image_path

#prompt setup?
def ask_gemini_multi(image_paths):
    parts = [{"text": """**System / Instruction Message:**
You are an expert educational assistant designed to generate high-quality study notes for students. Your task is to analyze the provided classroom images (which may include projected presentation slides, whiteboard notes, equations, or diagrams) and produce detailed, structured notes that help a student understand the material thoroughly.


**User Message:**
Analyze all the provided images of classroom material. Each image may include:
- A presentation projected on a screen
- A whiteboard with written formulas, key terms, and short explanations

Your goal is to:
1. **Identify the topic(s)** being taught in each image.
2. **Explain and elaborate** on these topics in clear, well-organized student notes.
3. **For each formula or concept mentioned:**
   - Explain what it represents.
   - Describe its **purpose and context of use**.
   - Provide **1–2 relevant real-world examples** that fit the apparent scope and level of the class (e.g., high school physics, introductory calculus, etc.).
4. **If diagrams or figures appear**, briefly describe what they illustrate and how they relate to the topic.
5. **Use consistent sectioning** and structure the notes for readability.

**Output format:**
Use the following structure for your response:
---
### Topic: [Title inferred from image]
**Overview:**
[Brief explanation of the concept or topic]

**Key Concepts and Formulas:**
- *Formula/Concept 1:* [Name]  
  **Explanation:** [What it means, what it’s used for, pretext]  
  **Example(s):** [One or two relevant real-world examples]

- *Formula/Concept 2:* ...

**Additional Notes:**
[Any contextual remarks, hints, or deeper connections to related material]

---

If multiple topics are present in different images, separate them clearly using the same structure.
Ensure that your notes are pedagogical, accurate, and easy for students to learn from.
"""}]

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



for i in range(1):
    time.sleep(3)
    print("Capturing images...")
    imgs = []

    for i in range(20):
        img_path = capture_image()
        print("Captured:", img_path)
        imgs.append(img_path)
        time.sleep(120)

    print("Sending all images to Gemini...")
    ans = ask_gemini_multi(imgs)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    result_txt = f"results/{timestamp}.txt"

    with open(result_txt, "w", encoding="utf-8") as f:
        f.write(ans)

    print("Saved result:", result_txt)

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("hackumass1-firebase-adminsdk-fbsvc-ddd3fb9045.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_gemini_text(text):
    db.collection("gemini_results").add({
        "timestamp": str(datetime.now()),
        "gemini_text": text
    })

save_gemini_text(ans)
print("Saved Gemini text to Firestore.")
