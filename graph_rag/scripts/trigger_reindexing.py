#!/usr/bin/env python3
"""
Simple script to trigger re-indexing with different collection names

This script demonstrates how to re-index your documents into different collections.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG

def quick_reindex(collection_name="galaxium_travels_documents_2"):
    """
    Quick re-indexing function for demonstration
    """
    
    # Load environment variables
    load_dotenv()
    
    print(f"🔄 Quick Re-indexing to Collection: {collection_name}")
    print("=" * 50)
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    try:
        # Initialize with the specified collection name
        graph_rag = GalaxiumGraphRAG(
            DOCUMENTS_PATH,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
            astra_db_collection_name=collection_name
        )
        
        print(f"✅ Initialized with collection: {graph_rag.astra_db_collection_name}")
        
        # Build knowledge graph (limit to 3 documents for quick test)
        print("📚 Building knowledge graph (limited to 3 documents for quick test)...")
        documents, links_map = graph_rag.build_knowledge_graph()
        
        # Limit to first 3 documents for quick test
        limited_docs = dict(list(documents.items())[:3])
        graph_rag.documents = limited_docs
        
        # Create vector store
        print(f"🧠 Creating vector store in collection: {collection_name}")
        graph_rag.create_vector_store()
        
        print(f"✅ Re-indexing completed!")
        print(f"   Collection: {collection_name}")
        print(f"   Documents indexed: {len(limited_docs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function with examples"""
    
    print("🔄 Galaxium Graph RAG - Re-indexing Examples")
    print("=" * 60)
    
    print("\n📋 Available re-indexing options:")
    print("1. Re-index to default collection (galaxium_travels_documents_2)")
    print("2. Re-index to custom collection")
    print("3. Re-index using environment variable")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        # Default collection
        success = quick_reindex("galaxium_travels_documents_2")
        
    elif choice == "2":
        # Custom collection
        custom_name = input("Enter collection name: ").strip()
        if custom_name:
            success = quick_reindex(custom_name)
        else:
            print("❌ No collection name provided")
            return
            
    elif choice == "3":
        # Environment variable
        load_dotenv()
        env_collection = os.getenv('ASTRA_DB_COLLECTION_NAME', 'galaxium_travels_documents_2')
        print(f"Using collection from environment: {env_collection}")
        success = quick_reindex(env_collection)
        
    else:
        print("❌ Invalid option")
        return
    
    if success:
        print("\n🎉 Re-indexing completed successfully!")
        print("\n💡 Tips:")
        print("   - Use 'python reindex_collection.py' for full re-indexing")
        print("   - Set ASTRA_DB_COLLECTION_NAME in .env for default collection")
        print("   - Use --force flag to skip confirmation prompts")
    else:
        print("\n❌ Re-indexing failed!")

if __name__ == "__main__":
    main()
