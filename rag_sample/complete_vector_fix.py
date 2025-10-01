#!/usr/bin/env python3
"""
Complete Vector Format Fix
Deletes existing collection, creates new one with proper vector format, and re-ingests data.
"""

import os
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from astrapy import DataAPIClient
    from langchain_openai import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    import numpy as np
except ImportError as e:
    logger.error(f"Missing required dependencies: {e}")
    sys.exit(1)


def complete_vector_fix():
    """Complete fix for vector format issues."""
    
    # Get environment variables
    ASTRA_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    ASTRA_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not all([ASTRA_TOKEN, ASTRA_ENDPOINT, OPENAI_API_KEY]):
        logger.error("Missing required environment variables")
        return
    
    try:
        # Connect to database
        logger.info("Connecting to AstraDB...")
        client = DataAPIClient(token=ASTRA_TOKEN)
        database = client.get_database(api_endpoint=ASTRA_ENDPOINT, token=ASTRA_TOKEN)
        
        collection_name = "galaxium_travels_rag"
        
        # Delete existing collection if it exists
        logger.info(f"Checking if collection {collection_name} exists...")
        try:
            existing_collection = database.get_collection(collection_name)
            logger.info("Collection exists, deleting it...")
            database.drop_collection(collection_name)
            logger.info("Collection deleted successfully")
        except Exception as e:
            logger.info(f"Collection doesn't exist or couldn't be deleted: {e}")
        
        # Create new collection
        logger.info(f"Creating new collection: {collection_name}")
        database.create_collection(name=collection_name)
        logger.info("Collection created successfully")
        
        # Load and process documents
        logger.info("Loading documents from sample_docs...")
        docs_path = Path("sample_docs")
        documents = []
        
        for doc_file in docs_path.glob("*.md"):
            logger.info(f"Loading document: {doc_file.name}")
            
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
        
        # Chunk documents
        logger.info("Chunking documents...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        all_chunks = []
        for doc in documents:
            chunks = text_splitter.split_documents([doc])
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks"] = len(chunks)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks")
        
        # Initialize embeddings
        logger.info("Initializing OpenAI embeddings...")
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # Get the new collection
        collection = database.get_collection(collection_name)
        
        # Process and store documents with proper vector format
        logger.info("Processing and storing documents with proper vector format...")
        
        batch_size = 10
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(all_chunks) + batch_size - 1)//batch_size}")
            
            # Extract texts for embedding
            texts = [chunk.page_content for chunk in batch]
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            batch_embeddings = embeddings.embed_documents(texts)
            
            # Prepare documents for storage
            documents_to_store = []
            for j, (chunk, embedding) in enumerate(zip(batch, batch_embeddings)):
                # Ensure embedding is a list of floats
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                
                # Create document with proper vector format
                doc_data = {
                    "_id": f"doc_{i+j}_{hash(chunk.page_content) % 10000}",
                    "page_content": chunk.page_content,
                    "$vector": embedding,  # Store as array, not binary
                    "metadata": chunk.metadata
                }
                documents_to_store.append(doc_data)
            
            # Store batch
            logger.info(f"Storing {len(documents_to_store)} documents...")
            try:
                collection.insert_many(documents_to_store)
                logger.info(f"Successfully stored batch {i//batch_size + 1}")
            except Exception as e:
                logger.error(f"Failed to store batch: {e}")
                raise
        
        logger.info("All documents stored successfully with proper vector format!")
        
        # Test the fix with a sample search
        logger.info("Testing the fix with a sample search...")
        test_embedding = embeddings.embed_query("suborbital space experience")
        if isinstance(test_embedding, np.ndarray):
            test_embedding = test_embedding.tolist()
        
        # Use the correct vector search method
        results = collection.vector_find(
            test_embedding,
            limit=3,
            fields=["page_content", "metadata"]
        )
        
        logger.info(f"Test search returned {len(results)} results")
        for i, result in enumerate(results, 1):
            content = result.get('page_content', '')
            metadata = result.get('metadata', {})
            logger.info(f"Result {i}: {content[:100]}...")
            logger.info(f"Metadata: {metadata}")
        
        logger.info("Vector format fix completed successfully!")
        logger.info("Vectors are now stored in proper array format: $vector: [0.00856781, -0.032348633, ...]")
        
    except Exception as e:
        logger.error(f"Error in complete vector fix: {e}")
        raise


if __name__ == "__main__":
    complete_vector_fix()
