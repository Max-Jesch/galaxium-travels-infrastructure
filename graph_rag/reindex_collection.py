#!/usr/bin/env python3
"""
Re-indexing script for Galaxium Graph RAG System

This script triggers a complete re-indexing of all documents into a new collection.
Use this when you want to:
- Create a new collection with a different name
- Re-index all documents with updated vector format
- Migrate to a new collection version
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG

def reindex_collection(collection_name=None, force_reindex=False):
    """
    Re-index all documents into a new collection
    
    Args:
        collection_name (str): Name of the collection to create. If None, uses environment variable or default.
        force_reindex (bool): If True, will delete existing collection and re-index everything.
    """
    
    # Load environment variables
    load_dotenv()
    
    print("🔄 Galaxium Graph RAG - Collection Re-indexing")
    print("=" * 60)
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    # Determine collection name
    if collection_name:
        target_collection = collection_name
        print(f"📊 Using specified collection: {target_collection}")
    else:
        target_collection = os.getenv('ASTRA_DB_COLLECTION_NAME', 'galaxium_travels_documents_2')
        print(f"📊 Using collection from environment: {target_collection}")
    
    # Check if we have the required environment variables
    required_vars = ['OPENAI_API_KEY', 'ASTRA_DB_API_ENDPOINT', 'ASTRA_DB_APPLICATION_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these variables in your .env file")
        return False
    
    try:
        # Initialize the Graph RAG system with the target collection
        print(f"\n🚀 Initializing Graph RAG system...")
        print(f"   Target collection: {target_collection}")
        
        graph_rag = GalaxiumGraphRAG(
            DOCUMENTS_PATH,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
            astra_db_collection_name=target_collection
        )
        
        print("✅ Graph RAG system initialized")
        
        # Build knowledge graph
        print(f"\n📚 Building knowledge graph...")
        documents, links_map = graph_rag.build_knowledge_graph()
        
        print(f"✅ Knowledge graph built successfully")
        print(f"   Documents parsed: {len(documents)}")
        print(f"   Total relationships: {sum(len(links) for links in links_map.values())}")
        
        # Create vector store (this will create the new collection)
        print(f"\n🧠 Creating vector store in collection: {target_collection}")
        print("   This will:")
        print("   - Create a new collection (if it doesn't exist)")
        print("   - Delete existing data in the collection")
        print("   - Re-index all documents with float array vectors")
        
        if not force_reindex:
            response = input("\n⚠️  This will delete existing data in the collection. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Re-indexing cancelled")
                return False
        
        graph_rag.create_vector_store()
        
        print(f"✅ Vector store created successfully in collection: {target_collection}")
        
        # Test the new collection with a sample query
        print(f"\n🧪 Testing the new collection...")
        test_query = "What are the different space travel offerings?"
        
        try:
            results = graph_rag.query(test_query, include_context=False)
            print(f"✅ Test query successful!")
            print(f"   Retrieved {len(results['retrieved_documents'])} documents")
            print(f"   Document types found: {list(results['related_documents'].keys())}")
        except Exception as e:
            print(f"⚠️  Test query failed: {e}")
            print("   The collection was created but there might be an issue with retrieval")
        
        print(f"\n🎉 Re-indexing completed successfully!")
        print(f"   Collection: {target_collection}")
        print(f"   Documents indexed: {len(documents)}")
        print(f"   Vectors stored as: Float arrays (not binary)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during re-indexing: {e}")
        return False

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Re-index Galaxium Graph RAG collection')
    parser.add_argument('--collection', '-c', type=str, 
                       help='Collection name to create (overrides environment variable)')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Skip confirmation prompt and force re-indexing')
    
    args = parser.parse_args()
    
    success = reindex_collection(
        collection_name=args.collection,
        force_reindex=args.force
    )
    
    if success:
        print("\n✅ Re-indexing completed successfully!")
    else:
        print("\n❌ Re-indexing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
