# HackRX Document Q&A API

A production-ready AI-powered document analysis API that processes PDFs and answers questions using Google Gemini.

## 🚀 Features

- **AI-Powered Q&A**: Uses Google Gemini for intelligent document analysis
- **Batch Processing**: Multiple questions in single API call (10x more efficient)
- **Multiple Document Sources**: Supports URLs and local files
- **Authentication**: Bearer token security
- **Clean JSON Responses**: Simple `{"answers": [...]}` format
- **Production Ready**: Docker, Render deployment support

## 📋 Quick Start

### 1. Installation
```bash
git clone https://github.com/kiranrokade17/hackrx.git
cd hackrx
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp .env.example .env
# Update .env with your API keys
```

### 3. Run
```bash
python main.py
```

API will be available at: `http://localhost:8000`

## 🧪 Testing

### Health Check
```bash
GET http://localhost:8000/health
```

### Document Q&A
```bash
POST http://localhost:8000/hackrx/run
Headers: Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the main topic?",
    "What are the key points?"
  ]
}
```

### Response Format
```json
{
  "answers": [
    "Answer to question 1",
    "Answer to question 2"
  ]
}
```

## 🔧 Environment Variables

```env
GEMINI_API_KEY=your_gemini_api_key
ALLOWED_API_KEYS=key1,key2,key3
LOG_LEVEL=INFO
MAX_DOCUMENT_SIZE=52428800
```

## 🚀 Deployment

### Render
```bash
# Configure environment variables in Render dashboard
# Deploy automatically from GitHub
```

### Docker
```bash
docker build -t hackrx-api .
docker run -p 8000:8000 hackrx-api
```

## 📖 API Documentation

- **Interactive Docs**: `http://localhost:8000/docs`
- **Postman Collection**: `docs/HackRX_API.postman_collection.json`
- **Testing Guide**: `docs/POSTMAN_GUIDE.md`

## 🎯 Key Benefits

- **90% Reduction** in API calls through batch processing
- **Production-ready** authentication and error handling
- **Scalable** architecture for multiple document types
- **Clean responses** with no unnecessary metadata

## 📊 Performance

- **Response Time**: 3-10 seconds for complex documents
- **Batch Efficiency**: 1 API call for multiple questions
- **Memory Optimized**: Streaming document processing
- **Rate Limit Friendly**: Intelligent API usage
