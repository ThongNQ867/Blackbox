import time
import cv2
from datetime import datetime
import os
import base64
from google import genai

client = genai.Client(api_key="AIzaSyCzFmE9-9tJKacn2dwdhmkWMqprGDgb45Q")

os.makedirs("captured", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Try to import Picamera2 (Raspberry Pi). If it's not available (e.g., on Windows),
# fall back to OpenCV's VideoCapture. This keeps the script runnable on dev
# machines and prevents lint errors about unused `cv2`.
try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except Exception:
    PICAMERA_AVAILABLE = False

def capture_image():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    image_path = f"captured/{timestamp}.jpg"
    # If running on a Raspberry Pi with picamera2 available, use it.
    if PICAMERA_AVAILABLE:
        picam = Picamera2()
        # create a simple preview configuration; adapt size as needed
        try:
            cfg = picam.create_preview_configuration({'size': (640, 480)})
            picam.configure(cfg)
        except Exception:
            # If create_preview_configuration isn't available or errors,
            # just start the camera with defaults
            pass

        picam.start()
        # short warm-up
        time.sleep(0.2)
        frame = picam.capture_array()
        picam.stop()

        # Write out using OpenCV (frame is a numpy array)
        cv2.imwrite(image_path, frame)
        return image_path

    # Fallback for development machines (Windows/macOS) using OpenCV
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()

    if ret:
        cv2.imwrite(image_path, frame)
        return image_path

    return None

def ask_gemini(image_path):
    # Read and encode image
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    base64_img = base64.b64encode(image_bytes).decode("utf-8")

    response = client.models.generate_content(
        model="gemini-2.0-flash",     # you can change this to gemini-2.0-flash
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": """**Persona and Role:**
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
* **Summary:** A concise, empowering wrap-up of the main takeaways."""},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64_img
                        }
                    }
                ]
            }
        ],
    )

    return response.text

while True:
    print("Capturing...")
    img_path = capture_image()

    if img_path:
        print("Sending to Gemini...")
        ans = ask_gemini(img_path)

        timestamp = os.path.splitext(os.path.basename(img_path))[0]

        result_txt = f"results/{timestamp}.txt"
        result_img = f"results/{timestamp}.jpg"

        with open(result_txt, "w", encoding="utf-8") as f:
            f.write(ans)

        # Copy image into results folder
        with open(img_path, "rb") as src, open(result_img, "wb") as dst:
            dst.write(src.read())

        print("Saved:", result_txt, result_img)

    print("Waiting 1 seconds...")
    time.sleep(60)
