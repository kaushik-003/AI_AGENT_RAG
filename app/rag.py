
"""
RAG (Retrieval-Augmented Generation) System
Handles document loading, chunking, embedding, and retrieval
"""

import os
from typing import List, Dict, Tuple
from pathlib import Path
import pickle

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class RAGSystem:
    def __init__(
        self, 
        documents_path: str = "./documents",
        embeddings_path: str = "./embeddings",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize RAG System
        
        Args:
            documents_path: Path to PDF documents
            embeddings_path: Path to store FAISS index
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.documents_path = Path(documents_path)
        self.embeddings_path = Path(embeddings_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
        # Vector store
        self.vector_store = None
        
        # Create directories if they don't exist
        self.embeddings_path.mkdir(parents=True, exist_ok=True)
        
    def load_documents(self) -> List[Document]:
        """
        Load all PDF documents from documents folder
        
        Returns:
            List of Document objects
        """
        documents = []
        pdf_files = list(self.documents_path.glob("*.pdf"))
        
        if not pdf_files:
            raise ValueError(f"No PDF files found in {self.documents_path}")
        
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            print(f"Loading: {pdf_file.name}")
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            
            # Add source metadata
            for doc in docs:
                doc.metadata["source"] = pdf_file.name
            
            documents.extend(docs)
        
        print(f"Loaded {len(documents)} pages from {len(pdf_files)} documents")
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of chunked documents
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks from {len(documents)} pages")
        return chunks
    
    def create_embeddings(self, chunks: List[Document]) -> FAISS:
        """
        Create embeddings and FAISS vector store
        
        Args:
            chunks: List of document chunks
            
        Returns:
            FAISS vector store
        """
        print("Generating embeddings... (this may take a minute)")
        
        vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        
        print("Embeddings created successfully")
        return vector_store
    
    def save_vector_store(self):
        """Save FAISS vector store to disk"""
        if self.vector_store is None:
            raise ValueError("Vector store not initialized")
        
        save_path = self.embeddings_path / "faiss_index"
        self.vector_store.save_local(str(save_path))
        print(f"Vector store saved to {save_path}")
    
    def load_vector_store(self) -> bool:
        """
        Load FAISS vector store from disk
        
        Returns:
            True if loaded successfully, False otherwise
        """
        load_path = self.embeddings_path / "faiss_index"
        
        if not load_path.exists():
            return False
        
        try:
            self.vector_store = FAISS.load_local(
                str(load_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"Vector store loaded from {load_path}")
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def build_index(self, force_rebuild: bool = False):
        """
        Build or load the vector store index
        
        Args:
            force_rebuild: Force rebuild even if index exists
        """
        # Try to load existing index
        if not force_rebuild and self.load_vector_store():
            return
        
        print("Building new vector store index...")
        
        # Load and process documents
        documents = self.load_documents()
        chunks = self.chunk_documents(documents)
        
        # Create embeddings and vector store
        self.vector_store = self.create_embeddings(chunks)
        
        # Save to disk
        self.save_vector_store()
        
        print("RAG index built successfully!")
    
    def search(
        self, 
        query: str, 
        k: int = 3
    ) -> List[Tuple[Document, float]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (Document, score) tuples
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call build_index() first.")
        
        # Perform similarity search with scores
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        return results
    
    def get_context(
        self, 
        query: str, 
        k: int = 3
    ) -> Tuple[str, List[str]]:
        """
        Get context and sources for a query
        
        Args:
            query: Search query
            k: Number of chunks to retrieve
            
        Returns:
            Tuple of (context_string, list_of_sources)
        """
        results = self.search(query, k=k)
        
        # Extract context and sources
        context_parts = []
        sources = set()
        
        for doc, score in results:
            context_parts.append(doc.page_content)
            sources.add(doc.metadata.get("source", "Unknown"))
        
        context = "\n\n---\n\n".join(context_parts)
        
        return context, list(sources)


# Utility function for testing
def test_rag_system():
    """Test the RAG system"""
    rag = RAGSystem()
    
    # Build index
    rag.build_index()
    
    # Test search
    test_queries = [
        "What is the remote work policy?",
        "How do I upload files using the API?",
        "What are the vacation days?",
        "What is CloudStorage Pro?"
    ]
    
    print("\n" + "="*60)
    print("TESTING RAG SYSTEM")
    print("="*60 + "\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        context, sources = rag.get_context(query, k=2)
        print(f"Sources: {sources}")
        print(f"Context preview: {context[:200]}...")
        print("-" * 60 + "\n")


if __name__ == "__main__":
    test_rag_system()