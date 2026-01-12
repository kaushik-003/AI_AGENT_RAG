
"""
Pydantic models for API request and response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    """Request model for /ask endpoint"""
    query: str = Field(
        ..., 
        min_length=1,
        max_length=1000,
        description="User query or question",
        examples=["What is the remote work policy?"]
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID for conversation memory",
        examples=["user_123"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How many vacation days do employees get?",
                "session_id": "user_123"
            }
        }


class QueryResponse(BaseModel):
    """Response model for /ask endpoint"""
    answer: str = Field(
        ...,
        description="AI-generated answer to the query"
    )
    sources: List[str] = Field(
        default_factory=list,
        description="List of source documents used"
    )
    session_id: str = Field(
        ...,
        description="Session ID used for the conversation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Employees receive 15-25 vacation days based on tenure...",
                "sources": ["company_policy.pdf", "benefits_guide.pdf"],
                "session_id": "user_123"
            }
        }


class HealthResponse(BaseModel):
    """Response model for /health endpoint"""
    status: str = Field(
        ...,
        description="Health status of the service"
    )
    message: str = Field(
        ...,
        description="Detailed health message"
    )
    agent_ready: bool = Field(
        ...,
        description="Whether the AI agent is initialized"
    )
    rag_ready: bool = Field(
        ...,
        description="Whether the RAG system is ready"
    )
    active_sessions: int = Field(
        ...,
        description="Number of active chat sessions"
    )


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str = Field(
        ...,
        description="Error message"
    )
    detail: Optional[str] = Field(
        default=None,
        description="Detailed error information"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid request",
                "detail": "Query field is required"
            }
        }


class SessionClearRequest(BaseModel):
    """Request model for clearing a session"""
    session_id: str = Field(
        ...,
        description="Session ID to clear",
        examples=["user_123"]
    )


class SessionClearResponse(BaseModel):
    """Response model for session clearing"""
    message: str = Field(
        ...,
        description="Confirmation message"
    )
    session_id: str = Field(
        ...,
        description="Cleared session ID"
    )