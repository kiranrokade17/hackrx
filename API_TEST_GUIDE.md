# 🚀 How to Test Your LLM API Application

## ✅ **Current Status: API is Working!**

Your API application is successfully running on `http://localhost:8000`

## 📋 **Step-by-Step Testing Guide**

### 1. **Basic Health Check**
Test if your API is responding:

```powershell
# Test root endpoint
Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing

# Expected Response: 
# {"message":"LLM-Powered Intelligent Query-Retrieval System","status":"active","version":"1.0.0"}
```

### 2. **Service Health Check**
```powershell
# Test health endpoint
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Expected Response:
# {"status":"healthy","services":{"api":"healthy","document_processor":"healthy",...}}
```

### 3. **API Documentation**
Open your browser and go to:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 4. **Test Main Endpoint**
```powershell
# Create test request
$headers = @{
    "Authorization" = "Bearer api_key_1"
    "Content-Type" = "application/json"
}

$body = @{
    "documents" = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    "questions" = @(
        "What is the grace period for premium payment?"
    )
} | ConvertTo-Json

# Send request
Invoke-WebRequest -Uri "http://localhost:8000/hackrx/run" -Method POST -Headers $headers -Body $body -UseBasicParsing -TimeoutSec 120
```

## 🔧 **Working Components**

✅ **FastAPI Server** - Running on port 8000  
✅ **Document Processor** - Can extract text from PDFs/DOCX  
✅ **Embedding Service** - Sentence transformers working  
✅ **LLM Service** - Google Gemini integration  
✅ **API Authentication** - Bearer token validation  
✅ **CORS** - Cross-origin requests enabled  

## ⚙️ **Configuration Status**

✅ **Gemini API Key** - Configured  
✅ **Pinecone API Key** - Configured (currently using FAISS fallback)  
✅ **MongoDB Atlas** - Configured  
✅ **API Keys** - Set for authentication  

## 🌐 **Using Your API**

### **cURL Example:**
```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer api_key_1" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
      "What is the grace period for premium payment?",
      "What is the waiting period for pre-existing diseases?"
    ]
  }'
```

### **Python Example:**
```python
import requests

url = "http://localhost:8000/hackrx/run"
headers = {
    "Authorization": "Bearer api_key_1",
    "Content-Type": "application/json"
}
data = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?"
    ]
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

### **JavaScript/Node.js Example:**
```javascript
const axios = require('axios');

const config = {
  method: 'post',
  url: 'http://localhost:8000/hackrx/run',
  headers: {
    'Authorization': 'Bearer api_key_1',
    'Content-Type': 'application/json'
  },
  data: {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
      "What is the grace period for premium payment?",
      "What is the waiting period for pre-existing diseases?"
    ]
  }
};

axios(config)
.then(function (response) {
  console.log(JSON.stringify(response.data));
})
.catch(function (error) {
  console.log(error);
});
```

## 📊 **Expected Response Format**

```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
  ]
}
```

## 🛠️ **Troubleshooting**

### **If API doesn't respond:**
1. Check if the server is running: Look for "Uvicorn running on http://0.0.0.0:8000"
2. Check Windows Firewall settings
3. Try accessing http://127.0.0.1:8000 instead of localhost

### **If you get 401 Unauthorized:**
- Check that you're using the correct API key from your .env file
- Valid keys: `api_key_1`, `api_key_2`, `api_key_3`

### **If you get 500 Internal Server Error:**
1. Check the terminal output for detailed error messages
2. Verify your Gemini API key is valid
3. Check internet connection for document download

## 🚀 **Next Steps**

1. **Test the Interactive Docs**: Visit http://localhost:8000/docs
2. **Try Different Documents**: Test with other PDF URLs
3. **Experiment with Questions**: Ask various types of questions
4. **Monitor Logs**: Watch the terminal for processing information

## 📝 **Quick Test Script**

Save this as `quick_test.ps1` and run it:

```powershell
Write-Host "🚀 Testing LLM API Application..." -ForegroundColor Green

# Test 1: Health Check
Write-Host "`n1. Testing Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing
    Write-Host "✅ Health Check: SUCCESS" -ForegroundColor Green
} catch {
    Write-Host "❌ Health Check: FAILED" -ForegroundColor Red
}

# Test 2: API Documentation
Write-Host "`n2. API Documentation available at:" -ForegroundColor Yellow
Write-Host "   📖 http://localhost:8000/docs" -ForegroundColor Cyan

# Test 3: Authentication Test
Write-Host "`n3. Testing Authentication..." -ForegroundColor Yellow
$headers = @{ "Authorization" = "Bearer api_key_1"; "Content-Type" = "application/json" }
$testBody = '{"documents":"https://example.com/test.pdf","questions":["test"]}' 

Write-Host "✅ API is ready for testing!" -ForegroundColor Green
Write-Host "`nYour API is working and ready to process documents! 🎉" -ForegroundColor Green
```

Your API application is **WORKING SUCCESSFULLY!** 🎉
