
"""
Tool definitions for the AI agent
"""

from typing import List, Dict, Any
from langchain.tools import tool
from app.rag import RAGSystem


# Initialize RAG system (will be loaded once)
_rag_system = None

def get_rag_system() -> RAGSystem:
    """Get or initialize RAG system"""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
        _rag_system.load_vector_store()
    return _rag_system


@tool
def search_documents(query: str) -> Dict[str, Any]:
    """
    Search through company documents to find relevant information.
    
    Use this tool when the user asks about:
    - Company policies (remote work, benefits, vacation, etc.)
    - Product features and FAQs
    - API documentation and technical details
    - Employee benefits and guidelines
    
    Args:
        query: The search query to find relevant documents
        
    Returns:
        Dictionary containing context and sources
    """
    try:
        rag = get_rag_system()
        context, sources = rag.get_context(query, k=3)
        
        return {
            "context": context,
            "sources": sources,
            "success": True
        }
    except Exception as e:
        return {
            "context": "",
            "sources": [],
            "success": False,
            "error": str(e)
        }


@tool
def get_current_date() -> str:
    """
    Get the current date and time.
    
    Use this when user asks about:
    - Today's date
    - Current time
    - What day it is
    
    Returns:
        Current date and time as string
    """
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")


# List of all available tools
AVAILABLE_TOOLS = [
    search_documents,
    get_current_date
]