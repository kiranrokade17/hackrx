# Test the API endpoint with Python requests
import requests
import json

def test_api_endpoint():
    url = "http://localhost:8003/hackrx/run"
    
    # Test with YOUR token (will fail)
    headers_wrong = {
        "Content-Type": "application/json",
        "Authorization": "Bearer fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a"
    }
    
    # Test with CORRECT token (will work)
    headers_correct = {
        "Content-Type": "application/json",
        "Authorization": "Bearer api_key_1"
    }
    
    # Your exact test data with all 10 questions
    data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?",
            "What is the No Claim Discount (NCD) offered in this policy?",
            "Is there a benefit for preventive health check-ups?",
            "How does the policy define a 'Hospital'?",
            "What is the extent of coverage for AYUSH treatments?",
            "Are there any sub-limits on room rent and ICU charges for Plan A?"
        ]
    }
    
    
    print("🚀 Testing API endpoint with YOUR token...")
    print(f"URL: {url}")
    print(f"Headers: {headers_wrong}")
    print(f"Questions: {len(data['questions'])}")
    print("-" * 70)
    
    # Test 1: With your wrong token
    try:
        response = requests.post(url, headers=headers_wrong, json=data, timeout=60)
        
        print(f"❌ Status Code: {response.status_code}")
        print(f"� Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "="*70)
    print("🚀 Testing API endpoint with CORRECT token...")
    print(f"Headers: {headers_correct}")
    print("-" * 70)
    
    # Test 2: With correct token
    try:
        response = requests.post(url, headers=headers_correct, json=data, timeout=60)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"� Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 SUCCESS! API is working with BATCH PROCESSING")
            print(f"📊 Questions processed: {len(result.get('answers', []))}")
            print(f"💰 API calls used: 1 (instead of {len(data['questions'])})")
            
            # Show first 3 answers
            answers = result.get('answers', [])
            for i, (question, answer) in enumerate(zip(data['questions'][:3], answers[:3])):
                print(f"\nQ{i+1}: {question}")
                print(f"A{i+1}: {answer[:100]}{'...' if len(answer) > 100 else ''}")
        else:
            print("❌ API Error")
            print(f"📝 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_endpoint()
