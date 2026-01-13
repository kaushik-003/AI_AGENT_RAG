# System Architecture

Detailed technical architecture of the AI Agent with RAG system.

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Client Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Browser  │  │ Postman  │  │   cURL   │  │  Mobile  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                       │ HTTPS
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Endpoints: /ask, /health, /clear-session, /docs      │  │
│  │  • Request Validation (Pydantic)                       │  │
│  │  • Error Handling                                      │  │
│  │  • CORS Middleware                                     │  │
│  │  • Logging                                             │  │
│  └────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    Agent Layer (LangGraph)                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              State Machine Workflow                    │  │
│  │                                                        │  │
│  │  ┌──────────┐      ┌─────────────┐     ┌──────────┐ │  │
│  │  │  Query   │─────▶│   Decide    │────▶│  Tools   │ │  │
│  │  │ Analysis │      │  Strategy   │     │ Execution│ │  │
│  │  └──────────┘      └─────────────┘     └────┬─────┘ │  │
│  │                                              │       │  │
│  │  ┌──────────┐      ┌─────────────┐          │       │  │
│  │  │ Response │◀─────│   Combine   │◀─────────┘       │  │
│  │  │Generation│      │   Results   │                  │  │
│  │  └──────────┘      └─────────────┘                  │  │
│  │                                                        │  │
│  │  Memory: Session-based conversation history          │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ search_docs  │ │ get_current  │ │  (future)    │
│    Tool      │ │   _date      │ │   tools      │
└──────┬───────┘ └──────────────┘ └──────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                      RAG System Layer                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  Document Processing                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │ PDF Load │─▶│  Chunk   │─▶│  Embed   │            │  │
│  │  └──────────┘  └──────────┘  └──────────┘            │  │
│  │        │              │              │                │  │
│  │        ▼              ▼              ▼                │  │
│  │  4 PDF Files  →  45 Chunks  →  Vector Embeddings     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                Vector Store (FAISS)                    │  │
│  │  • In-memory index                                     │  │
│  │  • Cosine similarity search                            │  │
│  │  • Top-K retrieval (K=3)                               │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                Retrieval Process                       │  │
│  │  Query → Embed → Search → Rank → Return Top 3 Chunks  │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                   External Services                          │
│  ┌──────────────────────┐      ┌──────────────────────┐     │
│  │     OpenAI API       │      │    Document Store    │     │
│  │  • GPT-4o-mini       │      │  • company_policy    │     │
│  │  • text-embed-3-sm   │      │  • product_faq       │     │
│  │  • $0.15/$0.60/1M    │      │  • api_docs          │     │
│  │  • $0.02/1M (embed)  │      │  • benefits_guide    │     │
│  └──────────────────────┘      └──────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. API Gateway (FastAPI)

**File:** `app/main.py`

**Responsibilities:**
- HTTP request handling
- Input validation
- Response formatting
- Error handling
- CORS management

**Key Features:**
```python
# Automatic API documentation
@app.get("/docs")  # Swagger UI
@app.get("/redoc") # ReDoc

# Request validation
class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    session_id: Optional[str] = None

# Error handling
@app.exception_handler(Exception)
async def handle_errors(request, exc):
    return JSONResponse(status_code=500, ...)
```

**Endpoints:**

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/` | GET | API info | No |
| `/health` | GET | Health check | No |
| `/ask` | POST | Query agent | No |
| `/clear-session` | POST | Clear session | No |
| `/docs` | GET | Swagger UI | No |
| `/redoc` | GET | ReDoc UI | No |

---

### 2. Agent Layer (LangGraph)

**File:** `app/agent.py`

**Architecture Pattern:** State Machine

**State Definition:**
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
```

**Workflow:**
```
[Entry] → [Agent Node] → [Should Continue?]
                              │
              ┌───────────────┴──────────────┐
              │                              │
            [Tools]                        [End]
              │
              └──────────▶ [Agent Node]
```

**Decision Logic:**
```python
def _should_continue(self, state):
    last_message = state["messages"][-1]
    if has_tool_calls(last_message):
        return "tools"  # Execute tools
    return "end"  # Return response
```

**Memory Management:**
- Stores last 10 messages per session
- Filters tool messages to prevent API errors
- Creates clean AI messages without tool_calls

**Session Isolation:**
```python
self.sessions = {
    "session_1": [msg1, msg2, ...],
    "session_2": [msg3, msg4, ...],
}
```

---

### 3. Tools Layer

**File:** `app/tools.py`

**Tool 1: search_documents**
```python
@tool
def search_documents(query: str) -> Dict[str, Any]:
    """Search company documents"""
    # Uses RAG system
    rag = get_rag_system()
    context, sources = rag.get_context(query, k=3)
    return {
        "context": context,
        "sources": sources,
        "success": True
    }
```

**Tool 2: get_current_date**
```python
@tool
def get_current_date() -> str:
    """Get current date and time"""
    return datetime.now().strftime("%A, %B %d, %Y")
```

