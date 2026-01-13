# API Usage Guide

Practical examples for using the AI Agent API.

**Base URL:** https://ai-agent-rag-7et2.onrender.com

---

## Quick Start

### Test the API

```bash
# 1. Check if API is running
curl https://ai-agent-rag-7et2.onrender.com/health

# 2. Ask your first question
curl -X POST https://ai-agent-rag-7et2.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the remote work policy?"}'
```

---

## Endpoint Reference

### 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Check if the API is running and ready

```bash
curl https://ai-agent-rag-7et2.onrender.com/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "agent_ready": true,
  "rag_ready": true,
  "active_sessions": 2
}
```

---

### 2. Ask Question

**Endpoint:** `POST /ask`

**Purpose:** Send a query to the AI agent

#### Basic Usage

```bash
curl -X POST https://ai-agent-rag-7et2.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many vacation days do employees get?"
  }'
```

#### With Session ID

```bash
curl -X POST https://ai-agent-rag-7et2.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the remote work policy?",
    "session_id": "user_123"
  }'
```

**Response:**
```json
{
  "answer": "According to TechCorp's policy, employees receive:\n- 0-2 years: 15 days\n- 3-5 years: 20 days\n- 6+ years: 25 days",
  "sources": ["benefits_guide.pdf"],
  "session_id": "user_123"
}
```

---

### 3. Clear Session

**Endpoint:** `POST /clear-session`

**Purpose:** Clear conversation history

```bash
curl -X POST https://ai-agent-rag-7et2.onrender.com/clear-session \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_123"
  }'
```

**Response:**
```json
{
  "message": "Session cleared successfully",
  "session_id": "user_123"
}
```

---

## Code Examples

### Python

```python
import requests

# Base URL
BASE_URL = "https://ai-agent-rag-7et2.onrender.com"

# Example 1: Simple query
def ask_question(query):
    response = requests.post(
        f"{BASE_URL}/ask",
        json={"query": query}
    )
    data = response.json()
    return data

# Example 2: With session
def ask_with_session(query, session_id):
    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "query": query,
            "session_id": session_id
        }
    )
    return response.json()

# Example 3: Multi-turn conversation
def conversation():
    session_id = "demo_session"
    
    # First question
    result1 = ask_with_session(
        "What is the vacation policy?",
        session_id
    )
    print(f"Answer: {result1['answer']}")
    
    # Follow-up question (uses context)
    result2 = ask_with_session(
        "What about sick leave?",
        session_id
    )
    print(f"Answer: {result2['answer']}")

# Usage
if __name__ == "__main__":
    # Simple query
    result = ask_question("How do I upload files using the API?")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
    
    # Conversation
    conversation()
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const BASE_URL = 'https://ai-agent-rag-7et2.onrender.com';

// Example 1: Simple query
async function askQuestion(query) {
  try {
    const response = await axios.post(`${BASE_URL}/ask`, {
      query: query
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}

// Example 2: With session
async function askWithSession(query, sessionId) {
  const response = await axios.post(`${BASE_URL}/ask`, {
    query: query,
    session_id: sessionId
  });
  return response.data;
}

// Example 3: Conversation
async function conversation() {
  const sessionId = 'demo_session';
  
  // First question
  const result1 = await askWithSession(
    'What are the health insurance options?',
    sessionId
  );
  console.log('Answer:', result1.answer);
  
  // Follow-up
  const result2 = await askWithSession(
    'What about dental?',
    sessionId
  );
  console.log('Answer:', result2.answer);
}

// Usage
(async () => {
  const result = await askQuestion('What is CloudStorage Pro?');
  console.log('Answer:', result.answer);
  console.log('Sources:', result.sources);
})();
```

### JavaScript (Browser/Fetch)

```javascript
const BASE_URL = 'https://ai-agent-rag-7et2.onrender.com';

// Example: Ask question
async function askQuestion(query) {
  const response = await fetch(`${BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query })
  });
  
  return await response.json();
}

// Usage
askQuestion('What is the remote work policy?')
  .then(data => {
    console.log('Answer:', data.answer);
    console.log('Sources:', data.sources);
  });
```

---

## Use Cases

### Use Case 1: Company Policy Bot

```python
def policy_bot():
    """Chatbot for company policies"""
    session_id = "policy_chat"
    
    questions = [
        "What is the remote work policy?",
        "How many vacation days do I get?",
        "What are the core working hours?",
        "Can I work from another country?"
    ]
    
    for question in questions:
        result = ask_with_session(question, session_id)
        print(f"\nQ: {question}")
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
```

### Use Case 2: API Documentation Helper

```python
def api_helper():
    """Help users with API integration"""
    queries = [
        "How do I authenticate with the API?",
        "What is the endpoint for uploading files?",
        "What are the rate limits?",
        "How do I handle errors?"
    ]
    
    for query in queries:
        result = ask_question(query)
        print(f"\nQuery: {query}")
        print(f"Answer: {result['answer']}\n")
