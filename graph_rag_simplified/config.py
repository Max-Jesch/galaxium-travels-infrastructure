#!/usr/bin/env python3
"""
Configuration management for Galaxium Document Preprocessing & Vector Indexing
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the document preprocessing system"""
    
    def __init__(self):
        # Load environment variables
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.astra_db_api_endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')
        self.astra_db_application_token = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
        self.astra_db_keyspace = os.getenv('ASTRA_DB_KEYSPACE')
        self.astra_db_collection_name = os.getenv('ASTRA_DB_COLLECTION_NAME', 'galaxium_travels_documents_simplified')
        
        # Document paths
        self.documents_path = Path(__file__).parent / "97_raw_markdown_files"
        
        # Validate required environment variables
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required configuration is present"""
        required_vars = {
            'OPENAI_API_KEY': self.openai_api_key,
            'ASTRA_DB_API_ENDPOINT': self.astra_db_api_endpoint,
            'ASTRA_DB_APPLICATION_TOKEN': self.astra_db_application_token,
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Check if documents path exists
        if not self.documents_path.exists():
            raise FileNotFoundError(f"Documents path not found: {self.documents_path}")
    
    def get_astra_db_config(self):
        """Get AstraDB configuration dictionary"""
        return {
            'api_endpoint': self.astra_db_api_endpoint,
            'token': self.astra_db_application_token,
            'keyspace': self.astra_db_keyspace,
            'collection_name': self.astra_db_collection_name
        }
    
    def get_openai_config(self):
        """Get OpenAI configuration dictionary"""
        return {
            'api_key': self.openai_api_key
        }
    
    def __str__(self):
        """String representation of configuration"""
        return f"""
Configuration:
  Documents Path: {self.documents_path}
  Collection Name: {self.astra_db_collection_name}
  AstraDB Endpoint: {self.astra_db_api_endpoint}
  Keyspace: {self.astra_db_keyspace}
  OpenAI API Key: {'***' + self.openai_api_key[-4:] if self.openai_api_key else 'Not set'}
        """.strip()

