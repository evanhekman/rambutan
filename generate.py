import google.generativeai as genai
import os
import time

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

with open("new_york_cowboy.txt", "r") as f:
    prompt = f.read()

response = model.generate_content(prompt)

with open("new_york_cowboy_output.txt", "a") as f:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    f.write(f"\n\n{timestamp}\n")
    f.write(response.text)

print(response.text)
