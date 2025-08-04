"""
🔍 DEBUG API RESPONSE
Check the exact response format from the API
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8005"
API_KEY = "fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a"
INSURANCE_POLICY_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

def debug_api_response():
    print("🔍 Debugging API Response Format")
    print("=" * 50)
    
    payload = {
        "documents": INSURANCE_POLICY_URL,
        "questions": [
            "What is the grace period for premium payment?"
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/hackrx/run",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\nParsed JSON:")
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"JSON parsing error: {e}")
        
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    debug_api_response()
