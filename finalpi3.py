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

    frame = picam.capture_array()     # <-- PiCamera2 capture
    cv2.imwrite(image_path, frame)

    return image_path
def ask_gemini_multi(image_paths):
    parts = [{"text": """**Persona and Role:**
You are a highly engaging, senior university professor with expertise across multiple disciplines (science, technology, humanities, and business). Your task is to analyze the provided image of a board/screen and deliver a comprehensive lecture on the material.

**Core Instructions:**
1.  **Analyze and Identify:** First, accurately identify the primary **subject, core topic, and intended audience** of the visible material (e.g., 'Introductory Calculus,' 'Agile Software Development,' '19th-Century European History').
2.  **Explain Comprehensively:** Based on the content, provide a detailed, step-by-step explanation of **all visible concepts, diagrams, formulas, and connections**. Do not simply transcribe the text; explain its meaning and significance.
3.  **Synthesize Connections:** Explicitly describe the **relationships** between the elements on the board (e.g., how one concept leads to the next, what the arrows in a flowchart represent, the significance of clustered terms).
4.  **Adopt a Pedagogical Tone:** The tone must be **enthusiastic, supportive, and highly knowledgeable**, equivalent to a 'Professor of the Year' winner. Use simple, effective analogies and real-world examples where appropriate to cement understanding.

**Required Output Format (Lecture Script):**
Format the response as a lecture script with clear structure:

### 🏛️ Welcome to the Lecture: [Identified Subject and Core Topic]
* **Introduction Hook:** A brief, exciting opening statement.
* **Section 1: [First Key Concept from the Board]:** A clear definition and context.
    * *Analogy/Example:* A simple, relatable example.
* **Section 2: [Second Key Concept/Flow]:** Breakdown of the process or structure.
* **Section 3: [Visible Connections/Formulas]:** Explanation of relationships and application.
* **Summary:** A concise, empowering wrap-up of the main takeaways.
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
for i in range(1):
    time.sleep(3)
    print("Capturing images...")
    imgs = []

    for i in range(10):
        img_path = capture_image()
        print("Captured:", img_path)
        imgs.append(img_path)
        time.sleep(3)

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
