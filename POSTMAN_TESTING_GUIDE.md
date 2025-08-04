# 🚀 **Postman Testing Guide for HackRX Document Q&A APIs**

## 📋 **Quick Setup Steps**

### 1. **Import Collection into Postman**
1. Open Postman application
2. Click **"Import"** button (top left)
3. Choose **"Upload Files"** 
4. Select the file: `Postman_Collection_HackRX_APIs.json`
5. Click **"Import"**

### 2. **Verify Collection Variables**
After importing, you should see these variables are set:
- `base_url_main`: `http://localhost:8000`
- `base_url_advanced`: `http://localhost:8005`  
- `api_key`: `fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a`

## 🧪 **Testing Sequence**

### **Step 1: Health Checks**
Test these endpoints first to ensure APIs are running:

**✅ Main API Health Check**
- **Method**: GET
- **URL**: `http://localhost:8000/health`
- **Expected**: Status 200 with service health details

**✅ Advanced API Health Check**  
- **Method**: GET
- **URL**: `http://localhost:8005/health`
- **Expected**: Status 200 with AI model status

### **Step 2: Basic Document Processing**

**🔍 Single Question Test (Advanced API)**
- **Method**: POST
- **URL**: `http://localhost:8005/hackrx/run`
- **Headers**: 
  ```
  Authorization: Bearer fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a
  Content-Type: application/json
  ```
- **Body**:
  ```json
  {
    "documents": "file:///D:/document/Ashish_Resume_final.pdf",
    "questions": [
      "What is the candidate's name?"
    ]
  }
  ```
- **Expected**: Status 200 with AI-generated answer

### **Step 3: Multi-Question Processing**

**🎯 Multiple Questions Test**
- **Method**: POST  
- **URL**: `http://localhost:8005/hackrx/run`
- **Headers**: Same as above
- **Body**:
  ```json
  {
    "documents": "file:///D:/document/Ashish_Resume_final.pdf",
    "questions": [
      "What is the candidate's current job title?",
      "Which programming languages does the candidate know?",
      "What is the candidate's educational qualification?",
      "How many years of experience does the candidate have?",
      "What are the candidate's key technical skills?"
    ]
  }
  ```
- **Expected**: Status 200 with array of 5 detailed answers

### **Step 4: Main API Testing (RAG-based)**

**🧠 RAG Processing Test**
- **Method**: POST
- **URL**: `http://localhost:8000/hackrx/run`  
- **Headers**: Same authorization
- **Body**: Same as multiple questions test
- **Expected**: Status 200 with RAG-processed answers

### **Step 5: Error Testing**

**❌ Invalid API Key Test**
- **Method**: POST
- **URL**: `http://localhost:8005/hackrx/run`
- **Headers**: 
  ```
  Authorization: Bearer invalid_key_123
  Content-Type: application/json
  ```
- **Body**: Any valid request body
- **Expected**: Status 401 "Invalid API key"

## 📊 **Expected Response Formats**

### **Successful Response**
```json
{
  "answers": [
    "The candidate's name is Ashish Pratap Singh...",
    "The main technical skills include C/C++, Java, Python..."
  ],
  "status": "success",
  "document_info": {
    "total_pages": 2,
    "title": "",
    "author": "", 
    "file_type": "PDF"
  }
}
```

### **Error Response**
```json
{
  "detail": "Invalid API key"
}
```

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

**1. Connection Refused**
- ✅ **Check**: APIs are running on correct ports
- ✅ **Run**: `python main.py` (port 8000) and `python advanced_document_api_v2.py` (port 8005)

**2. 401 Unauthorized**  
- ✅ **Check**: API key in Authorization header
- ✅ **Format**: `Bearer fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a`

**3. 400 Bad Request**
- ✅ **Check**: JSON body format is correct
- ✅ **Check**: Document path exists: `D:/document/Ashish_Resume_final.pdf`

**4. 500 Internal Server Error**
- ✅ **Check**: Gemini API key is valid in `.env` file
- ✅ **Check**: Required packages are installed

## 🎯 **Performance Testing**

### **Response Time Expectations**
- **Health checks**: < 100ms
- **Single question**: 3-10 seconds  
- **Multiple questions**: 10-30 seconds
- **Large documents**: 30-60 seconds

### **Batch Testing**
Test with different document types:
```json
{
  "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
  "questions": ["What is this document about?"]
}
```

## 📝 **Testing Checklist**

- [ ] Import Postman collection successfully
- [ ] Health checks return 200 status  
- [ ] Single question test works
- [ ] Multi-question test works
- [ ] Authentication works with valid key
- [ ] Authentication fails with invalid key
- [ ] Both main API and advanced API respond
- [ ] Response format is correct JSON
- [ ] Processing times are acceptable
- [ ] Error handling works properly

## 🚀 **Ready to Test!**

Your APIs are now ready for comprehensive testing in Postman. Start with health checks and work through the test sequence above.

For any issues, check the terminal logs where the APIs are running for detailed error messages.
