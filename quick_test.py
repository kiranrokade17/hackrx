# Quick API key validation
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing API key: {api_key}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    response = model.generate_content("Hello, respond with 'API key working!'")
    print(f"✅ SUCCESS: {response.text}")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
