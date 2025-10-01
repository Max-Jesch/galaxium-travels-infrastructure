#!/usr/bin/env python3
"""
Quick re-indexing script - just re-index the documents with fixed vector storage
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG

def quick_reindex():
    """Quick re-indexing with minimal output"""
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    # Create new collection name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_collection_name = f"galaxium_travels_documents_v3_{timestamp}"
    
    print(f"🚀 Quick Re-indexing to: {new_collection_name}")
    
    try:
        # Initialize and build
        graph_rag = GalaxiumGraphRAG(
            DOCUMENTS_PATH,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
            astra_db_collection_name=new_collection_name
        )
        
        print("📚 Building knowledge graph...")
        documents, links_map = graph_rag.build_knowledge_graph()
        print(f"✅ Built graph with {len(documents)} documents")
        
        print("🔍 Creating vector store...")
        graph_rag.create_vector_store()
        print("✅ Vector store created")
        
        print("🕸️  Creating graph retriever...")
        graph_rag.create_graph_retriever()
        print("✅ Graph retriever created")
        
        print(f"\n🎉 Re-indexing completed!")
        print(f"🗄️  Collection: {new_collection_name}")
        print(f"📊 Documents: {len(documents)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Re-indexing failed: {e}")
        return False

if __name__ == "__main__":
    success = quick_reindex()
    if not success:
        sys.exit(1)

