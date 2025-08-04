# HackRX Document Q&A API - Production Ready

🚀 **AI-powered document analysis API with Google Gemini integration**

## Features
- ✅ **Batch Processing** - Multiple questions in single API call
- ✅ **PDF Support** - Large document processing (up to 50MB)
- ✅ **Real AI Analysis** - Google Gemini 1.5 Flash integration
- ✅ **Secure Authentication** - Bearer token based
- ✅ **Production Ready** - Optimized for deployment
- ✅ **Error Handling** - Comprehensive error responses

## Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.template .env
# Add your GEMINI_API_KEY and ALLOWED_API_KEYS

# 3. Run the server
python advanced_document_api_v2.py

# 4. Test the API
curl http://localhost:8000/health
```

## API Usage
```bash
POST /hackrx/run
Content-Type: application/json
Authorization: Bearer your_api_key

{
    "documents": "https://example.com/document.pdf",
    "questions": [
        "What is the main topic?",
        "What are the key findings?"
    ]
}
```

## Deployment
- **Render:** Configuration ready with render.yaml
- **Docker:** Dockerfile included
- **Environment:** All secrets managed via .env
- **Monitoring:** Health check endpoint available

## Performance
- **Response Time:** 3-8 seconds typical
- **Document Size:** Up to 50MB PDFs
- **Questions:** 1-25 per request (recommended)
- **Accuracy:** High-quality AI analysis

## Security
- API key authentication
- Environment-based configuration
- No hardcoded secrets
- CORS properly configured

---
**Built for HackRX** | **Powered by Google Gemini AI**