```

### Use Case 3: Employee Benefits Guide

```python
def benefits_assistant():
    """Interactive benefits guide"""
    session = "benefits_session"
    
    print("Ask me about employee benefits!")
    print("Examples: health insurance, 401k, PTO, etc.\n")
    
    while True:
        question = input("Your question (or 'quit'): ")
        if question.lower() == 'quit':
            break
            
        result = ask_with_session(question, session)
        print(f"\n{result['answer']}\n")
        
        if result['sources']:
            print(f"Source: {', '.join(result['sources'])}\n")
```

---

## Query Examples

### General Questions (No Document Search)

```bash
# Greetings
"Hello, how are you?"
"What can you help me with?"

# General knowledge
"What is AI?"
"Explain machine learning"

# Current information
"What's today's date?"
```

### Document-Based Questions

#### Company Policies
```bash
"What is the remote work policy?"
"What are the core working hours?"
"Can I work from home?"
"What is the equipment policy?"
"How do I report security incidents?"
```

#### Employee Benefits
```bash
"How many vacation days do employees get?"
"What health insurance options are available?"
"What is the 401k matching policy?"
"How much parental leave is offered?"
"What is the dental insurance coverage?"
```

#### Product (CloudStorage Pro)
```bash
"What is CloudStorage Pro?"
"How do I reset my password?"
"What are the pricing plans?"
"How does file versioning work?"
"What security features are available?"
```

#### API Documentation
```bash
"How do I upload a file using the API?"
"What is the authentication method?"
"What are the error codes?"
"How do I create a folder via API?"
"What is the rate limit?"
```

---

## Conversation Examples

### Example 1: Multi-turn Context

```python
session = "context_demo"

# Turn 1
ask("What is the vacation policy?", session)
# Agent searches documents, explains policy

# Turn 2 (uses context from turn 1)
ask("What about sick leave?", session)
# Agent understands this is related to time off

# Turn 3
ask("Can unused days be rolled over?", session)
# Agent has full conversation context
```

### Example 2: Clarification

```python
session = "clarification_demo"

# Initial question
ask("How does the API work?", session)
# Too broad - agent asks for clarification

# Follow-up with specifics
ask("How do I authenticate with the API?", session)
# Agent provides specific authentication details
```

---

## ⚡ Best Practices

### 1. Use Session IDs

```python
#  GOOD: Use consistent session ID
session_id = f"user_{user_id}"
ask_with_session(query, session_id)

#  BAD: No session ID (loses context)
ask_question(query)
```

### 2. Clear Sessions When Done

```python
# Start new topic
clear_session(session_id)
ask_with_session("New question", session_id)
```

### 3. Handle Errors

```python
try:
    result = ask_question(query)
    print(result['answer'])
except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")
except KeyError:
    print("Unexpected response format")
```

### 4. Check Sources

```python
result = ask_question(query)
if result['sources']:
    print(f"Answer based on: {result['sources']}")
else:
    print("Answer from general knowledge")
```

---

## Response Format

### Successful Response

```json
{
  "answer": "The answer text here...",
  "sources": ["document1.pdf", "document2.pdf"],
  "session_id": "user_123"
}
```

### Error Response

```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

---

## Rate Limiting

Currently no rate limiting, but best practices:
- Don't spam requests
- Wait for response before next request
- Use reasonable timeouts (30-60 seconds)

---

## Testing

### Test Suite

```python
def test_api():
    """Test all endpoints"""
    
    # Test 1: Health check
    health = requests.get(f"{BASE_URL}/health")
    assert health.status_code == 200
    assert health.json()['status'] == 'healthy'
    
    # Test 2: Simple query
    result = ask_question("Hello")
    assert 'answer' in result
    
    # Test 3: Document query
    result = ask_question("What is the remote work policy?")
    assert result['sources']  # Should have sources
    
    # Test 4: Session memory
    session = "test_session"
    ask_with_session("My name is Alice", session)
    result = ask_with_session("What's my name?", session)
    assert 'alice' in result['answer'].lower()
    
    print("All tests passed!")

test_api()
```

---

## Interactive Documentation

**Swagger UI:** https://ai-agent-rag-7et2.onrender.com/docs
- Try endpoints directly in browser
- See request/response schemas
- Generate code snippets

**ReDoc:** https://ai-agent-rag-7et2.onrender.com/redoc
- Clean, readable documentation
- Better for learning API structure

---

## Troubleshooting

### Issue: Slow Response

**Cause:** Cold start (free tier spins down)
**Solution:** Wait 30-60 seconds for first request

### Issue: "Service Unavailable"

**Cause:** API is starting up or down
**Solution:** Check https://ai-agent-rag-7et2.onrender.com/health

### Issue: Empty Answer

**Cause:** Query too vague or no relevant documents
**Solution:** Be more specific in your question

### Issue: No Sources

**Normal:** General knowledge questions don't need documents
**Problem:** Document query but no sources → documents not loaded

---

## Tips

1. **Be Specific:** "What is the vacation policy?" vs "vacation?"
2. **Use Context:** Follow-up questions work better with session IDs
3. **Check Sources:** Verify which documents were used
4. **Clear Sessions:** Start fresh for new topics
5. **Test Locally:** Use Swagger UI for experimentation

---

**Happy querying!**