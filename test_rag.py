
"""
Test script to verify RAG system is working
"""

from app.rag import RAGSystem
from dotenv import load_dotenv

def main():
    """Test the RAG retrieval system"""
    load_dotenv()
    
    print("-"*60)
    print("TESTING RAG RETRIEVAL SYSTEM")
    print("-"*60 + "\n")
    
    # Initialize RAG
    rag = RAGSystem()
    
    # Load existing index
    if not rag.load_vector_store():
        print("Error: No vector store found!")
        print("Please run 'uv run python build_index.py' first")
        return
    
    # Test queries
    test_queries = [
        "What is the remote work policy?",
        "How many vacation days do employees get?",
        "How do I upload a file using the API?",
        "What is CloudStorage Pro?",
        "What are the health insurance options?",
    ]
    
    print("Running test queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'-'*60}")
        print(f"Query {i}: {query}")
        print('-'*60)
        
        try:
            # Get context and sources
            context, sources = rag.get_context(query, k=3)
            
            print(f"\nSources found: {', '.join(sources)}")
            print(f"\nContext retrieved ({len(context)} characters):")
            print("-" * 60)
            
            # Show first 500 characters of context
            preview = context[:500]
            if len(context) > 500:
                preview += "..."
            print(preview)
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "-"*60)
    print("RAG testing complete!")
    print("-"*60)

if __name__ == "__main__":
    main()