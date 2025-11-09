import google.generativeai as genai

genai.configure(api_key="AIzaSyCu2NG2rwJv41HHwkETOmIFU7Kc_MgQgcU")

model = genai.GenerativeModel("gemini-2.0-flash")

with open("hello.png", "rb") as f:
    img = f.read()

response = model.generate_content([
    "Explain the information inside this image.Explain all the terms, formular and the meaning of it.",
    {"mime_type": "image/jpeg", "data": img}
])

print(response.text)