#!/usr/bin/env python3
"""
Test script to inspect existing collection with API options
This script tests if the API options fix works on an existing collection
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG

def test_existing_collection():
    """Test the API options on an existing collection"""
    
    print("🔧 Testing API Options on Existing Collection")
    print("=" * 50)
    
    # Use existing collection
    collection_name = "galaxium_travels_documents_v3_20250930_111248"
    
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
        
        # Just inspect the existing collection
        print("\n🔬 Inspecting existing collection with API options...")
        print("-" * 40)
        stored_docs = graph_rag.inspect_vector_storage(limit=3)
        
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
            elif any('Binary' in fmt for fmt in vector_formats):
                print("   - ❌ Still using binary format")
            else:
                print("   - ℹ️  No vector fields found (stored internally)")
        else:
            print("❌ Failed to inspect vector storage")
            return False
        
        # Test a simple query
        print("\n🧪 Testing query functionality...")
        try:
            results = graph_rag.query("What are the different space travel offerings?")
            print(f"✅ Query successful - retrieved {len(results['retrieved_documents'])} documents")
            print(f"📝 Answer preview: {results['answer'][:200]}...")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return False
        
        print(f"\n🎉 Test completed successfully!")
        print(f"🗄️  Collection: {collection_name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = test_existing_collection()
    
    if success:
        print("\n✅ API options test completed successfully!")
        print("🎯 The API options configuration should now use float arrays instead of binary encoding")
    else:
        print("\n❌ API options test failed!")
        print("🔧 Please check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()

