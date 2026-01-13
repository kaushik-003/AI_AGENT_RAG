# AI Agent with RAG System

An intelligent AI agent powered by GPT-4o-mini that can answer questions by searching through company documents using Retrieval-Augmented Generation (RAG).

**🌐 Live Demo:** https://ai-agent-rag-7et2.onrender.com/docs

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Design Decisions](#design-decisions)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Assignment Requirements](#assignment-requirements)

---

## 🎯 Overview

This project implements an AI-powered question-answering system that combines:
- **AI Agent**: Intelligent decision-making using LangGraph
- **RAG System**: Document retrieval using FAISS vector store
- **REST API**: FastAPI backend with OpenAPI documentation
- **Tool Calling**: Dynamic tool selection based on query type
- **Session Memory**: Conversation context management

The agent can intelligently decide whether to:
1. Answer directly using its knowledge
2. Search company documents for relevant information
3. Use other tools (e.g., get current date)

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────────┐
│           FastAPI Backend               │
│  ┌─────────────────────────────────┐   │
│  │        AI Agent (LangGraph)     │   │
│  │  ┌───────────┐   ┌───────────┐  │   │
│  │  │  Decision │──▶│   Tools   │  │   │
│  │  │   Engine  │   │  Calling  │  │   │
│  │  └───────────┘   └─────┬─────┘  │   │
│  │                         │        │   │
│  │                         ▼        │   │
│  │              ┌──────────────┐   │   │
│  │              │ RAG System   │   │   │
│  │              │  - FAISS DB  │   │   │
│  │              │  - Embeddings│   │   │
│  │              └──────────────┘   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────┐         ┌──────────────┐
│  OpenAI API │         │  Documents   │
│ GPT-4o-mini │         │  (4 PDFs)    │
└─────────────┘         └──────────────┘
```

### Architecture Components

1. **Client Layer**
   - Web browser accessing API endpoints
   - Swagger UI for interactive testing
   - Any HTTP client (curl, Postman, etc.)

2. **API Layer (FastAPI)**
   - RESTful endpoints (`/ask`, `/health`)
   - Request validation using Pydantic
   - Error handling and logging
   - CORS support

3. **Agent Layer (LangGraph)**
   - Query analysis and routing
   - Tool selection and execution
   - Session memory management
   - Response generation

4. **RAG System**
   - Document processing (PDF → chunks)
   - Vector embeddings (OpenAI)
   - FAISS vector store
   - Similarity search

5. **External Services**
   - OpenAI API (GPT-4o-mini, embeddings)
   - Document storage (4 PDF files)

---

## ✨ Features

### Core Features
-  **Intelligent Query Routing**: Automatically decides when to search documents
-  **Document Search**: RAG-based retrieval from company documents
-  **Tool Calling**: Multiple tools (document search, date retrieval)
-  **Session Memory**: Maintains conversation context
-  **Source Attribution**: Returns source documents for transparency
-  **REST API**: Production-ready FastAPI endpoints
-  **Auto Documentation**: Swagger UI and ReDoc

### Document Coverage
- Company policies (remote work, vacation, etc.)
- Product FAQs (CloudStorage Pro)
- API documentation
- Employee benefits guide

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11**: Programming language
- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### AI & Machine Learning
- **OpenAI GPT-4o-mini**: Language model ($0.15/$0.60 per 1M tokens)
- **text-embedding-3-small**: Embeddings model ($0.02 per 1M tokens)
- **LangChain**: LLM application framework
- **LangGraph**: Agent orchestration
- **FAISS**: Vector similarity search

### Document Processing
- **PyPDF**: PDF text extraction
- **RecursiveCharacterTextSplitter**: Text chunking

### Development Tools
- **UV**: Fast Python package manager
- **Docker**: Containerization
- **Git/GitHub**: Version control

### Deployment
- **Render.com**: Cloud hosting (free tier)
- **HTTPS**: Automatic SSL/TLS

---

## 📁 Project Structure

```
ai-agent-rag/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application
│   ├── agent.py             # AI agent with LangGraph
│   ├── rag.py               # RAG system implementation
│   ├── tools.py             # Tool definitions
│   ├── models.py            # Pydantic models
│   └── config.py            # Configuration management
├── documents/               # Source documents (4 PDFs)
│   ├── company_policy.pdf
│   ├── product_faq.pdf
│   ├── api_documentation.pdf
│   └── benefits_guide.pdf
├── embeddings/              # FAISS vector store
│   └── faiss_index/
│       ├── index.faiss
│       └── index.pkl
├── tests/
│   ├── test_api.py         # API endpoint tests
│   ├── test_agent.py       # Agent functionality tests
│   └── test_rag.py         # RAG system tests
├── build_index.py           # Script to build vector store
├── .env                     # Environment variables (not in git)
├── .gitignore
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
├── pyproject.toml          # UV project configuration
├── README.md               # This file
└── DEPLOYMENT.md           # Deployment guide
```

---

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- UV package manager
- OpenAI API key
- Git

### Local Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-agent-rag.git
cd ai-agent-rag
```

#### 2. Install UV Package Manager
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 3. Install Dependencies
```bash
# Install all dependencies
uv sync

# Or install manually
uv add fastapi uvicorn python-dotenv
uv add openai langgraph langchain langchain-openai langchain-community
uv add faiss-cpu pypdf2 pydantic pydantic-settings
```

#### 4. Configure Environment Variables
```bash
# Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_PATH=./embeddings
API_HOST=0.0.0.0
API_PORT=8000
EOF
```

**Get OpenAI API Key:**
1. Go to https://platform.openai.com/
2. Create an account or sign in
3. Navigate to API Keys
4. Create new secret key
5. Copy and paste into `.env` file

#### 5. Prepare Documents
```bash
# Documents are already included in the repository
# Located in: documents/*.pdf
ls documents/
```

#### 6. Build RAG Index
```bash
# Process documents and create vector embeddings
uv run python build_index.py
```

**Expected Output:**
```
============================================================
RAG INDEX BUILDER
============================================================

Found 4 PDF files:
  - company_policy.pdf
  - product_faq.pdf
  - api_documentation.pdf
  - benefits_guide.pdf

📄 Found 4 PDF files
Loading: company_policy.pdf
...
 Loaded 12 pages from 4 documents
 Created 45 chunks from 12 pages
 Generating embeddings...
 Embeddings created successfully
 Vector store saved to embeddings/faiss_index

============================================================
 SUCCESS! RAG index built successfully
============================================================
```

#### 7. Start the Server
```bash
# Run the FastAPI server
uv run uvicorn app.main:app --reload
```

**Server will start at:** http://localhost:8000

#### 8. Test the API
```bash
# Open in browser
open http://localhost:8000/docs

# Or test with curl
curl http://localhost:8000/health

curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the remote work policy?"}'
```

---

## API Documentation

### Base URL
- **Production**: https://ai-agent-rag-7et2.onrender.com
- **Local**: http://localhost:8000

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "agent_ready": true,
  "rag_ready": true,
  "active_sessions": 0
}
```

#### 2. Ask Question
```http
POST /ask
```

**Request Body:**
```json
{
  "query": "What is the remote work policy?",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "answer": "According to TechCorp's Remote Work Policy...",
  "sources": ["company_policy.pdf"],
  "session_id": "optional_session_id"
}
```

#### 3. Clear Session
```http
POST /clear-session
```

**Request Body:**
```json
{
  "session_id": "session_to_clear"
}
```

**Response:**
```json
{
  "message": "Session cleared successfully",
  "session_id": "session_to_clear"
}
```

#### 4. API Documentation
- **Swagger UI**: https://ai-agent-rag-7et2.onrender.com/docs
- **ReDoc**: https://ai-agent-rag-7et2.onrender.com/redoc

### Example Usage

```python
import httpx

