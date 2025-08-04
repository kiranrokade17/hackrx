import requests
import json

# Test the advanced document API with real document processing
def test_advanced_document_api():
    # API configuration
    api_url = "http://localhost:8005/hackrx/run"
    headers = {
        "Authorization": "Bearer fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a",
        "Content-Type": "application/json"
    }
    
    # Test data with your resume
    test_data = {
        "documents": "file:///D:/document/Ashish_Resume_final.pdf",
        "questions": [
            "What is the candidate's name and current position?",
            "What are the main technical skills mentioned in this resume?",
            "What is the candidate's educational background?",
            "What companies has this person worked for?",
            "What programming languages and technologies does this candidate know?",
            "What are the candidate's key achievements or projects?"
        ]
    }
    
    print("🚀 Testing Advanced Document API with Real PDF Analysis...")
    print(f"📄 Document: {test_data['documents']}")
    print(f"❓ Questions: {len(test_data['questions'])}")
    print("-" * 60)
    
    try:
        # Make API request
        response = requests.post(api_url, headers=headers, json=test_data, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Status: {result.get('status')}")
            print(f"📖 Document Info: {result.get('document_info')}")
            print("-" * 60)
            
            # Display answers
            for i, (question, answer) in enumerate(zip(test_data['questions'], result['answers'])):
                print(f"\n🔍 Question {i+1}: {question}")
                print(f"💡 Answer: {answer}")
                print("-" * 40)
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out - this is normal for large documents")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_advanced_document_api()
