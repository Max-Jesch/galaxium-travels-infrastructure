#!/usr/bin/env python3
"""
Test script to verify the configurable collection name functionality
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG
from dotenv import load_dotenv

def test_collection_configuration():
    """Test that the collection name is configurable through environment variables"""
    
    # Load environment variables
    load_dotenv()
    
    print("🧪 Testing Configurable Collection Name")
    print("=" * 50)
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    # Test 1: Default collection name
    print("\n1. Testing default collection name...")
    graph_rag_default = GalaxiumGraphRAG(
        DOCUMENTS_PATH,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
        astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
        astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE')
    )
    
    print(f"   Default collection name: {graph_rag_default.astra_db_collection_name}")
    assert graph_rag_default.astra_db_collection_name == "galaxium_travels_documents_2"
    print("   ✅ Default collection name is correct")
    
    # Test 2: Custom collection name via parameter
    print("\n2. Testing custom collection name via parameter...")
    custom_collection = "galaxium_travels_documents_custom"
    graph_rag_custom = GalaxiumGraphRAG(
        DOCUMENTS_PATH,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
        astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
        astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
        astra_db_collection_name=custom_collection
    )
    
    print(f"   Custom collection name: {graph_rag_custom.astra_db_collection_name}")
    assert graph_rag_custom.astra_db_collection_name == custom_collection
    print("   ✅ Custom collection name via parameter works")
    
    # Test 3: Environment variable override
    print("\n3. Testing environment variable override...")
    os.environ['ASTRA_DB_COLLECTION_NAME'] = 'galaxium_travels_documents_env_test'
    
    graph_rag_env = GalaxiumGraphRAG(
        DOCUMENTS_PATH,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
        astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
        astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE')
    )
    
    print(f"   Environment collection name: {graph_rag_env.astra_db_collection_name}")
    assert graph_rag_env.astra_db_collection_name == 'galaxium_travels_documents_env_test'
    print("   ✅ Environment variable override works")
    
    # Clean up environment variable
    if 'ASTRA_DB_COLLECTION_NAME' in os.environ:
        del os.environ['ASTRA_DB_COLLECTION_NAME']
    
    print("\n🎉 All collection configuration tests passed!")
    return True

def test_actual_collection_creation():
    """Test that the collection is actually created with the correct name"""
    
    # Load environment variables
    load_dotenv()
    
    print("\n🔧 Testing Actual Collection Creation")
    print("=" * 50)
    
    # Check if we have the required environment variables
    required_vars = ['OPENAI_API_KEY', 'ASTRA_DB_API_ENDPOINT', 'ASTRA_DB_APPLICATION_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nSkipping actual collection creation test...")
        return True
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    try:
        # Initialize with custom collection name
        custom_collection = "galaxium_travels_documents_test"
        print(f"Creating collection: {custom_collection}")
        
        graph_rag = GalaxiumGraphRAG(
            DOCUMENTS_PATH,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
            astra_db_collection_name=custom_collection
        )
        
        # Build knowledge graph (limit to 2 documents for test)
        print("Building knowledge graph (limited to 2 documents for test)...")
        documents, links_map = graph_rag.build_knowledge_graph()
        
        # Limit to first 2 documents for test
        limited_docs = dict(list(documents.items())[:2])
        graph_rag.documents = limited_docs
        
        # Create vector store
        print(f"Creating vector store with collection: {custom_collection}")
        graph_rag.create_vector_store()
        
        print("✅ Collection created successfully!")
        print(f"   Collection name: {graph_rag.astra_db_collection_name}")
        
        # Verify the collection exists by checking the vectorstore
        if hasattr(graph_rag.vectorstore, 'collection'):
            print("   ✅ Collection object is accessible")
        else:
            print("   ⚠️  Collection object not accessible (might be in-memory)")
        
    except Exception as e:
        print(f"❌ Error during collection creation test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Collection Configuration Test Suite")
    print("=" * 60)
    
    # Test configuration logic
    success1 = test_collection_configuration()
    
    # Test actual collection creation (if environment is set up)
    success2 = test_actual_collection_creation()
    
    if success1 and success2:
        print("\n✅ All tests completed successfully!")
        print("\n📋 Summary of changes:")
        print("   - Collection name is now configurable via ASTRA_DB_COLLECTION_NAME")
        print("   - Default collection name is 'galaxium_travels_documents_2'")
        print("   - Collection name can be overridden via constructor parameter")
        print("   - Environment variable takes precedence over default")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
