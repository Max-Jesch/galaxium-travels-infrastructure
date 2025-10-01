#!/usr/bin/env python3
"""
ACTUAL test of the API options fix
This script will create a simple document and verify the vector format
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_api_options_actually():
    """Actually test the API options by creating a simple document"""
    
    print("🔧 ACTUALLY Testing API Options Fix")
    print("=" * 50)
    
    try:
        from astrapy import DataAPIClient
        from astrapy.api_options import APIOptions, SerdesOptions
        from langchain_astradb import AstraDBVectorStore
        from langchain_openai import OpenAIEmbeddings
        from langchain_core.documents import Document
        
        # Create a unique collection name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        collection_name = f"test_api_fix_{timestamp}"
        
        print(f"🗄️  Collection: {collection_name}")
        
        # Configure API options
        api_options = APIOptions(
            serdes_options=SerdesOptions(
                binary_encode_vectors=False,
                custom_datatypes_in_reading=False
            )
        )
        
        print("✅ API options configured")
        
        # Create embeddings
        embeddings = OpenAIEmbeddings()
        
        # Create a simple document
        test_doc = Document(
            page_content="This is a test document for vector storage with API options.",
            metadata={"test": True, "timestamp": timestamp}
        )
        
        print("✅ Test document created")
        
        # Create vector store with API options
        vector_store = AstraDBVectorStore(
            embedding=embeddings,
            collection_name=collection_name,
            api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            namespace=os.getenv('ASTRA_DB_KEYSPACE'),
            api_options=api_options,
            pre_delete_collection=True
        )
        
        print("✅ Vector store created with API options")
        
        # Add the document
        vector_store.add_documents([test_doc])
        print("✅ Document added to vector store")
        
        # Now inspect the collection directly
        client = DataAPIClient(
            token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            api_options=api_options
        )
        database = client.get_database(
            api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            keyspace=os.getenv('ASTRA_DB_KEYSPACE')
        )
        collection = database.get_collection(collection_name)
        
        print("\n🔬 Inspecting the actual stored document...")
        print("-" * 40)
        
        # Get the document
        docs = list(collection.find({}, limit=1))
        if docs:
            doc = docs[0]
            print(f"Document ID: {doc.get('_id', 'N/A')}")
            print(f"Content: {doc.get('content', '')[:100]}...")
            
            # Check for vector field
            if '$vector' in doc:
                vector = doc['$vector']
                if isinstance(vector, list):
                    print(f"🎯 SUCCESS: Vector is a float array with {len(vector)} dimensions!")
                    print(f"Sample values: {vector[:5]}")
                    print("✅ The API options fix is working!")
                    return True
                elif isinstance(vector, dict) and '$binary' in vector:
                    print(f"❌ FAILED: Vector is still binary format")
                    print(f"Binary data: {vector['$binary'][:50]}...")
                    return False
                else:
                    print(f"⚠️  Unexpected vector format: {type(vector)}")
                    return False
            else:
                print("ℹ️  No $vector field found - vectors may be stored internally")
                return False
        else:
            print("❌ No documents found in collection")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = test_api_options_actually()
    
    if success:
        print("\n🎉 SUCCESS: The API options fix actually works!")
        print("🎯 Vectors are stored as float arrays, not binary!")
    else:
        print("\n❌ FAILED: The API options fix did not work")
        print("🔧 Vectors are still being stored in binary format")
        sys.exit(1)

if __name__ == "__main__":
    main()

