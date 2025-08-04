"""
🧪 Test Simple Response Format
Quick test to verify the API returns only the answers array as requested
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8005"
API_KEY = "fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a"
INSURANCE_POLICY_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

def test_simple_response_format():
    print("🧪 Testing Simple Response Format")
    print("=" * 50)
    
    payload = {
        "documents": INSURANCE_POLICY_URL,
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?"
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
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n🎯 EXPECTED FORMAT:")
            print('{"answers": ["answer1", "answer2"]}')
            
            print("\n📋 ACTUAL RESPONSE:")
            print(json.dumps(result, indent=2))
            
            # Verify it's the correct format
            if "answers" in result and len(result) == 1:
                print("\n✅ SUCCESS! Response format is exactly as requested")
                print(f"✅ Contains only 'answers' field")
                print(f"✅ Number of answers: {len(result['answers'])}")
                
                # Show answers
                for i, answer in enumerate(result['answers'], 1):
                    print(f"\n📝 Answer {i}:")
                    print(f"   {answer[:100]}...")
            else:
                print("\n❌ ERROR: Response format still contains extra fields")
                print(f"   Fields found: {list(result.keys())}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_simple_response_format()
