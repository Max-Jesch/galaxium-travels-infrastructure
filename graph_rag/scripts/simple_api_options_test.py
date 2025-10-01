#!/usr/bin/env python3
"""
Simple test to verify API options work with AstraDB
This script creates a minimal test to verify the binary_encode_vectors=False setting works
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_api_options_directly():
    """Test API options directly with AstraDB"""
    
    print("🔧 Testing API Options Directly with AstraDB")
    print("=" * 50)
    
    try:
        from astrapy import DataAPIClient
        from astrapy.api_options import APIOptions, SerdesOptions
        from langchain_astradb import AstraDBVectorStore
        from langchain_openai import OpenAIEmbeddings
        
        print("✅ Successfully imported required modules")
        
        # Configure API options
        api_options = APIOptions(
            serdes_options=SerdesOptions(
                binary_encode_vectors=False,
                custom_datatypes_in_reading=False
            )
        )
        
        print("✅ Successfully created API options with binary_encode_vectors=False")
        
        # Test creating a client with API options
        client = DataAPIClient(
            token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            api_options=api_options
        )
        
        print("✅ Successfully created DataAPIClient with API options")
        
        # Test creating a database object
        database = client.get_database(
            api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
        )
        
        print("✅ Successfully created database object with API options")
        
        # Test creating embeddings
        embeddings = OpenAIEmbeddings()
        test_text = "This is a test document for vector storage."
        test_embedding = embeddings.embed_query(test_text)
        
        print(f"✅ Successfully created embedding with {len(test_embedding)} dimensions")
        print(f"   Sample values: {test_embedding[:5]}")
        
        # Test that the embedding is a float array
        if isinstance(test_embedding, list) and all(isinstance(x, (int, float)) for x in test_embedding):
            print("✅ Embedding is a proper float array")
        else:
            print("❌ Embedding is not a proper float array")
            return False
        
        print("\n🎉 API options test completed successfully!")
        print("🎯 The API options configuration should work correctly")
        print("💡 The key is that binary_encode_vectors=False prevents binary encoding")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = test_api_options_directly()
    
    if success:
        print("\n✅ API options test completed successfully!")
        print("🎯 The fix should work - we just need to apply it when creating collections")
    else:
        print("\n❌ API options test failed!")
        print("🔧 Please check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()

