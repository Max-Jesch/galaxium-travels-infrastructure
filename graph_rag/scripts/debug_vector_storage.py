#!/usr/bin/env python3
"""
Debug script to understand how vectors are being stored

This script will help us understand what's happening with vector storage.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG

def debug_vector_storage():
    """Debug vector storage to understand what's happening"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 Debug Vector Storage")
    print("=" * 50)
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    try:
        # Initialize the Graph RAG system
        print("Initializing Graph RAG system...")
        graph_rag = GalaxiumGraphRAG(
            DOCUMENTS_PATH,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
            astra_db_collection_name="debug_test_collection"
        )
        
        print(f"✅ Graph RAG system initialized")
        print(f"   Collection: {graph_rag.astra_db_collection_name}")
        
        # Build knowledge graph (limit to 1 document for debug)
        print("Building knowledge graph (limited to 1 document for debug)...")
        documents, links_map = graph_rag.build_knowledge_graph()
        
        # Limit to first 1 document for debug
        limited_docs = dict(list(documents.items())[:1])
        graph_rag.documents = limited_docs
        
        print(f"   Document: {list(limited_docs.keys())[0]}")
        
        # Create vector store
        print("Creating vector store...")
        graph_rag.create_vector_store()
        
        # Check what was actually stored
        print("🔍 Checking what was stored in the database...")
        
        # Use AstraDB client directly
        from astrapy import DataAPIClient
        
        client = DataAPIClient(token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'))
        db = client.get_database(api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'))
        collection = db.get_collection("debug_test_collection")
        
        # Get all documents
        docs = list(collection.find())
        print(f"   Found {len(docs)} documents in collection")
        
        if docs:
            doc = docs[0]
            print(f"   Document keys: {list(doc.keys())}")
            
            # Print the full document structure
            print("\n📄 Full document structure:")
            for key, value in doc.items():
                if key == 'metadata' and isinstance(value, dict):
                    print(f"   {key}: {list(value.keys())}")
                elif isinstance(value, (list, dict)) and len(str(value)) > 100:
                    print(f"   {key}: {type(value)} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                else:
                    print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🧪 Vector Storage Debug Tool")
    print("=" * 60)
    
    success = debug_vector_storage()
    
    if success:
        print("\n✅ Debug completed!")
    else:
        print("\n❌ Debug failed!")

if __name__ == "__main__":
    main()
