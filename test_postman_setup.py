import requests
import json

def test_postman_setup():
    """Test script to verify APIs are ready for Postman testing"""
    
    print("🧪 **HackRX API Postman Readiness Test**")
    print("=" * 50)
    
    # Test configuration
    api_key = "fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Advanced API Health Check
    print("\n🔍 **Test 1: Advanced API Health Check**")
    try:
        response = requests.get("http://localhost:8005/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2: Advanced API Root Endpoint
    print("\n🔍 **Test 2: Advanced API Root Endpoint**")
    try:
        response = requests.get("http://localhost:8005/", timeout=5)
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"✅ API Name: {result.get('message')}")
        print(f"✅ Version: {result.get('version')}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: Authentication Test
    print("\n🔍 **Test 3: Authentication Test**")
    test_data = {
        "documents": "file:///D:/document/Ashish_Resume_final.pdf",
        "questions": ["What is this document about?"]
    }
    
    try:
        response = requests.post(
            "http://localhost:8005/hackrx/run", 
            headers=headers, 
            json=test_data, 
            timeout=30
        )
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Answers received: {len(result.get('answers', []))}")
            print(f"✅ Document info: {result.get('document_info')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 4: Invalid API Key Test
    print("\n🔍 **Test 4: Invalid API Key Test**")
    bad_headers = {
        "Authorization": "Bearer invalid_key_123",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "http://localhost:8005/hackrx/run", 
            headers=bad_headers, 
            json=test_data, 
            timeout=10
        )
        print(f"✅ Status: {response.status_code} (should be 401)")
        print(f"✅ Error message: {response.json()}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print("📋 **Postman Setup Instructions:**")
    print("1. Import the collection: Postman_Collection_HackRX_APIs.json")
    print("2. Verify these URLs work:")
    print("   - Health Check: http://localhost:8005/health")
    print("   - Main API: http://localhost:8005/hackrx/run")
    print("3. Use this API key in Authorization header:")
    print(f"   Bearer {api_key}")
    print("4. Test with your resume file path:")
    print("   file:///D:/document/Ashish_Resume_final.pdf")
    print("\n🚀 **Ready for Postman testing!**")

if __name__ == "__main__":
    test_postman_setup()
