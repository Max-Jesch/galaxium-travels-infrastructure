#!/usr/bin/env python3
"""
Test script to create a minimal collection with API options
This script creates a small collection to test the API options fix
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG

def test_minimal_collection():
    """Test the API options with a minimal collection"""
    
    print("🔧 Testing API Options with Minimal Collection")
    print("=" * 50)
    
    # Create a minimal collection name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    collection_name = f"test_fix_{timestamp}"
    
    print(f"🗄️  Collection: {collection_name}")
    
    try:
        # Initialize the Graph RAG system
        print("\n🔧 Initializing Graph RAG system with API options...")
        graph_rag = GalaxiumGraphRAG(
            documents_path="/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files",
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
            astra_db_collection_name=collection_name
        )
        
        # Create a minimal knowledge graph with just 2 documents
        print("\n📚 Building minimal knowledge graph...")
        documents, links_map = graph_rag.build_knowledge_graph()
        
        # Take only the first 2 documents to avoid index limits
        limited_docs = dict(list(documents.items())[:2])
        graph_rag.documents = limited_docs
        print(f"✅ Limited to {len(limited_docs)} documents")
        
        # Create vector store with API options
        print("\n🔍 Creating vector store with API options...")
        graph_rag.create_vector_store()
        print("✅ Vector store created with API options")
        
        # Inspect vector storage format
        print("\n🔬 Inspecting vector storage format...")
        print("-" * 40)
        stored_docs = graph_rag.inspect_vector_storage(limit=2)
        
        if stored_docs:
            print("✅ Vector storage inspection completed")
            
            # Analyze the results
            has_vector_fields = any('$vector' in doc for doc in stored_docs)
            vector_formats = []
            
            for doc in stored_docs:
                if '$vector' in doc:
                    vector = doc['$vector']
                    if isinstance(vector, list):
                        vector_formats.append(f"Array({len(vector)} dims)")
                        print(f"🎯 SUCCESS: Found float array vector with {len(vector)} dimensions!")
                        print(f"   Sample values: {vector[:5]}")
                    elif isinstance(vector, dict) and '$binary' in vector:
                        vector_formats.append("Binary")
                        print(f"❌ Still binary format: {vector['$binary'][:50]}...")
                    else:
                        vector_formats.append(f"{type(vector).__name__}")
                        print(f"⚠️  Unexpected format: {type(vector)}")
                else:
                    print("ℹ️  No $vector field found in document")
            
            print(f"\n📊 Vector storage analysis:")
            print(f"   - Documents with vectors: {sum(1 for doc in stored_docs if '$vector' in doc)}")
            print(f"   - Vector formats found: {set(vector_formats)}")
            
            if any('Array' in fmt for fmt in vector_formats):
                print("   - ✅ SUCCESS: Float arrays found!")
                return True
            elif any('Binary' in fmt for fmt in vector_formats):
                print("   - ❌ Still using binary format")
                return False
            else:
                print("   - ℹ️  No vector fields found (stored internally)")
                return False
        else:
            print("❌ Failed to inspect vector storage")
            return False
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = test_minimal_collection()
    
    if success:
        print("\n✅ API options test completed successfully!")
        print("🎯 The API options configuration works - vectors are stored as float arrays!")
    else:
        print("\n❌ API options test failed!")
        print("🔧 Please check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()

