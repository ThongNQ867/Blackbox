import cv2
import google.generativeai as genai

# ✅ same API setup
genai.configure(api_key="AIzaSyCu2NG2rwJv41HHwkETOmIFU7Kc_MgQgcU")
model = genai.GenerativeModel("gemini-2.0-flash")

# ✅ capture from laptop webcam
cam = cv2.VideoCapture(0)

ret, frame = cam.read()
cv2.imwrite("frame.jpg", frame)
cam.release()

print("✅ Captured frame.jpg")

# ✅ send to Gemini
with open("frame.jpg", "rb") as f:
    img = f.read()

response = model.generate_content([
    "Explain the information inside this image.Explain all the terms, formular and the meaning of it.",
    {"mime_type": "image/jpeg", "data": img}
])

print("\n✅ Gemini Response:\n")
print(response.text)
