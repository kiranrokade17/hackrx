# 📚 **HackRX Document Q&A API - Complete Postman Testing Guide**

## 🚀 **Quick Start Checklist**
- ✅ API is running on `http://localhost:8005`
- ✅ Gemini model is healthy
- ✅ Authentication is working
- ✅ Ready for Postman testing!

---

## 📋 **Step 1: Import Postman Collection**

### Method 1: Import JSON File
1. Open Postman
2. Click **"Import"** button (top left)
3. Choose **"Upload Files"**
4. Select: `HackRX_Document_QA_API_Postman_Collection.json`
5. Click **"Import"**

### Method 2: Import by Raw JSON
1. Open Postman → **Import** → **Raw text**
2. Copy the entire content from `HackRX_Document_QA_API_Postman_Collection.json`
3. Paste and click **"Continue"**

---

## ⚙️ **Step 2: Configure Environment Variables**

The collection includes these pre-configured variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8005` | API server URL |
| `api_key` | `fcafc493f46a84b082decd38f0e64525e9992934678ffbdf2ee400b6f9afdb8a` | Authentication key |
| `resume_file` | `file:///D:/document/Ashish_Resume_final.pdf` | **⚠️ UPDATE THIS PATH** |
| `insurance_policy_url` | `https://hackrx.blob.core.windows.net/...` | Remote insurance PDF |

### 🔧 **Update Resume File Path:**
1. In Postman, go to **Collections** → **HackRX Document Q&A API**
2. Click **Variables** tab
3. Update `resume_file` with your actual PDF path:
   ```
   file:///C:/path/to/your/document.pdf
   ```

---

## 🧪 **Step 3: Testing Sequence**

### **Test 1: Health Check** ✅
**Endpoint:** `GET /health`
- **Purpose:** Verify API is running
- **Expected Response:**
  ```json
  {
    "status": "healthy",
    "services": {"gemini": "healthy"},
    "version": "2.1.0"
  }
  ```

### **Test 2: Single Question - Resume** 📄
**Endpoint:** `POST /hackrx/run`
- **Purpose:** Test basic document Q&A
- **Questions:** 1 question about resume
- **Expected:** Clean JSON with 1 answer

### **Test 3: Multiple Questions - Resume** 📄📄
**Endpoint:** `POST /hackrx/run`
- **Purpose:** Test batch processing
- **Questions:** 6 questions in ONE API call
- **Expected:** JSON array with 6 answers

### **Test 4: Insurance Policy Analysis** 🏥
**Endpoint:** `POST /hackrx/run`
- **Purpose:** Test complex document analysis
- **Questions:** 10 insurance questions in ONE call
- **Expected:** Detailed policy answers

### **Test 5: Authentication Tests** 🔐
- **Invalid API Key:** Should return `401 Unauthorized`
- **Missing Authorization:** Should return `401 Unauthorized`

### **Test 6: Error Handling** ⚠️
- **Invalid Document Path:** Should return error message
- **Empty Questions:** Should return validation error

---

## 📊 **Expected Response Format**

### ✅ **Successful Response:**
```json
{
  "success": true,
  "document_title": "Resume - Ashish Kumar",
  "questions_count": 6,
  "answers": [
    {
      "question": "What is the candidate's name and current position?",
      "answer": "The candidate's name is Ashish Kumar and he is currently working as a Senior Software Engineer."
    },
    {
      "question": "What are the main technical skills mentioned?",
      "answer": "The main technical skills include Python, JavaScript, React, Node.js, MongoDB, PostgreSQL, AWS, and Docker."
    }
  ],
  "processing_time": "3.2s",
  "model_used": "gemini-1.5-flash"
}
```

### ❌ **Error Response:**
```json
{
  "success": false,
  "error": "Document not found",
  "error_code": "DOCUMENT_NOT_FOUND",
  "timestamp": "2025-08-04T15:30:00Z"
}
```

---

## 🎯 **Key Testing Points**

### 1. **Batch Processing Efficiency** 
- ✅ **OLD WAY:** 10 questions = 10 API calls = 10x rate limits
- ✅ **NEW WAY:** 10 questions = 1 API call = Efficient!

### 2. **Response Quality**
- Professional, non-formatted JSON
- Context-aware answers
- Document-specific insights

### 3. **Authentication**
- Bearer token validation
- Secure API key system

### 4. **Error Handling**
- Clear error messages
- Proper HTTP status codes
- Graceful failure handling

---

## 🚨 **Troubleshooting Guide**

### **Issue: API not responding**
```bash
# Check if server is running
curl http://localhost:8005/health
```

### **Issue: Document not found**
- Verify file path is correct
- Use forward slashes: `file:///C:/path/to/file.pdf`
- Check file permissions

### **Issue: Authentication failed**
- Verify API key in collection variables
- Check Authorization header format: `Bearer {api_key}`

### **Issue: Gemini rate limits**
- Our batch processing should prevent this
- Check terminal logs for rate limit messages
- Wait 1 minute and retry

---

## 📈 **Performance Benchmarks**

| Test Case | Questions | Expected Time | Rate Limit Impact |
|-----------|-----------|---------------|-------------------|
| Single Question | 1 | 2-4 seconds | Minimal |
| Resume Analysis | 6 | 5-8 seconds | Low (1 API call) |
| Insurance Policy | 10 | 8-12 seconds | Low (1 API call) |

---

## 🎉 **Success Criteria**

### ✅ **API is working perfectly if:**
1. Health check returns `200 OK`
2. Single questions get accurate answers
3. Batch processing works (multiple questions in one call)
4. Authentication rejects invalid keys
5. Error handling is graceful
6. Response format is clean JSON

---

## 🔗 **Ready to Test!**

1. **Import the Postman collection**
2. **Update the resume file path**
3. **Start with Health Check**
4. **Test single question first**
5. **Try batch processing**
6. **Verify authentication**

**Your API is ready for professional document Q&A testing! 🚀**
