# Deployment Guide

Complete guide for deploying the AI Agent with RAG system.

---

## Production Deployment (Render.com)

**Current Deployment:** https://ai-agent-rag-7et2.onrender.com

### Prerequisites
- GitHub account
- Render.com account (free)
- OpenAI API key

### Deployment Steps

#### 1. Prepare Repository

```bash
# Ensure all files are committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Create Render.com Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

#### 3. Create New Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `ai-agent-rag`
   - **Environment**: `Docker`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: (empty - uses Dockerfile)
   - **Start Command**: (empty - uses Dockerfile CMD)

#### 4. Configure Environment Variables

In Render dashboard, add these environment variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_PATH=./embeddings
API_HOST=0.0.0.0
API_PORT=8000
```

#### 5. Deploy

1. Click "Create Web Service"
2. Wait 5-10 minutes for build
3. Check logs for any errors
4. Visit your URL: `https://your-app-name.onrender.com/docs`

### Verification

```bash
# Test health endpoint
curl https://ai-agent-rag-7et2.onrender.com/health

# Test ask endpoint
curl -X POST https://ai-agent-rag-7et2.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the remote work policy?"}'
```

---

## 🐳 Docker Deployment

### Local Docker

```bash
# Build image
docker build -t ai-agent-rag:latest .

# Run container
docker run -d \
  --name ai-agent \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your_key" \
  ai-agent-rag:latest

# View logs
docker logs ai-agent

# Stop container
docker stop ai-agent
docker rm ai-agent
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ai-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=gpt-4o-mini
      - EMBEDDING_MODEL=text-embedding-3-small
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## Alternative Deployment Options

### Railway.app

1. Connect GitHub repository
2. Add environment variables
3. Deploy automatically
4. **Cost**: $5 credit/month (free)

### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Deploy
flyctl deploy
```

### Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create ai-agent-rag

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key

# Deploy
git push heroku main
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VECTOR_STORE_PATH` | Path to embeddings | `./embeddings` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |

---

## Monitoring

### Health Checks

Render automatically monitors:
- `/health` endpoint
- Response time
- Error rate

### Logs

```bash
# View logs in Render dashboard
# Or use Render CLI
render logs
```

### Metrics

Monitor in Render dashboard:
- CPU usage
- Memory usage
- Request count
- Response times

---

## Updates & Rollbacks

### Deploy New Version

```bash
# Commit changes
git add .
git commit -m "Update feature"
git push origin main

# Render auto-deploys from main branch
```

### Manual Redeploy

In Render dashboard:
1. Go to your service
2. Click "Manual Deploy"
3. Select branch
4. Click "Deploy"

### Rollback

In Render dashboard:
1. Go to "Deploys" tab
2. Find previous successful deploy
3. Click "Rollback to this deploy"

---

## Cost Optimization

### Render Free Tier

- **Included**: 750 hours/month
- **Limitation**: Spins down after 15 min inactivity
- **Wake-up time**: ~30 seconds

### Upgrade to Paid ($7/month)

Benefits:
- No spin-down
- Better performance
- Custom domains
- More build minutes

### OpenAI API Costs

Monitor usage:
1. Go to https://platform.openai.com/usage
2. Check daily costs
3. Set spending limits

**Estimated costs:**
- Light usage: $1-2/month
- Medium usage: $5-10/month
- Heavy usage: $20+/month

---

## Security Best Practices

### 1. Environment Variables

 **DO:**
- Store API keys in environment variables
- Use different keys for dev/prod
- Rotate keys regularly

 **DON'T:**
- Commit `.env` files
- Hardcode API keys
- Share keys publicly

### 2. API Rate Limiting

Implement rate limiting:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/ask")
@limiter.limit("10/minute")
async def ask_question(request: Request):
    ...
```

### 3. Input Validation

Already implemented:
- Pydantic models
- Query length limits
- Type checking

---

## Troubleshooting

### Common Issues

#### 1. Build Fails

**Error**: "Requirements not found"
```bash
# Solution: Ensure requirements.txt exists
uv pip compile pyproject.toml -o requirements.txt
```

#### 2. Health Check Fails

**Error**: "Health check timeout"
```bash
# Solution: Check WEBSITES_PORT or PORT env variable
# Render uses PORT, not API_PORT
```

#### 3. Out of Memory

**Error**: "Container killed (OOM)"
```bash
# Solution: Reduce model size or upgrade plan
# Use gpt-4o-mini instead of gpt-4
```

#### 4. Slow Cold Starts

**Issue**: First request takes 30+ seconds
```bash
# Solution: 
# - Use Render paid plan (no spin-down)
# - Keep-alive service (ping every 10 min)
# - Use smaller models
```

---

## Scaling

### Horizontal Scaling

For high traffic:
1. Use load balancer
2. Multiple instances
3. Shared Redis for sessions
4. External vector DB (Pinecone)

### Vertical Scaling

Increase resources:
1. More CPU cores
2. More RAM
3. Better network

---

## Debugging

### Enable Debug Mode

```python
# app/main.py
import logging

logging.basicConfig(level=logging.DEBUG)
```

### View Detailed Logs

```bash
# In Render dashboard
# Events → Logs → Select log level
```

### Test Locally

```bash
# Run with debug
uvicorn app.main:app --reload --log-level debug
```

---


