import requests
import json

def test_response_format():
    """Test to show the exact response format"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a"
    }
    
    body = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?"
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:8006/hackrx/run",
            headers=headers,
            json=body,
            timeout=30
        )
        
        print("📊 RESPONSE STATUS:", response.status_code)
        print("📋 RESPONSE FORMAT:")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
            
            # Check the structure
            print(f"\n✅ Response contains 'answers' key: {'answers' in result}")
            print(f"✅ Answers is a list: {isinstance(result.get('answers'), list)}")
            print(f"✅ Number of answers: {len(result.get('answers', []))}")
            print(f"✅ No extra metadata: {len(result.keys()) == 1}")
            
        else:
            print("❌ ERROR:", response.text)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_response_format()
