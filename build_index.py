
"""
Script to build the RAG index from PDF documents
Run this once after adding/updating documents
"""

import sys
from pathlib import Path
from app.rag import RAGSystem
from dotenv import load_dotenv

def main():
    """Build the vector store index"""
    # Load environment variables
    load_dotenv()
    
    print("-"*60)
    print("RAG INDEX BUILDER")
    print("-"*60 + "\n")
    
    # Check if documents exist
    docs_path = Path("./documents")
    pdf_files = list(docs_path.glob("*.pdf"))
    
    if not pdf_files:
        print("Error: No PDF files found in ./documents/")
        print("\nPlease add PDF files to the documents/ folder first.")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    print()
    
    # Initialize RAG system
    rag = RAGSystem(
        documents_path="./documents",
        embeddings_path="./embeddings",
        chunk_size=1000,
        chunk_overlap=200
    )
    
    # Build index
    try:
        rag.build_index(force_rebuild=True)
        print("\n" + "-"*60)
        print("SUCCESS! RAG index built successfully")
        print("-"*60)
        print("\nYou can now run the FastAPI server or test queries.")
        
    except Exception as e:
        print(f"\nError building index: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()