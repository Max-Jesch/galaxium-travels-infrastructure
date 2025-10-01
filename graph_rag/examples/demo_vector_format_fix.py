#!/usr/bin/env python3
"""
Demonstration script showing the vector format fix for AstraDB
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG
from dotenv import load_dotenv

def demonstrate_vector_format_fix():
    """Demonstrate the vector format fix"""
    
    print("🔧 Vector Format Fix Demonstration")
    print("=" * 60)
    print()
    
    print("PROBLEM:")
    print("Before the fix, vectors were stored in AstraDB like this:")
    print('  "$vector": {"$binary": "PM8/ZLuBuZe8aukOvGsiK7zz1X..."}')
    print("This binary format is efficient but not human-readable.")
    print()
    
    print("SOLUTION:")
    print("After the fix, vectors are stored as float arrays:")
    print('  "$vector": [0.011600582860410213, -0.0247, 0.0156, ...]')
    print("This format is human-readable and easier to work with.")
    print()
    
    print("IMPLEMENTATION:")
    print("The fix involves:")
    print("1. Custom vector insertion method (_add_documents_with_float_vectors)")
    print("2. Direct collection access to bypass LangChain's binary encoding")
    print("3. Explicit $vector field with float array values")
    print("4. Fallback to standard method if custom insertion fails")
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Check if we have the required environment variables
    required_vars = ['OPENAI_API_KEY', 'ASTRA_DB_API_ENDPOINT', 'ASTRA_DB_APPLICATION_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("To test the fix, please set these environment variables in your .env file")
        return
    
    print("🧪 Testing the fix with a small document set...")
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    try:
        # Initialize the Graph RAG system
        graph_rag = GalaxiumGraphRAG(
            DOCUMENTS_PATH,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE')
        )
        
        # Build knowledge graph (limit to first 3 documents for demo)
        print("Building knowledge graph (limited to 3 documents for demo)...")
        documents, links_map = graph_rag.build_knowledge_graph()
        
        # Limit to first 3 documents for demo
        limited_docs = dict(list(documents.items())[:3])
        graph_rag.documents = limited_docs
        
        # Create vector store
        print("Creating vector store with float array vectors...")
        graph_rag.create_vector_store()
        
        print("✅ Vector store created successfully!")
        print()
        print("The vectors are now stored as float arrays instead of binary format.")
        print("You can verify this by checking your AstraDB collection directly.")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        print("This might be due to missing environment variables or network issues.")

if __name__ == "__main__":
    demonstrate_vector_format_fix()
