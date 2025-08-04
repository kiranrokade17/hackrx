# Fresh API key test with new key
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

print(f"🔑 Testing NEW API key: {api_key}")
print(f"🔑 Key ends with: ...{api_key[-8:] if api_key else 'None'}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    print("🚀 Sending test request...")
    response = model.generate_content("Hello, respond with 'NEW API key is working perfectly!'")
    print(f"✅ SUCCESS: {response.text}")
    print("🎉 Your new API key is working!")
    print("💰 You have fresh quota available!")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    if "429" in str(e):
        print("⚠️  This API key also has quota issues")
        print("💡 Try creating another new Google account for a fresh API key")
    elif "401" in str(e) or "403" in str(e):
        print("⚠️  API key authentication failed")
        print("💡 Check if the API key is correct and enabled")