# Ask a question
response = httpx.post(
    "https://ai-agent-rag-7et2.onrender.com/ask",
    json={
        "query": "How many vacation days do employees get?",
        "session_id": "user_123"
    }
)

data = response.json()
print(f"Answer: {data['answer']}")
print(f"Sources: {data['sources']}")
```

```bash
# Using curl
curl -X POST https://ai-agent-rag-7et2.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I upload files using the API?",
    "session_id": "demo"
  }'
```

---

## 🎨 Design Decisions

### 1. Architecture Choices

**Why LangGraph?**
- Built-in state management for agents
- Visual graph-based workflow
- Easy tool integration
- Better than simple prompt chaining

**Why FAISS?**
- Fast similarity search
- No external dependencies
- Works offline
- Free and open-source
- Alternative: Pinecone (requires API, paid)

**Why FastAPI?**
- Automatic API documentation
- Built-in validation with Pydantic
- High performance (async support)
- Modern Python framework

### 2. Document Processing

**Chunking Strategy:**
- **Chunk size**: 1000 characters
- **Overlap**: 200 characters
- **Rationale**: Balance between context and precision

**Why this matters:**
- Too small: Loses context
- Too large: Retrieves irrelevant info
- Overlap ensures no information loss at boundaries

### 3. Model Selection

**GPT-4o-mini vs GPT-4:**
- 16x cheaper ($0.15 vs $2.50 per 1M input tokens)
- Faster response time
- Sufficient for Q&A tasks
- Better cost/performance ratio

**text-embedding-3-small:**
- Latest embedding model
- Better than ada-002
- Higher quality at same price

### 4. Session Management

**In-Memory Storage:**
- Simple implementation
- Last access
- Lost on restart
- **Future**: Use Redis for persistence

**Message History:**
- Keep last 10 messages per session
- Filter out tool messages
- Prevents context overflow

### 5. Tool Design

**Separate Tools vs Combined:**
- Chose separate tools for clarity
- Each tool has single responsibility
- Easier to test and maintain
- Agent decides which tool to use

---

## Limitations

### Current Limitations

1. **Document Scope**
   - Limited to 4 pre-loaded PDFs
   - Cannot upload new documents via API
   - **Impact**: Fixed knowledge base

2. **Session Persistence**
   - Sessions stored in memory
   - Lost when server restarts
   - **Impact**: Conversations don't persist

3. **Scalability**
   - Single instance deployment
   - No load balancing
   - FAISS in-memory storage
   - **Impact**: Limited concurrent users

4. **Document Updates**
   - Requires rebuilding index manually
   - No real-time document ingestion
   - **Impact**: Can't update knowledge dynamically

5. **Error Recovery**
   - Limited retry logic
   - No circuit breaker for API failures
   - **Impact**: May fail on API rate limits

6. **Search Quality**
   - Simple cosine similarity
   - No re-ranking
   - No query expansion
   - **Impact**: May miss relevant documents

7. **Cost Management**
   - No token counting
   - No rate limiting per user
   - **Impact**: Potential unexpected costs

---

## Future Improvements

### Short-term (1-2 weeks)

1. **Document Upload API**
   ```python
   POST /upload-document
   # Allow users to upload PDFs
   ```

2. **Session Persistence**
   - Integrate Redis for session storage
   - Save conversation history

3. **Better Error Handling**
   - Retry logic for API calls
   - Graceful degradation
   - User-friendly error messages

4. **Monitoring**
   - Add logging aggregation
   - Track API usage metrics
   - Monitor response times

### Medium-term (1-2 months)

5. **Advanced RAG**
   - Hybrid search (keyword + vector)
   - Query expansion
   - Re-ranking results
   - Metadata filtering

6. **User Authentication**
   - JWT-based auth
   - API key management
   - Rate limiting per user

7. **Streaming Responses**
   - Server-Sent Events (SSE)
   - Real-time typing indicators
   - Better UX for long responses

8. **Caching**
   - Cache common queries
   - Reduce API calls
   - Faster responses

### Long-term (3+ months)

9. **Multi-modal Support**
   - Image understanding
   - Table extraction
   - Chart analysis

10. **Advanced Features**
    - Multi-document reasoning
    - Summarization
    - Question generation
    - Fact verification

11. **Scalability**
    - Horizontal scaling
    - Database for vector store (Pinecone/Weaviate)
    - Distributed caching
    - Load balancing

12. **Enterprise Features**
    - Multi-tenancy
    - Role-based access control
    - Audit logging
    - Compliance (GDPR, SOC2)

---

## Assignment Requirements Checklist

### Task 1: AI Agent Development 
- ✅ Accepts user queries
- ✅ Decides between direct answer or document search
- ✅ Returns structured responses
- ✅ Uses OpenAI API
- ✅ Implements prompt engineering
- ✅ Tool calling (search_documents, get_current_date)
- ✅ Session-based memory

### Task 2: RAG Implementation ✅
- ✅ 4 sample documents provided (PDF)
- ✅ Documents converted to embeddings
- ✅ Embeddings stored in FAISS
- ✅ Retrieves relevant chunks
- ✅ Passes context to LLM

### Task 3: Backend API ✅
- ✅ FastAPI framework
- ✅ POST /ask endpoint
- ✅ Request/response format as specified
- ✅ Additional endpoints (health, clear-session)

### Task 4: Deployment ✅
- ✅ Deployed on Render.com (cloud platform)
- ✅ Environment variables for secrets
- ✅ Accessible via public URL
- ✅ HTTPS enabled
- ✅ Docker containerization (bonus)


## Performance Metrics

### Response Times (Average)
- Health check: ~100ms
- Simple query: ~2-3 seconds
- Document-based query: ~3-5 seconds
- First request (cold start): ~10 seconds

### Costs (Estimated Monthly)
- OpenAI API: ~$2-5 (with free tier)
- Hosting (Render.com): $0 (free tier)
- **Total**: $0-5/month

### Token Usage (Per Query)
- Input: ~500-1500 tokens
- Output: ~200-500 tokens
- Embeddings: ~1000 tokens
- **Cost per query**: ~$0.001-0.003

---

## Testing

### Run Tests
```bash
# Test RAG system
uv run python test_rag.py

# Test AI agent
uv run python test_agent.py

# Test API endpoints
uv run python test_api.py

# Interactive testing
uv run python test_agent.py --interactive
```

### Test Coverage
- RAG system: Document loading, embedding, search
- AI Agent: Tool calling, memory, decision-making
- API: All endpoints, error handling, validation

---


### Development Workflow
1. Create feature branch
2. Make changes
3. Run tests
4. Submit pull request

---

## License

This project is created for educational purposes.
---

## Author

**Kaushik Maram**
- GitHub: [kaushik-003](https://github.com/kaushik-003)
- Email: koushikmaram17@gmail.com

---

## Acknowledgments

- OpenAI for GPT-4o-mini and embeddings API
- LangChain team for the excellent framework
- Render.com for free hosting

---

## Support

For questions or issues:
1. Check the [API Documentation](https://ai-agent-rag-7et2.onrender.com/docs)
2. Review [Limitations](#limitations)
3. Open an issue on GitHub

---

**Last Updated:** January 2026
**Version:** 1.0.0
**Status:** Production Ready