**Tool Binding:**
```python
self.llm_with_tools = self.llm.bind_tools([
    search_documents,
    get_current_date
])
```

**Tool Selection:**
The LLM automatically decides which tool to use based on:
- Query content
- Tool descriptions
- System prompt instructions

---

### 4. RAG System

**File:** `app/rag.py`

**Pipeline:**

#### Step 1: Document Loading
```python
PyPDFLoader("document.pdf")
├─ Extracts text from PDF
├─ Preserves page structure
└─ Adds metadata (source, page)
```

#### Step 2: Text Chunking
```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Max chunk length
    chunk_overlap=200,    # Overlap between chunks
    separators=["\n\n", "\n", " ", ""]
)

Example:
Input: 5000 char document
Output: 6 chunks (with overlap)
- Chunk 1: chars 0-1000
- Chunk 2: chars 800-1800  (200 char overlap)
- Chunk 3: chars 1600-2600
- ...
```

**Why overlap?**
- Prevents information loss at boundaries
- Ensures complete sentences/paragraphs
- Better context preservation

#### Step 3: Embedding Generation
```python
OpenAIEmbeddings(model="text-embedding-3-small")

Process:
Text → API → 1536-dim vector
"remote work" → [0.23, -0.15, 0.87, ...]
```

**Embedding Properties:**
- Dimensionality: 1536
- Semantic similarity preserved
- Cost: $0.02 per 1M tokens

#### Step 4: Vector Storage (FAISS)
```python
FAISS.from_documents(chunks, embeddings)

Structure:
Index:
  Vector 1: [0.23, -0.15, ...]  → Chunk 1, company_policy.pdf
  Vector 2: [0.45, 0.23, ...]   → Chunk 2, company_policy.pdf
  Vector 3: [-0.12, 0.67, ...]  → Chunk 3, product_faq.pdf
  ...
```

**FAISS Features:**
- In-memory storage
- Fast cosine similarity search
- Optimized for < 1M vectors
- No external dependencies

#### Step 5: Retrieval
```python
similarity_search_with_score(query, k=3)

Process:
1. Embed query
2. Compute cosine similarity with all vectors
3. Sort by similarity score
4. Return top K chunks

Example:
Query: "vacation policy"
Returns:
  1. (chunk_text, 0.92) - benefits_guide.pdf
  2. (chunk_text, 0.87) - company_policy.pdf
  3. (chunk_text, 0.75) - benefits_guide.pdf
```

**Similarity Metric:**
```
cosine_similarity = (A · B) / (||A|| × ||B||)

Range: -1 to 1
- 1.0 = identical
- 0.0 = orthogonal
- -1.0 = opposite
```

---

### 5. LLM Integration

**Model:** GPT-4o-mini

**Configuration:**
```python
ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,      # Deterministic
    streaming=False,    # Full response
)
```

**System Prompt:**
```python
"""
You are a helpful AI assistant for TechCorp Inc.

Decision-making guidelines:
1. Company policies → Use search_documents
2. Product FAQs → Use search_documents
3. API docs → Use search_documents
4. General chat → Answer directly
5. Current date → Use get_current_date

When using search_documents:
- Base answer on retrieved context
- Cite sources
- Acknowledge limitations
"""
```

**Context Assembly:**
```python
messages = [
    SystemMessage(system_prompt),
    HumanMessage("What is the vacation policy?"),
    AIMessage(tool_calls=[...]),
    ToolMessage(content="Retrieved context..."),
    AIMessage("Based on the policy...")
]
```

---

## Request Flow

### Example: "What is the remote work policy?"

```
1. Client Request
   POST /ask
   {"query": "What is the remote work policy?"}
   
2. FastAPI Validation
   ✓ Query length valid
   ✓ Parse JSON
   ✓ Create QueryRequest model
   
3. Agent Receives Query
   session_id = generate_uuid()
   initial_state = {
       "messages": [
           SystemMessage(prompt),
           HumanMessage(query)
       ]
   }
   
4. Agent Analysis
   LLM analyzes: "This is about company policy"
   Decision: "Use search_documents tool"
   
5. Tool Execution
   search_documents("What is the remote work policy?")
   
6. RAG Process
   a. Embed query → [0.34, -0.12, ...]
   b. Search FAISS → Find top 3 chunks
   c. Return context + sources
   
7. Tool Result
   ToolMessage({
       "context": "TechCorp Remote Work Policy...",
       "sources": ["company_policy.pdf"]
   })
   
8. Agent Synthesis
   LLM receives:
   - Original query
   - Retrieved context
   - System instructions
   
   Generates: "According to TechCorp's policy..."
   
9. Response Formation
   {
       "answer": "According to TechCorp's policy...",
       "sources": ["company_policy.pdf"],
       "session_id": "abc-123"
   }
   
10. Store in Session
    sessions["abc-123"] = [
        HumanMessage(query),
        AIMessage(answer)
    ]
    
11. Return to Client
    HTTP 200 OK
    JSON response
```

