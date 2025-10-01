#!/usr/bin/env python3
"""
Vector indexer for Galaxium Travels documents
Handles OpenAI embeddings and AstraDB storage with proper vector format for Langflow compatibility
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Core libraries
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from astrapy.api_options import APIOptions, SerdesOptions
from astrapy import DataAPIClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorIndexer:
    """Handles vector generation and AstraDB storage with proper format for Langflow"""
    
    def __init__(self, config):
        self.config = config
        self.embeddings = None
        self.vectorstore = None
        self.database = None
        self.collection = None
        
        # Initialize OpenAI
        self._initialize_openai()
        
        # Initialize AstraDB
        self._initialize_astradb()
    
    def _initialize_openai(self):
        """Initialize OpenAI embeddings"""
        logger.info("Initializing OpenAI embeddings...")
        self.embeddings = OpenAIEmbeddings()
        logger.info("✅ OpenAI embeddings initialized")
    
    def _initialize_astradb(self):
        """Initialize AstraDB with proper vector format configuration"""
        logger.info("Initializing AstraDB with float array vector support...")
        
        # Configure AstraPy to use plain float arrays instead of binary encoding
        api_options = APIOptions(
            serdes_options=SerdesOptions(
                binary_encode_vectors=False,  # This is the key flag!
                custom_datatypes_in_reading=False
            )
        )
        
        try:
            # Create AstraDB client
            client = DataAPIClient(
                token=self.config.astra_db_application_token,
                api_options=api_options
            )
            
            # Get database
            self.database = client.get_database(
                api_endpoint=self.config.astra_db_api_endpoint,
                token=self.config.astra_db_application_token,
                keyspace=self.config.astra_db_keyspace
            )
            
            # Get collection
            self.collection = self.database.get_collection(
                self.config.astra_db_collection_name,
                keyspace=self.config.astra_db_keyspace
            )
            
            logger.info("✅ AstraDB initialized with float array vector support")
            
        except Exception as e:
            logger.error(f"❌ Error initializing AstraDB: {e}")
            raise
    
    def create_vectorstore(self):
        """Create LangChain AstraDB vector store with proper configuration"""
        logger.info("Creating LangChain AstraDB vector store...")
        
        # Configure AstraPy to use plain float arrays instead of binary encoding
        api_options = APIOptions(
            serdes_options=SerdesOptions(
                binary_encode_vectors=False,  # This is the key flag!
                custom_datatypes_in_reading=False
            )
        )
        
        try:
            self.vectorstore = AstraDBVectorStore(
                embedding=self.embeddings,
                collection_name=self.config.astra_db_collection_name,
                api_endpoint=self.config.astra_db_api_endpoint,
                token=self.config.astra_db_application_token,
                namespace=self.config.astra_db_keyspace,
                pre_delete_collection=True,  # Clear existing data
                api_options=api_options,  # Use plain float arrays
            )
            logger.info("✅ LangChain AstraDB vector store created")
            
        except Exception as e:
            logger.error(f"❌ Error creating vector store: {e}")
            raise
    
    def index_documents(self, documents: Dict[str, Any]) -> bool:
        """Index all documents with embeddings and proper vector format"""
        logger.info(f"Indexing {len(documents)} documents...")
        
        try:
            # Convert documents to LangChain format
            langchain_docs = []
            
            for doc_id, doc in documents.items():
                # Create metadata with relationship information
                metadata = doc.metadata.copy()
                metadata.update({
                    'doc_id': doc_id,
                    'doc_type': doc.doc_type,
                    'title': doc.title,
                    'file_path': doc.file_path,
                    'category': doc.category,
                    'linked_docs': doc.linked_docs  # Resolved document IDs for graph traversal
                })
                
                # Create LangChain document
                from langchain_core.documents import Document
                langchain_doc = Document(
                    page_content=doc.content,
                    metadata=metadata
                )
                langchain_docs.append(langchain_doc)
            
            # Add documents to vector store using standard method
            if langchain_docs:
                logger.info(f"Adding {len(langchain_docs)} documents to vector store...")
                self.vectorstore.add_documents(langchain_docs)
                logger.info(f"✅ Successfully indexed {len(langchain_docs)} documents")
            else:
                logger.warning("No documents to index")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error indexing documents: {e}")
            return False
    
    def verify_vector_format(self, limit: int = 5) -> bool:
        """Verify that vectors are stored as float arrays, not binary"""
        logger.info("Verifying vector format...")
        
        try:
            # Get a few documents to inspect their structure
            documents = list(self.collection.find({}, limit=limit))
            logger.info(f"Retrieved {len(documents)} documents for verification")
            
            all_correct = True
            
            for i, doc in enumerate(documents):
                logger.info(f"\nDocument {i+1}: {doc.get('_id', 'N/A')}")
                
                # Check for vector field
                if '$vector' in doc:
                    vector = doc['$vector']
                    if isinstance(vector, list):
                        logger.info(f"  ✅ Vector stored as float array: {len(vector)} dimensions")
                        logger.info(f"  Sample: {vector[:5]}...")
                    elif isinstance(vector, dict) and '$binary' in vector:
                        logger.error(f"  ❌ Vector stored as binary: {len(vector['$binary'])} chars")
                        all_correct = False
                    else:
                        logger.warning(f"  ⚠️  Vector stored in unknown format: {type(vector)}")
                        all_correct = False
                else:
                    logger.error("  ❌ No $vector field found")
                    all_correct = False
                
                # Check metadata
                metadata = doc.get('metadata', {})
                linked_docs = metadata.get('linked_docs', [])
                logger.info(f"  Linked docs: {len(linked_docs)} relationships")
                if linked_docs:
                    logger.info(f"  Sample links: {linked_docs[:3]}")
            
            if all_correct:
                logger.info("✅ All vectors stored as float arrays - Langflow compatible!")
            else:
                logger.error("❌ Some vectors not stored as float arrays - Langflow may have issues")
            
            return all_correct
            
        except Exception as e:
            logger.error(f"❌ Error verifying vector format: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed database"""
        try:
            # Count total documents using find with limit
            all_docs = list(self.collection.find({}))
            total_docs = len(all_docs)
            
            # Count documents with relationships
            docs_with_links = sum(1 for doc in all_docs 
                                if doc.get('metadata', {}).get('linked_docs'))
            
            # Count total relationships
            total_relationships = sum(len(doc.get('metadata', {}).get('linked_docs', [])) 
                                    for doc in all_docs)
            
            stats = {
                'total_documents': total_docs,
                'documents_with_relationships': docs_with_links,
                'total_relationships': total_relationships,
                'collection_name': self.config.astra_db_collection_name,
                'keyspace': self.config.astra_db_keyspace
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def test_vector_search(self, query: str = "space travel", limit: int = 3) -> List[Dict[str, Any]]:
        """Test vector search functionality"""
        logger.info(f"Testing vector search with query: '{query}'")
        
        try:
            # Check if vectorstore is available
            if not self.vectorstore:
                logger.error("❌ Vector store not initialized")
                return []
            
            # Perform similarity search
            results = self.vectorstore.similarity_search(query, k=limit)
            
            search_results = []
            for i, doc in enumerate(results):
                result = {
                    'rank': i + 1,
                    'title': doc.metadata.get('title', 'Unknown'),
                    'doc_type': doc.metadata.get('doc_type', 'Unknown'),
                    'category': doc.metadata.get('category', 'Unknown'),
                    'content_preview': doc.page_content[:200] + '...',
                    'linked_docs': doc.metadata.get('linked_docs', [])
                }
                search_results.append(result)
            
            logger.info(f"✅ Vector search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Error testing vector search: {e}")
            return []
