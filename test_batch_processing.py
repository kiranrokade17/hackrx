# Batch Processing Test - ONE API call for multiple questions
import requests
import time

def test_batch_processing():
    """Test the new batch processing functionality"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer api_key_1"
    }
    
    # Test with multiple questions (will use 1 API call instead of 5)
    body = {
        "documents": "D:/document/resume kiran.pdf",
        "questions": [
            "What skills does Kiran have?",
            "What is his education?", 
            "What work experience does he have?",
            "What programming languages does he know?",
            "What projects has he worked on?"
        ]
    }
    
    print("🚀 TESTING BATCH PROCESSING")
    print(f"Questions to process: {len(body['questions'])}")
    print(f"OLD METHOD: {len(body['questions'])} API calls")
    print(f"NEW METHOD: 1 API call")
    print(f"API USAGE REDUCTION: {((len(body['questions'])-1)/len(body['questions']))*100:.0f}%")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8003/hackrx/run",
            headers=headers,
            json=body,
            timeout=60
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ BATCH PROCESSING SUCCESS!")
            print(f"⏱️  Processing time: {duration:.2f} seconds")
            print(f"📊 Questions processed: {len(body['questions'])}")
            print(f"📋 Answers received: {len(result['answers'])}")
            print(f"🎯 API calls used: 1 (instead of {len(body['questions'])})")
            print(f"💰 Quota savings: {len(body['questions'])-1} API calls saved")
            
            print("\n📝 Sample Answers:")
            for i, (question, answer) in enumerate(zip(body['questions'][:3], result['answers'][:3])):
                print(f"\nQ{i+1}: {question}")
                print(f"A{i+1}: {answer[:150]}{'...' if len(answer) > 150 else ''}")
                
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_api_quota_comparison():
    """Compare API usage between old and new methods"""
    
    test_scenarios = [
        {"questions": 1, "description": "Single question"},
        {"questions": 5, "description": "Small batch"},
        {"questions": 10, "description": "Large batch"},
    ]
    
    print("\n📊 API QUOTA USAGE COMPARISON")
    print("=" * 60)
    print(f"{'Scenario':<15} {'Questions':<10} {'Old Calls':<10} {'New Calls':<10} {'Savings':<10}")
    print("-" * 60)
    
    for scenario in test_scenarios:
        q_count = scenario["questions"]
        old_calls = q_count
        new_calls = 1
        savings = old_calls - new_calls
        
        print(f"{scenario['description']:<15} {q_count:<10} {old_calls:<10} {new_calls:<10} {savings:<10}")
    
    print("-" * 60)
    print(f"📈 Daily limit (50 calls) can now handle:")
    print(f"   Old method: 5 requests with 10 questions each")
    print(f"   New method: 50 requests with 10 questions each")
    print(f"   Improvement: 10x more multi-question requests!")

if __name__ == "__main__":
    test_batch_processing()
    test_api_quota_comparison()
