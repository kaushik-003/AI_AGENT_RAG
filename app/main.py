
"""
FastAPI application for AI Agent with RAG
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uuid
import logging

from app.models import (
    QueryRequest, 
    QueryResponse, 
    HealthResponse, 
    ErrorResponse,
    SessionClearRequest,
    SessionClearResponse
)
from app.agent import get_agent
from app.rag import RAGSystem
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global state
agent = None
rag = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    global agent, rag
    
    logger.info("Starting AI Agent API...")
    
    try:
        # Initialize RAG system
        logger.info("Loading RAG system...")
        rag = RAGSystem()
        if not rag.load_vector_store():
            logger.warning("Vector store not found. Run build_index.py first!")
        else:
            logger.info("RAG system loaded successfully")
        
        # Initialize agent
        logger.info("Initializing AI agent...")
        agent = get_agent()
        logger.info("AI agent initialized successfully")
        
        logger.info("API is ready to receive requests")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Agent API...")


# Create FastAPI app
app = FastAPI(
    title="AI Agent with RAG API",
    description="Intelligent AI agent that can search company documents and answer questions",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# API Endpoints

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AI Agent with RAG API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "ask": "/ask",
            "clear_session": "/clear-session"
        }
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Check API health status"
)
async def health_check():
    """
    Check the health status of the API and its components
    """
    try:
        # Check if agent is ready
        agent_ready = agent is not None
        
        # Check if RAG is ready
        rag_ready = rag is not None and rag.vector_store is not None
        
        # Get active sessions count
        active_sessions = agent.get_session_count() if agent else 0
        
        # Determine overall status
        if agent_ready and rag_ready:
            health_status = "healthy"
            message = "All systems operational"
        elif agent_ready and not rag_ready:
            health_status = "degraded"
            message = "Agent ready but RAG system not initialized"
        else:
            health_status = "unhealthy"
            message = "System not ready"
        
        return HealthResponse(
            status=health_status,
            message=message,
            agent_ready=agent_ready,
            rag_ready=rag_ready,
            active_sessions=active_sessions
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed"
        )


@app.post(
    "/ask",
    response_model=QueryResponse,
    tags=["Chat"],
    summary="Ask a question to the AI agent",
    responses={
        200: {"description": "Successful response"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def ask_question(request: QueryRequest):
    """
    Send a query to the AI agent and get a response.
    
    The agent will:
    - Analyze your question
    - Search relevant documents if needed
    - Provide an answer with sources
    - Maintain conversation context using session_id
    
    **Example queries:**
    - "What is the remote work policy?"
    - "How do I upload files using the API?"
    - "What are the vacation benefits?"
    """
    try:
        # Validate agent is ready
        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI agent not initialized"
            )
        
        # Generate session_id if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Log the request
        logger.info(f"Query received - Session: {session_id[:8]}... Query: {request.query[:50]}...")
        
        # Get response from agent
        response = agent.chat(
            query=request.query,
            session_id=session_id
        )
        
        # Check for errors in agent response
        if "error" in response:
            logger.error(f"Agent error: {response['error']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent error: {response['error']}"
            )
        
        # Log successful response
        logger.info(f"Response sent - Session: {session_id[:8]}... Sources: {response.get('sources', [])}")
        
        return QueryResponse(
            answer=response["answer"],
            sources=response.get("sources", []),
            session_id=response["session_id"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /ask endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.post(
    "/clear-session",
    response_model=SessionClearResponse,
    tags=["Session"],
    summary="Clear a conversation session"
)
async def clear_session(request: SessionClearRequest):
    """
    Clear the conversation history for a specific session.
    
    This will remove all previous messages and context for the given session_id.
    """
    try:
        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI agent not initialized"
            )
        
        # Clear the session
        agent.clear_session(request.session_id)
        
        logger.info(f"Session cleared: {request.session_id[:8]}...")
        
        return SessionClearResponse(
            message="Session cleared successfully",
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing session: {str(e)}"
        )


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )