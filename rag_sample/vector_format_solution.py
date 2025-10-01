#!/usr/bin/env python3
"""
Vector Format Solution
This script demonstrates the issue and provides a workaround for the vector format problem.
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
    from langchain_astradb import AstraDBVectorStore
    import numpy as np
except ImportError as e:
    logger.error(f"Missing required dependencies: {e}")
    sys.exit(1)


def demonstrate_vector_format_issue():
    """Demonstrate the vector format issue and provide solution."""
    
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
        
        # Get a sample document to examine the vector format
        logger.info("Retrieving a sample document to examine vector format...")
        sample_docs = list(collection.find({}, limit=1))
        
        if sample_docs:
            sample_doc = sample_docs[0]
            logger.info("Sample document found:")
            logger.info(f"Document ID: {sample_doc.get('_id')}")
            logger.info(f"Has $vector field: {'$vector' in sample_doc}")
            
            if '$vector' in sample_doc:
                vector_field = sample_doc['$vector']
                logger.info(f"Vector field type: {type(vector_field)}")
                logger.info(f"Vector field value: {vector_field}")
                
                if isinstance(vector_field, dict) and '$binary' in vector_field:
                    logger.error("❌ PROBLEM IDENTIFIED: Vector is stored in binary format!")
                    logger.error(f"Current format: {vector_field}")
                    logger.error("This is the issue - vectors should be stored as arrays, not binary")
                elif isinstance(vector_field, list):
                    logger.info("✅ Vector is stored in proper array format")
                    logger.info(f"Vector length: {len(vector_field)}")
                    logger.info(f"First few values: {vector_field[:5]}")
                else:
                    logger.warning(f"Unexpected vector format: {type(vector_field)}")
            else:
                logger.warning("No $vector field found in document")
        else:
            logger.warning("No documents found in collection")
        
        # Demonstrate the correct approach
        logger.info("\n" + "="*60)
        logger.info("SOLUTION: Use direct AstraDB API with proper vector format")
        logger.info("="*60)
        
        # Create a new collection with a different name for testing
        test_collection_name = "galaxium_travels_correct_format"
        
        try:
            # Delete test collection if it exists
            database.drop_collection(test_collection_name)
            logger.info(f"Deleted existing test collection: {test_collection_name}")
        except:
            pass
        
        # Create new collection
        logger.info(f"Creating test collection: {test_collection_name}")
        database.create_collection(name=test_collection_name)
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # Create a test document with proper vector format
        test_text = "This is a test document for vector format verification."
        test_embedding = embeddings.embed_query(test_text)
        
        # Ensure embedding is a list of floats
        if isinstance(test_embedding, np.ndarray):
            test_embedding = test_embedding.tolist()
        
        # Create document with proper vector format
        test_doc = {
            "_id": "test_doc_001",
            "page_content": test_text,
            "$vector": test_embedding,  # Store as array, not binary
            "metadata": {
                "source": "test",
                "filename": "test.txt"
            }
        }
        
        # Get the test collection
        test_collection = database.get_collection(test_collection_name)
        
        # Insert the test document
        logger.info("Inserting test document with proper vector format...")
        try:
            test_collection.insert_one(test_doc)
            logger.info("✅ Test document inserted successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to insert test document: {e}")
            return
        
        # Verify the vector format
        logger.info("Verifying the vector format...")
        inserted_doc = test_collection.find_one({"_id": "test_doc_001"})
        
        if inserted_doc and '$vector' in inserted_doc:
            vector_field = inserted_doc['$vector']
            logger.info(f"Vector field type: {type(vector_field)}")
            
            if isinstance(vector_field, list):
                logger.info("✅ SUCCESS: Vector is stored in proper array format!")
                logger.info(f"Vector length: {len(vector_field)}")
                logger.info(f"First few values: {vector_field[:5]}")
                logger.info("This is the correct format for downstream systems")
            else:
                logger.error(f"❌ Vector is still in wrong format: {type(vector_field)}")
        else:
            logger.error("❌ Could not verify vector format")
        
        # Clean up test collection
        logger.info("Cleaning up test collection...")
        database.drop_collection(test_collection_name)
        
        logger.info("\n" + "="*60)
        logger.info("RECOMMENDATION:")
        logger.info("="*60)
        logger.info("1. The issue is that langchain-astradb stores vectors in binary format")
        logger.info("2. For downstream systems to work, vectors must be stored as arrays")
        logger.info("3. Use direct AstraDB API calls instead of langchain-astradb")
        logger.info("4. Store vectors as: $vector: [0.00856781, -0.032348633, ...]")
        logger.info("5. NOT as: $vector: {'$binary': 'POpfcbtoVzc8AX37vQT97bybdVI7...'}")
        
    except Exception as e:
        logger.error(f"Error in vector format demonstration: {e}")
        raise


if __name__ == "__main__":
    demonstrate_vector_format_issue()

