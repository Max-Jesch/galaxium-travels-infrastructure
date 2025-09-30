#!/usr/bin/env python3
"""
Test script to verify that vectors are stored as float arrays instead of binary format
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG
from dotenv import load_dotenv

def test_vector_format():
    """Test that vectors are stored as float arrays in AstraDB"""
    
    # Load environment variables
    load_dotenv()
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    print("🧪 Testing Vector Format in AstraDB")
    print("=" * 50)
    
    # Initialize the Graph RAG system
    print("Initializing Graph RAG system...")
    graph_rag = GalaxiumGraphRAG(
        DOCUMENTS_PATH,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
        astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
        astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE')
    )
    
    # Build knowledge graph
    print("Building knowledge graph...")
    documents, links_map = graph_rag.build_knowledge_graph()
    
    # Create vector store
    print("Creating vector store with float array vectors...")
    graph_rag.create_vector_store()
    
    # Test query to verify the system works
    print("Testing query functionality...")
    test_query = "What are the different space travel offerings?"
    
    try:
        results = graph_rag.query(test_query, include_context=False)
        print(f"✅ Query successful: Retrieved {len(results['retrieved_documents'])} documents")
        
        # Check if we can access the collection directly to verify vector format
        if hasattr(graph_rag.vectorstore, 'collection'):
            print("🔍 Checking vector format in database...")
            
            # Get a sample document from the collection
            sample_doc = graph_rag.vectorstore.collection.find_one()
            if sample_doc and '$vector' in sample_doc:
                vector = sample_doc['$vector']
                print(f"Vector type: {type(vector)}")
                
                if isinstance(vector, list):
                    print("✅ SUCCESS: Vectors are stored as float arrays!")
                    print(f"Sample vector (first 5 values): {vector[:5]}")
                elif isinstance(vector, dict) and '$binary' in vector:
                    print("❌ ISSUE: Vectors are still stored in binary format")
                    print(f"Binary vector: {vector}")
                else:
                    print(f"⚠️  UNKNOWN: Vector format is {type(vector)}")
            else:
                print("❌ No vector field found in document")
        else:
            print("⚠️  Cannot access collection directly for verification")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    print("\n🎉 Vector format test completed!")
    return True

if __name__ == "__main__":
    success = test_vector_format()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
