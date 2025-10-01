#!/usr/bin/env python3
"""
Fixed RAG Script for Galaxium Travels
Creates OpenAI embeddings and stores them in AstraDB with proper vector format.
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
    from langchain_openai import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    import numpy as np
except ImportError as e:
    logger.error(f"Missing required dependencies: {e}")
    logger.error("Please install required packages: pip install langchain-astradb langchain-openai astrapy")
    sys.exit(1)


class FixedGalaxiumRAG:
    """Fixed RAG implementation that ensures proper vector format in AstraDB."""
    
    def __init__(self, 
                 astra_token: str,
                 astra_endpoint: str,
                 openai_api_key: str,
                 collection_name: str = "galaxium_travels_fixed",
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
        self.database = None
        self.collection = None
        
    def setup_database_connection(self):
        """Set up direct AstraDB connection."""
        logger.info("Setting up AstraDB connection...")
        
        try:
            client = DataAPIClient(token=self.astra_token)
            self.database = client.get_database(
                api_endpoint=self.astra_endpoint,
                token=self.astra_token
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_collection(self):
        """Create collection with proper vector configuration."""
        logger.info(f"Creating collection: {self.collection_name}")
        
        try:
            # Create collection
            self.database.create_collection(
                name=self.collection_name
            )
            logger.info("Collection created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info("Collection already exists, using existing collection")
            else:
                logger.error(f"Failed to create collection: {e}")
                raise
    
    def get_collection(self):
        """Get the collection reference."""
        if not self.collection:
            self.collection = self.database.get_collection(self.collection_name)
        return self.collection
    
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
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        
        try:
            embeddings = self.embeddings.embed_documents(texts)
            logger.info("Embeddings generated successfully")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def store_documents_with_vectors(self, documents: List[Document]) -> None:
        """Store documents with properly formatted vectors."""
        logger.info(f"Storing {len(documents)} documents with vectors...")
        
        # Extract texts for embedding
        texts = [doc.page_content for doc in documents]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Prepare documents for storage
        documents_to_store = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Ensure embedding is a list of floats
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            # Create document with proper vector format
            doc_data = {
                "_id": f"doc_{i}_{hash(doc.page_content) % 10000}",
                "page_content": doc.page_content,
                "$vector": embedding,  # Store as array, not binary
                "metadata": doc.metadata
            }
            documents_to_store.append(doc_data)
        
        # Store in batches
        batch_size = 20
        collection = self.get_collection()
        
        for i in range(0, len(documents_to_store), batch_size):
            batch = documents_to_store[i:i + batch_size]
            logger.info(f"Storing batch {i//batch_size + 1}/{(len(documents_to_store) + batch_size - 1)//batch_size}")
            
            try:
                collection.insert_many(batch)
                logger.info(f"Stored {len(batch)} documents")
            except Exception as e:
                logger.error(f"Failed to store batch: {e}")
                raise
        
        logger.info("All documents stored successfully")
    
    def search_similar(self, query: str, k: int = 4) -> List[Dict]:
        """Search for similar documents."""
        logger.info(f"Searching for: {query}")
        
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Ensure embedding is a list of floats
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Search using vector similarity
            collection = self.get_collection()
            results = collection.vector_find(
                query_embedding,
                limit=k,
                fields=["page_content", "metadata"]
            )
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def search_with_scores(self, query: str, k: int = 4) -> List[tuple]:
        """Search for similar documents with scores."""
        logger.info(f"Searching with scores for: {query}")
        
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Ensure embedding is a list of floats
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Search using vector similarity with scores
            collection = self.get_collection()
            results = collection.vector_find(
                query_embedding,
                limit=k,
                fields=["page_content", "metadata"],
                include_similarities=True
            )
            
            # Format results with scores
            formatted_results = []
            for result in results:
                score = result.get('$similarity', 0.0)
                doc = Document(
                    page_content=result.get('page_content', ''),
                    metadata=result.get('metadata', {})
                )
                formatted_results.append((doc, score))
            
            logger.info(f"Found {len(formatted_results)} similar documents with scores")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search with scores failed: {e}")
            raise


def main():
    """Main function to demonstrate the fixed RAG system."""
    
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
        logger.info("Initializing Fixed Galaxium RAG system...")
        rag = FixedGalaxiumRAG(
            astra_token=ASTRA_TOKEN,
            astra_endpoint=ASTRA_ENDPOINT,
            openai_api_key=OPENAI_API_KEY,
            collection_name="galaxium_travels_fixed",
            namespace="default_keyspace"
        )
        
        # Set up database and collection
        rag.setup_database_connection()
        rag.create_collection()
        
        # Load and process documents
        logger.info("Loading documents...")
        documents = rag.load_documents("sample_docs")
        
        logger.info("Chunking documents...")
        chunks = rag.chunk_documents(documents)
        
        # Store documents with proper vector format
        logger.info("Storing documents with proper vector format...")
        rag.store_documents_with_vectors(chunks)
        
        # Example searches
        logger.info("Performing example searches...")
        
        # Search 1: Suborbital experience
        print("\n" + "="*50)
        print("SEARCH 1: Suborbital Experience")
        print("="*50)
        results = rag.search_similar("What is the suborbital space experience?", k=3)
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Content: {result.get('page_content', '')[:200]}...")
            print(f"Metadata: {result.get('metadata', {})}")
        
        # Search 2: Pricing information
        print("\n" + "="*50)
        print("SEARCH 2: Pricing Information")
        print("="*50)
        results = rag.search_similar("What are the pricing options for space travel?", k=3)
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Content: {result.get('page_content', '')[:200]}...")
            print(f"Metadata: {result.get('metadata', {})}")
        
        # Search 3: Safety information
        print("\n" + "="*50)
        print("SEARCH 3: Safety Information")
        print("="*50)
        results = rag.search_similar("What safety features are available?", k=3)
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Content: {result.get('page_content', '')[:200]}...")
            print(f"Metadata: {result.get('metadata', {})}")
        
        # Search with scores
        print("\n" + "="*50)
        print("SEARCH 4: Search with Similarity Scores")
        print("="*50)
        results_with_scores = rag.search_with_scores("International Space Station visit", k=3)
        for i, (doc, score) in enumerate(results_with_scores, 1):
            print(f"\nResult {i} (Score: {score:.4f}):")
            print(f"Content: {doc.page_content[:200]}...")
            print(f"Metadata: {doc.metadata}")
        
        logger.info("Fixed RAG system demonstration completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
