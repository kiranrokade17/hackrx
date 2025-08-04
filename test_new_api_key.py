import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_new_gemini_api_key():
    """Test if the new Gemini API key works"""
    
    print("🧪 **Testing New Gemini API Key**")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from .env
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "YOUR_NEW_GEMINI_API_KEY_HERE":
        print("❌ Please update GEMINI_API_KEY in .env file with your actual API key")
        return False
    
    print(f"🔑 Testing API Key: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        # Test 1: Configure Gemini
        genai.configure(api_key=api_key)
        print("✅ API Key configured successfully")
        
        # Test 2: Initialize model
        model = genai.GenerativeModel("gemini-1.5-flash")
        print("✅ Model initialized successfully")
        
        # Test 3: Simple generation test
        response = model.generate_content("Hello, can you confirm this API key is working?")
        print("✅ Test generation successful")
        print(f"🤖 Response: {response.text[:100]}...")
        
        print("\n" + "=" * 50)
        print("🎉 **New Gemini API Key is working perfectly!**")
        print("✅ You can now restart your API server")
        return True
        
    except Exception as e:
        print(f"❌ API Key test failed: {e}")
        print("\n💡 **Troubleshooting:**")
        print("1. Verify the API key is correct")
        print("2. Check if the API key has proper permissions")
        print("3. Ensure you haven't exceeded quota limits")
        return False

def test_api_server_with_new_key():
    """Test if the API server works with new key"""
    
    print("\n🧪 **Testing API Server with New Key**")
    print("=" * 50)
    
    # Test configuration
    api_key = "fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    test_data = {
        "documents": "file:///D:/document/Ashish_Resume_final.pdf",
        "questions": ["What is the candidate's name?"]
    }
    
    try:
        print("⏳ Testing API server...")
        response = requests.post(
            "http://localhost:8005/hackrx/run", 
            headers=headers, 
            json=test_data, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get('answers', [])
            if answers and not any("Error generating answer: 429" in answer for answer in answers):
                print("✅ API server working with new Gemini key!")
                print(f"🎯 Received answer: {answers[0][:100]}...")
                return True
            else:
                print("❌ Still getting rate limit errors")
                return False
        else:
            print(f"❌ API server error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        print("💡 Make sure to restart the API server after updating .env")
        return False

if __name__ == "__main__":
    # Test the Gemini API key directly
    if test_new_gemini_api_key():
        print("\n" + "🔄" * 20)
        print("Now restart your API server and test again!")
        print("🔄" * 20)
    else:
        print("\n❌ Fix the API key issue before proceeding")