**Timing:**
- FastAPI validation: ~10ms
- Agent processing: ~500ms
- RAG search: ~100ms
- LLM generation: ~2-3s
- **Total: ~3-4 seconds**

---

## Data Flow

### Document Processing (One-time)

```
PDF Files (4 documents)
    │
    ├─▶ PyPDF Extraction
    │     │
    │     └─▶ Raw Text (12 pages)
    │
    ├─▶ Text Chunking
    │     │
    │     └─▶ 45 Chunks (1000 chars each)
    │
    ├─▶ Embedding Generation
    │     │
    │     └─▶ 45 Vectors (1536 dims each)
    │
    └─▶ FAISS Index
          │
          └─▶ Saved to disk
                embeddings/faiss_index/
                ├─ index.faiss (vectors)
                └─ index.pkl (metadata)
```

### Query Processing (Runtime)

```
User Query
    │
    ├─▶ Validation
    │
    ├─▶ Agent Analysis
    │     │
    │     └─▶ Tool Selection
    │
    ├─▶ RAG Search
    │     │
    │     ├─▶ Embed Query
    │     ├─▶ Similarity Search
    │     └─▶ Retrieve Top-K
    │
    ├─▶ Context Assembly
    │     │
    │     └─▶ [System + History + Context + Query]
    │
    ├─▶ LLM Generation
    │     │
    │     └─▶ Answer + Citations
    │
    └─▶ Response
```

---

## Security Architecture

### 1. API Security
- Environment variables for secrets
- No hardcoded credentials
- HTTPS only in production
- Input validation (Pydantic)

### 2. Data Security
- No user data stored permanently
- Sessions in memory (cleared on restart)
- No logging of sensitive info

### 3. Rate Limiting
- Currently: None (add for production)
- Recommended: 10 requests/minute per IP

---

## Performance Considerations

### Bottlenecks

1. **LLM API Calls** (2-3s)
   - Solution: Caching common queries
   - Solution: Streaming responses

2. **Cold Starts** (10-30s on Render free tier)
   - Solution: Paid tier (always on)
   - Solution: Keep-alive pings

3. **Vector Search** (< 100ms, not a bottleneck)
   - FAISS is very fast for our scale
   - Scales to millions of vectors

### Optimization Strategies

```python
# 1. Caching
from functools import lru_cache

@lru_cache(maxsize=100)
def get_answer(query):
    return agent.chat(query)

# 2. Async Processing
async def ask_multiple(queries):
    return await asyncio.gather(*[
        ask_async(q) for q in queries
    ])

# 3. Connection Pooling
session = requests.Session()  # Reuse connections
```

---

## Integration Points

### Current Integrations
1. OpenAI API (GPT-4o-mini, embeddings)
2. FAISS (local vector store)

### Future Integrations
1. Redis (session persistence)
2. PostgreSQL (user data)
3. Pinecone (cloud vector store)
4. Auth0 (authentication)
5. Prometheus (monitoring)

---

## Testing Architecture

### Test Layers

```
Unit Tests
├─ test_rag.py (RAG components)
├─ test_agent.py (Agent logic)
└─ test_tools.py (Tool functions)

Integration Tests
├─ test_api.py (API endpoints)
└─ test_e2e.py (End-to-end)

Load Tests
└─ test_performance.py (Concurrent requests)
```

---

## Scalability

### Current Scale
- Concurrent users: ~10-50
- Documents: 4 PDFs
- Vector store: 45 embeddings
- Sessions: In-memory (limited)

### Scaling Strategy

**Horizontal Scaling:**
```
Load Balancer
├─▶ Instance 1
├─▶ Instance 2
└─▶ Instance 3

Shared:
├─ Redis (sessions)
├─ PostgreSQL (data)
└─ Pinecone (vectors)
```

**Vertical Scaling:**
- Upgrade to more RAM/CPU
- Optimize FAISS index
- Use faster storage

---

## Design Patterns

### 1. Singleton Pattern
```python
_agent_instance = None

def get_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AIAgent()
    return _agent_instance
```

### 2. Factory Pattern
```python
def create_tool(name: str) -> Tool:
    if name == "search":
        return SearchTool()
    elif name == "date":
        return DateTool()
```

### 3. State Pattern (LangGraph)
```python
class AgentState(TypedDict):
    messages: List[BaseMessage]
    # State transitions handled by LangGraph
```

---

## Technology Choices

| Decision | Chosen | Alternative | Reason |
|----------|--------|-------------|--------|
| Web Framework | FastAPI | Flask, Django | Performance, async, auto-docs |
| Agent Framework | LangGraph | LangChain only | State management, clarity |
| Vector Store | FAISS | Pinecone, Weaviate | Free, local, fast |
| LLM | GPT-4o-mini | GPT-4, Claude | Cost-effective |
| Deployment | Render | Heroku, AWS | Free tier, simple |

---

