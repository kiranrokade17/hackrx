# Clean up script to remove unwanted files for sharing
Write-Host "🧹 CLEANING UP API APPLICATION FOR SHARING..." -ForegroundColor Yellow

# Files to remove
$filesToRemove = @(
    "debug_chunks.py",
    "debug_detailed.py", 
    "debug_env.py",
    "debug_name.ps1",
    "debug_test.ps1",
    "quick_test.py",
    "simple_api.py",
    "simple_confirmation.ps1",
    "simple_debug.ps1",
    "simple_test.ps1",
    "simple_verification.ps1",
    "startup.py",
    "setup.ps1",
    "test_api.ps1",
    "test_api_key.py",
    "test_ashish_clean.ps1",
    "test_ashish_resume.ps1",
    "test_clean_insurance.ps1",
    "test_format_verification.ps1",
    "test_fresh_env.py",
    "test_multi_questions.ps1",
    "test_name_only.ps1",
    "test_new_api_key.ps1",
    "test_raw_response.ps1",
    "test_services.py",
    "verify_gemini_flash.ps1",
    "postman_verification_test.ps1",
    "format_confirmation.ps1",
    "format_success_summary.ps1",
    "JSON_ERROR_FIX.md",
    "JSON_ERROR_SOLUTION.md",
    "POSTMAN_DEBUG_GUIDE.md",
    "POSTMAN_INSTANT_FIX.md",
    "POSTMAN_JSON_FIX.md",
    ".env",
    ".env.backup",
    ".env.new",
    "API_TEST_GUIDE.md"
)

# Directories to remove
$dirsToRemove = @(
    "__pycache__",
    ".vscode",
    "tests"
)

Write-Host "Removing debug and test files..." -ForegroundColor Cyan

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "✅ Removed: $file" -ForegroundColor Green
    }
}

foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        Remove-Item $dir -Recurse -Force
        Write-Host "✅ Removed directory: $dir" -ForegroundColor Green
    }
}

# Create docs directory and move documentation
Write-Host "Organizing documentation..." -ForegroundColor Cyan

if (!(Test-Path "docs")) {
    New-Item -ItemType Directory -Name "docs"
    Write-Host "✅ Created docs directory" -ForegroundColor Green
}

# Move documentation files to docs folder
$docsToMove = @(
    "POSTMAN_GUIDE.md",
    "RAG_IMPLEMENTATION_SUMMARY.md", 
    "API_Test_Collection.postman_collection.json"
)

foreach ($doc in $docsToMove) {
    if (Test-Path $doc) {
        Move-Item $doc "docs/" -Force
        Write-Host "✅ Moved $doc to docs/" -ForegroundColor Green
    }
}

# Update .env.example to remove your actual keys
Write-Host "Creating clean .env.example..." -ForegroundColor Cyan

$envExample = @"
# Environment Variables - UPDATE WITH YOUR VALUES
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=document-embeddings
PINECONE_ENVIRONMENT=us-east-1
MONGODB_URL=your_mongodb_connection_string_here
MONGODB_DATABASE=llm_query_system
API_SECRET_KEY=your_secret_key_here_change_this_in_production
ALLOWED_API_KEYS=api_key_1,api_key_2,api_key_3
"@

$envExample | Out-File ".env.example" -Encoding UTF8
Write-Host "✅ Updated .env.example" -ForegroundColor Green

# Create a clean README for sharing
Write-Host "Creating sharing-ready README..." -ForegroundColor Cyan

$readmeContent = @"
# 🚀 LLM-Powered Document Q&A API

A robust API for answering questions about documents using RAG (Retrieval-Augmented Generation) architecture with Google Gemini LLM.

## ✨ Features

- **Multi-Document Support**: PDF, DOCX, and URL inputs
- **Multi-Question Processing**: Handle up to 10 questions simultaneously
- **RAG Architecture**: Semantic chunking, vector search, and context-aware generation
- **Clean JSON Responses**: No markdown formatting, professional output
- **Authentication**: Bearer token security
- **Async Processing**: High-performance FastAPI backend

## 🛠️ Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run the Application
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

## 📡 API Usage

### Health Check
```
GET http://localhost:8003/health
```

### Process Documents
```
POST http://localhost:8003/hackrx/run
Content-Type: application/json
Authorization: Bearer api_key_1

{
    "documents": "path/to/document.pdf",
    "questions": [
        "What is the main topic?",
        "Who are the key stakeholders?"
    ]
}
```

## 📁 Project Structure

```
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── services/              # Core services
│   ├── rag_service.py     # RAG implementation
│   ├── llm_service.py     # Gemini integration
│   └── ...               # Other services
├── models/               # Request/Response models
└── docs/                # Documentation
```

## 🔧 Configuration

Required environment variables:
- `GEMINI_API_KEY`: Google Gemini API key
- `MONGODB_URL`: MongoDB connection string
- `ALLOWED_API_KEYS`: Comma-separated API keys

## 📚 Documentation

See `docs/` folder for:
- Postman collection
- RAG implementation details
- Usage guides

## 🚀 Performance

- Processing time: 10-20 seconds for 4 questions
- Supports documents up to 100K+ characters
- Intelligent chunking to respect API limits
- Efficient vector similarity search

Built with FastAPI, Google Gemini, MongoDB, and FAISS.
"@

$readmeContent | Out-File "README.md" -Encoding UTF8
Write-Host "✅ Created sharing-ready README.md" -ForegroundColor Green

Write-Host "`n🎉 CLEANUP COMPLETE!" -ForegroundColor Yellow
Write-Host "Your API application is now ready to share with your friend." -ForegroundColor Green
Write-Host "`nRemaining files are clean and essential for the application." -ForegroundColor White
Write-Host "Remember to tell your friend to update .env.example with their API keys!" -ForegroundColor Cyan
