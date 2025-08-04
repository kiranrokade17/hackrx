import requests
import json
import time

def test_batch_optimized_api():
    """Test the batch-optimized API with insurance policy"""
    
    # API configuration
    api_url = "http://localhost:8005/hackrx/run"
    headers = {
        "Authorization": "Bearer fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a",
        "Content-Type": "application/json"
    }
    
    # Test with smaller set to demonstrate batch processing
    test_data = {
        "documents": "file:///D:/document/Ashish_Resume_final.pdf",  # Use local file to avoid quota hit
        "questions": [
            "What is the candidate's name?",
            "What programming languages does the candidate know?",
            "What is the candidate's current job title?"
        ]
    }
    
    print("🧪 **Testing BATCH-OPTIMIZED API**")
    print(f"📄 Document: {test_data['documents']}")
    print(f"❓ Questions: {len(test_data['questions'])}")
    print("-" * 80)
    
    start_time = time.time()
    
    try:
        print("⏳ Making API request with BATCH processing...")
        
        response = requests.post(
            api_url, 
            headers=headers, 
            json=test_data, 
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"⏱️ Processing Time: {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Status: {result.get('status')}")
            print(f"📖 Document Info: {result.get('document_info')}")
            print(f"🔥 API Calls Used: {result.get('api_calls_used', 'N/A')}")
            print("-" * 80)
            
            # Display answers
            answers = result.get('answers', [])
            if answers:
                for i, (question, answer) in enumerate(zip(test_data['questions'], answers)):
                    print(f"\n🔍 Question {i+1}: {question}")
                    # Check if this is a batch-generated answer or individual
                    if "Error generating answer: 429" in answer:
                        print(f"❌ Rate Limited: {answer}")
                    else:
                        print(f"✅ Answer: {answer[:150]}{'...' if len(answer) > 150 else ''}")
                    print("-" * 40)
            else:
                print("❌ No answers received")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_batch_optimized_api()
