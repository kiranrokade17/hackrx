# Test new API key - FRESH
import os
import google.generativeai as genai

# Clear environment and reload
os.environ.pop('GEMINI_API_KEY', None)

# Load fresh
from dotenv import load_dotenv
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
print(f"🔑 Testing API key: {api_key}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    response = model.generate_content("Respond with: 'NEW API KEY IS WORKING!'")
    print(f"✅ SUCCESS: {response.text}")
    print("🎉 Your new API key works perfectly!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    if "429" in str(e):
        print("❌ Rate limit exceeded on this key too")
    elif "expired" in str(e).lower() or "invalid" in str(e).lower():
        print("❌ API key is expired or invalid")
    else:
        print("❌ Other error occurred")
