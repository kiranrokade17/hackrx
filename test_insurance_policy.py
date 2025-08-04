import requests
import json
import time

def test_insurance_policy():
    """Test the exact input provided by user"""
    
    # API configuration
    api_url = "http://localhost:8005/hackrx/run"
    headers = {
        "Authorization": "Bearer fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a",
        "Content-Type": "application/json"
    }
    
    # Exact user input
    test_data = {
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
            "Are there sub-limits on room rent and ICU charges for Plan A?"
        ]
    }
    
    print("🧪 **Testing Insurance Policy PDF from Azure Blob Storage**")
    print(f"📄 Document URL: {test_data['documents'][:80]}...")
    print(f"❓ Questions: {len(test_data['questions'])}")
    print("-" * 80)
    
    start_time = time.time()
    
    try:
        print("⏳ Making API request... (This may take 30-60 seconds for large documents)")
        
        # Make API request with longer timeout
        response = requests.post(
            api_url, 
            headers=headers, 
            json=test_data, 
            timeout=120  # 2 minutes timeout
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"⏱️ Processing Time: {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Status: {result.get('status')}")
            print(f"📖 Document Info: {result.get('document_info')}")
            print("-" * 80)
            
            # Display answers
            answers = result.get('answers', [])
            if answers:
                for i, (question, answer) in enumerate(zip(test_data['questions'], answers)):
                    print(f"\n🔍 Question {i+1}: {question}")
                    print(f"💡 Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
                    print("-" * 40)
            else:
                print("❌ No answers received")
                
        elif response.status_code == 400:
            print(f"❌ Bad Request: {response.text}")
            error_data = response.json() if response.text else {}
            print(f"Error details: {error_data}")
            
        elif response.status_code == 401:
            print(f"❌ Unauthorized: {response.text}")
            
        elif response.status_code == 500:
            print(f"❌ Server Error: {response.text}")
            
        else:
            print(f"❌ Unexpected Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ ❌ Request timed out after 2 minutes")
        print("This could indicate:")
        print("- Large document taking too long to process")
        print("- Network issues downloading the PDF")
        print("- Gemini API rate limiting")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - API server might be down")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_insurance_policy()
