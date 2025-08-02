# LLM-Powered Intelligent Query-Retrieval System

A comprehensive FastAPI-based system for processing large documents and answering questions using LLM technology. Designed for insurance, legal, HR, and compliance domains.

## Features

- **Document Processing**: Support for PDF, DOCX, and other document formats
- **Semantic Search**: FAISS/Pinecone vector database for efficient document retrieval
- **LLM Integration**: Google Gemini for intelligent answer generation
- **MongoDB Storage**: Persistent storage for queries and document metadata
- **RESTful API**: Clean, well-documented API endpoints
- **Authentication**: Bearer token authentication for secure access

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   FastAPI App   │───▶│  Document Proc  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MongoDB       │◀───│  Vector Store   │◀───│  Embedding Svc  │
└─────────────────┘    │ (FAISS/Pinecone)│    └─────────────────┘
                       └─────────────────┘              │
                              │                         ▼
                              ▼                ┌─────────────────┐
                       ┌─────────────────┐    │   LLM Service   │
                       │   Answer Gen    │◀───│    (Gemini)     │
                       └─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.9+
- MongoDB (local or cloud)
- Google Gemini API Key
- Pinecone API Key (optional, uses FAISS as fallback)

### Installation

1. **Clone and Setup**
   ```bash
   cd "c:\Users\Admin\my projects\api application"
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   
   Update `.env` file with your credentials:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX_NAME=document-embeddings
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DATABASE=llm_query_system
   ALLOWED_API_KEYS=your_api_key_1,your_api_key_2
   ```

3. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Usage

### Main Endpoint: `/hackrx/run`

**Request:**
```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/document.pdf",
    "questions": [
      "What is the grace period for premium payment?",
      "What is the waiting period for pre-existing diseases?"
    ]
  }'
```

**Response:**
```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment...",
    "There is a waiting period of thirty-six (36) months..."
  ]
}
```

### Other Endpoints

- `GET /health` - System health check
- `GET /documents/{document_id}/metadata` - Document metadata
- `GET /queries/history` - Query history

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `PINECONE_API_KEY` | Pinecone API key | Optional |
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `ALLOWED_API_KEYS` | Comma-separated API keys | Required |

### Document Processing

- **Supported Formats**: PDF, DOCX, DOC, TXT
- **Max File Size**: 50MB
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters

## System Components

### Document Processor (`services/document_processor.py`)
- Downloads documents from URLs
- Extracts text from various formats
- Splits documents into searchable chunks

### Embedding Service (`services/embedding_service.py`)
- Uses Sentence Transformers for embeddings
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Generates embeddings for chunks and queries

### Vector Store (`services/vector_store.py`)
- Supports both Pinecone and FAISS
- Automatic fallback to FAISS if Pinecone not available
- Cosine similarity search

### LLM Service (`services/llm_service.py`)
- Google Gemini integration
- Context-aware answer generation
- Retry mechanisms and error handling

### Database Service (`services/database.py`)
- MongoDB integration using Motor (async)
- Stores queries, answers, and document metadata
- Analytics and reporting capabilities

## Development

### Running Tests
```bash
pytest tests/
```

### Code Structure
```
api application/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── models/                # Pydantic models
├── services/              # Core business logic
├── utils/                 # Helper functions
├── tests/                 # Test suite
├── requirements.txt       # Dependencies
└── .env                   # Environment variables
```

### Adding New Features

1. **New Endpoints**: Add to `main.py`
2. **New Services**: Create in `services/`
3. **New Models**: Add to `models/`
4. **Configuration**: Update `config.py`

## Deployment

### Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

The application is ready for deployment on:
- **Azure**: App Service, Container Instances
- **AWS**: ECS, Lambda, EC2
- **GCP**: Cloud Run, Compute Engine
- **Heroku**: Direct deployment

## Performance Considerations

- **Caching**: Implement Redis for embedding caching
- **Load Balancing**: Use multiple instances for high load
- **Database**: MongoDB replica sets for production
- **Vector Store**: Pinecone recommended for production scale

## Security

- **Authentication**: Bearer token authentication
- **Input Validation**: Pydantic models for request validation
- **Rate Limiting**: Implement rate limiting for production
- **HTTPS**: Always use HTTPS in production

## Monitoring

- **Health Checks**: Built-in health monitoring
- **Logging**: Structured logging throughout
- **Metrics**: Ready for Prometheus/Grafana integration
- **Error Tracking**: Sentry-compatible error handling

## Troubleshooting

### Common Issues

1. **Document Processing Fails**
   - Check document URL accessibility
   - Verify file format support
   - Check file size limits

2. **Embedding Generation Slow**
   - Consider using faster embedding models
   - Implement embedding caching
   - Reduce chunk sizes

3. **LLM API Errors**
   - Verify Gemini API key
   - Check rate limits
   - Monitor API quotas

### Logs and Debugging

```bash
# View logs in development
tail -f logs/app.log

# Check service health
curl http://localhost:8000/health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

For support or questions, please create an issue in the repository.
