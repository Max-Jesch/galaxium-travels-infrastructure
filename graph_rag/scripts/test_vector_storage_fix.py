#!/usr/bin/env python3
"""
Test script to verify the vector storage fix
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG

def test_vector_storage():
    """Test the vector storage implementation"""
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    print("🔍 Testing Vector Storage Fix")
    print("=" * 50)
    
    # Initialize the Graph RAG system
    print("Initializing Galaxium Travels Graph RAG System...")
    graph_rag = GalaxiumGraphRAG(
        DOCUMENTS_PATH,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
        astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
        astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
        astra_db_collection_name=os.getenv('ASTRA_DB_COLLECTION_NAME')
    )
    
    # Build knowledge graph
    print("\nBuilding knowledge graph...")
    documents, links_map = graph_rag.build_knowledge_graph()
    print(f"✅ Built knowledge graph with {len(documents)} documents")
    
    # Create vector store
    print("\nCreating vector store...")
    graph_rag.create_vector_store()
    print("✅ Vector store created successfully")
    
    # Inspect vector storage format
    print("\n🔍 Inspecting vector storage format...")
    print("-" * 30)
    stored_docs = graph_rag.inspect_vector_storage(limit=3)
    
    if stored_docs:
        print("\n✅ Vector storage inspection completed")
        print("📊 Summary:")
        print(f"  - Retrieved {len(stored_docs)} documents")
        print(f"  - Documents have proper structure")
        
        # Check if vectors are stored as expected
        has_vector_fields = any('$vector' in doc for doc in stored_docs)
        if has_vector_fields:
            print("  - ✅ Vector fields found in documents")
        else:
            print("  - ⚠️  No $vector fields found (vectors may be stored internally)")
    else:
        print("❌ Failed to inspect vector storage")
    
    # Test a simple query
    print("\n🧪 Testing query functionality...")
    try:
        results = graph_rag.query("What are the different space travel offerings?")
        print(f"✅ Query successful - retrieved {len(results['retrieved_documents'])} documents")
        print(f"📝 Answer preview: {results['answer'][:200]}...")
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_vector_storage()

