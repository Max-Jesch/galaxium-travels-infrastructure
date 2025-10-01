#!/usr/bin/env python3
"""
Simple RAG Script for Galaxium Travels
Creates OpenAI embeddings and stores them in AstraDB for RAG functionality.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from astrapy import DataAPIClient
    from langchain_astradb import AstraDBVectorStore
    from langchain_openai import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
except ImportError as e:
    logger.error(f"Missing required dependencies: {e}")
    logger.error("Please install required packages: pip install langchain-astradb langchain-openai astrapy")
    sys.exit(1)


class GalaxiumRAG:
    """Simple RAG implementation for Galaxium Travels using OpenAI embeddings and AstraDB."""
    
    def __init__(self, 
                 astra_token: str,
                 astra_endpoint: str,
                 openai_api_key: str,
                 collection_name: str = "galaxium_travels",
                 namespace: str = "default_keyspace"):
        """
        Initialize the RAG system.
        
        Args:
            astra_token: AstraDB application token
            astra_endpoint: AstraDB API endpoint
            openai_api_key: OpenAI API key
            collection_name: Name of the collection in AstraDB
            namespace: Keyspace/namespace in AstraDB
        """
        self.astra_token = astra_token
        self.astra_endpoint = astra_endpoint
        self.openai_api_key = openai_api_key
        self.collection_name = collection_name
        self.namespace = namespace
        
        # Initialize components
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = None
        
    def load_documents(self, docs_dir: str = "sample_docs") -> List[Document]:
        """Load documents from the sample_docs directory."""
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            raise FileNotFoundError(f"Documents directory not found: {docs_path}")
        
        documents = []
        
        for doc_file in docs_path.glob("*.md"):
            logger.info(f"Loading document: {doc_file.name}")
            
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create document with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "source": str(doc_file),
                    "filename": doc_file.name,
                    "title": doc_file.stem.replace("_", " ").title()
                }
            )
            documents.append(doc)
        
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks for better retrieval."""
        logger.info("Chunking documents...")
        
        all_chunks = []
        for doc in documents:
            chunks = self.text_splitter.split_documents([doc])
            # Add chunk index to metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks"] = len(chunks)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
    
    def setup_vector_store(self) -> AstraDBVectorStore:
        """Set up the AstraDB vector store."""
        logger.info("Setting up AstraDB vector store...")
        
        try:
            vector_store = AstraDBVectorStore(
                embedding=self.embeddings,
                collection_name=self.collection_name,
                token=self.astra_token,
                api_endpoint=self.astra_endpoint,
                namespace=self.namespace,
                # Ensure proper vector format
                vectorize_options=None,  # Use external embeddings
            )
            
            self.vector_store = vector_store
            logger.info("Vector store initialized successfully")
            return vector_store
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def ingest_documents(self, documents: List[Document]) -> None:
        """Ingest documents into the vector store."""
        if not self.vector_store:
            self.setup_vector_store()
        
        logger.info(f"Ingesting {len(documents)} documents into vector store...")
        
        try:
            # Add documents to vector store
            self.vector_store.add_documents(documents)
            logger.info("Documents ingested successfully")
            
        except Exception as e:
            logger.error(f"Failed to ingest documents: {e}")
            raise
    
    def search(self, query: str, k: int = 4) -> List[Document]:
        """Search for relevant documents."""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Please run setup first.")
        
        logger.info(f"Searching for: {query}")
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} relevant documents")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def search_with_scores(self, query: str, k: int = 4) -> List[tuple]:
        """Search for relevant documents with similarity scores."""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Please run setup first.")
        
        logger.info(f"Searching with scores for: {query}")
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(results)} relevant documents with scores")
            return results
            
        except Exception as e:
            logger.error(f"Search with scores failed: {e}")
            raise


def main():
    """Main function to demonstrate the RAG system."""
    
    # Configuration - Set these environment variables or update these values
    ASTRA_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    ASTRA_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Check for required environment variables
    if not ASTRA_TOKEN:
        logger.error("ASTRA_DB_APPLICATION_TOKEN environment variable not set")
        sys.exit(1)
    
    if not ASTRA_ENDPOINT:
        logger.error("ASTRA_DB_API_ENDPOINT environment variable not set")
        sys.exit(1)
    
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    try:
        # Initialize RAG system
        logger.info("Initializing Galaxium RAG system...")
        rag = GalaxiumRAG(
            astra_token=ASTRA_TOKEN,
            astra_endpoint=ASTRA_ENDPOINT,
            openai_api_key=OPENAI_API_KEY,
            collection_name="galaxium_travels_rag",
            namespace="default_keyspace"
        )
        
        # Load and process documents
        logger.info("Loading documents...")
        documents = rag.load_documents("sample_docs")
        
        logger.info("Chunking documents...")
        chunks = rag.chunk_documents(documents)
        
        # Set up vector store and ingest documents
        logger.info("Setting up vector store and ingesting documents...")
        rag.setup_vector_store()
        rag.ingest_documents(chunks)
        
        # Example searches
        logger.info("Performing example searches...")
        
        # Search 1: Suborbital experience
        print("\n" + "="*50)
        print("SEARCH 1: Suborbital Experience")
        print("="*50)
        results = rag.search("What is the suborbital space experience?", k=3)
        for i, doc in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Source: {doc.metadata.get('filename', 'Unknown')}")
            print(f"Content: {doc.page_content[:200]}...")
        
        # Search 2: Pricing information
        print("\n" + "="*50)
        print("SEARCH 2: Pricing Information")
        print("="*50)
        results = rag.search("What are the pricing options for space travel?", k=3)
        for i, doc in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Source: {doc.metadata.get('filename', 'Unknown')}")
            print(f"Content: {doc.page_content[:200]}...")
        
        # Search 3: Safety information
        print("\n" + "="*50)
        print("SEARCH 3: Safety Information")
        print("="*50)
        results = rag.search("What safety features are available?", k=3)
        for i, doc in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Source: {doc.metadata.get('filename', 'Unknown')}")
            print(f"Content: {doc.page_content[:200]}...")
        
        # Search with scores
        print("\n" + "="*50)
        print("SEARCH 4: Search with Similarity Scores")
        print("="*50)
        results_with_scores = rag.search_with_scores("International Space Station visit", k=3)
        for i, (doc, score) in enumerate(results_with_scores, 1):
            print(f"\nResult {i} (Score: {score:.4f}):")
            print(f"Source: {doc.metadata.get('filename', 'Unknown')}")
            print(f"Content: {doc.page_content[:200]}...")
        
        logger.info("RAG system demonstration completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
