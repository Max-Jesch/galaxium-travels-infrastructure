#!/usr/bin/env python3
"""
Vector Format Fix Script
Fixes the vector storage format in AstraDB to use proper array format instead of binary.
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


def fix_vector_format():
    """Fix vector format in existing collection."""
    
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
        
        # Get the existing collection
        collection_name = "galaxium_travels_rag"
        logger.info(f"Accessing collection: {collection_name}")
        collection = database.get_collection(collection_name)
        
        # Get all documents from the collection
        logger.info("Retrieving all documents...")
        all_docs = list(collection.find({}, limit=1000))
        logger.info(f"Found {len(all_docs)} documents")
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # Process each document
        for i, doc in enumerate(all_docs):
            logger.info(f"Processing document {i+1}/{len(all_docs)}")
            
            # Get the page content
            page_content = doc.get('page_content', '')
            if not page_content:
                logger.warning(f"Document {i+1} has no page_content, skipping")
                continue
            
            # Generate new embedding
            logger.info("Generating new embedding...")
            new_embedding = embeddings.embed_query(page_content)
            
            # Ensure it's a list of floats
            if isinstance(new_embedding, np.ndarray):
                new_embedding = new_embedding.tolist()
            
            # Update the document with proper vector format
            doc_id = doc.get('_id')
            if doc_id:
                logger.info(f"Updating document {doc_id} with proper vector format...")
                
                # Update the document with the new vector format
                collection.update_one(
                    {"_id": doc_id},
                    {
                        "$set": {
                            "$vector": new_embedding  # Store as array, not binary
                        }
                    }
                )
                logger.info(f"Updated document {doc_id}")
            else:
                logger.warning(f"Document {i+1} has no _id, skipping")
        
        logger.info("Vector format fix completed successfully!")
        
        # Test the fix with a sample search
        logger.info("Testing the fix with a sample search...")
        test_embedding = embeddings.embed_query("suborbital space experience")
        if isinstance(test_embedding, np.ndarray):
            test_embedding = test_embedding.tolist()
        
        results = collection.vector_find(
            test_embedding,
            limit=3,
            fields=["page_content", "metadata"]
        )
        
        logger.info(f"Test search returned {len(results)} results")
        for i, result in enumerate(results, 1):
            logger.info(f"Result {i}: {result.get('page_content', '')[:100]}...")
        
    except Exception as e:
        logger.error(f"Error fixing vector format: {e}")
        raise


if __name__ == "__main__":
    fix_vector_format()

