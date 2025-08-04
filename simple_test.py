import requests
import json

# Your exact request data
url = "http://localhost:8003/hackrx/run"
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

print("=" * 80)
print("🔥 TESTING WITH YOUR TOKEN (WILL FAIL)")
print("=" * 80)

headers_wrong = {
    "Content-Type": "application/json",
    "Authorization": "Bearer fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a"
}

try:
    response = requests.post(url, headers=headers_wrong, json=data, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("✅ TESTING WITH CORRECT TOKEN (WILL WORK)")
print("=" * 80)

headers_correct = {
    "Content-Type": "application/json", 
    "Authorization": "Bearer api_key_1"
}

try:
    response = requests.post(url, headers=headers_correct, json=data, timeout=60)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"🎉 SUCCESS! Got {len(result.get('answers', []))} answers")
        print(f"💰 Used 1 API call for {len(data['questions'])} questions")
        
        # Show first 2 answers
        for i, answer in enumerate(result.get('answers', [])[:2]):
            print(f"\nQ{i+1}: {data['questions'][i]}")
            print(f"A{i+1}: {answer}")
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
