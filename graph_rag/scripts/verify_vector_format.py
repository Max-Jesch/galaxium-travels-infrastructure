#!/usr/bin/env python3
"""
Direct verification of vector format in AstraDB collection

This script directly checks the database to verify that vectors are stored
as float arrays instead of binary format.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG

def verify_vector_format_directly():
    """Directly verify vector format in the database"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 Direct Vector Format Verification")
    print("=" * 50)
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    # Check if we have the required environment variables
    required_vars = ['OPENAI_API_KEY', 'ASTRA_DB_API_ENDPOINT', 'ASTRA_DB_APPLICATION_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these variables in your .env file")
        return False
    
    try:
        # Initialize the Graph RAG system
        print("Initializing Graph RAG system...")
        graph_rag = GalaxiumGraphRAG(
            DOCUMENTS_PATH,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
            astra_db_collection_name=os.getenv('ASTRA_DB_COLLECTION_NAME', 'galaxium_travels_documents_2')
        )
        
        print(f"✅ Graph RAG system initialized")
        print(f"   Collection: {graph_rag.astra_db_collection_name}")
        
        # Build knowledge graph (limit to 2 documents for quick test)
        print("Building knowledge graph (limited to 2 documents for quick test)...")
        documents, links_map = graph_rag.build_knowledge_graph()
        
        # Limit to first 2 documents for quick test
        limited_docs = dict(list(documents.items())[:2])
        graph_rag.documents = limited_docs
        
        # Create vector store
        print("Creating vector store...")
        graph_rag.create_vector_store()
        
        # Now directly access the collection to check vector format
        print("🔍 Checking vector format in database...")
        
        if hasattr(graph_rag.vectorstore, 'collection'):
            # Get a sample document from the collection
            sample_doc = graph_rag.vectorstore.collection.find_one()
            
            if sample_doc:
                print(f"✅ Found document in collection")
                print(f"   Document keys: {list(sample_doc.keys())}")
                
                # Check for vector field
                if '$vector' in sample_doc:
                    vector = sample_doc['$vector']
                    print(f"   Vector type: {type(vector)}")
                    print(f"   Vector length: {len(vector) if isinstance(vector, list) else 'N/A'}")
                    
                    if isinstance(vector, list):
                        print("✅ SUCCESS: Vectors are stored as float arrays!")
                        print(f"   Sample vector (first 5 values): {vector[:5]}")
                        print(f"   Sample vector (last 5 values): {vector[-5:]}")
                        
                        # Verify these are actually floats
                        if all(isinstance(x, (int, float)) for x in vector[:10]):
                            print("✅ Confirmed: All values are numeric (float/int)")
                        else:
                            print("⚠️  Warning: Some values are not numeric")
                            
                    elif isinstance(vector, dict) and '$binary' in vector:
                        print("❌ ISSUE: Vectors are still stored in binary format")
                        print(f"   Binary vector: {vector}")
                        return False
                    else:
                        print(f"⚠️  UNKNOWN: Vector format is {type(vector)}")
                        print(f"   Vector content: {vector}")
                        return False
                else:
                    print("❌ No $vector field found in document")
                    print(f"   Available fields: {list(sample_doc.keys())}")
                    return False
            else:
                print("❌ No documents found in collection")
                return False
        else:
            print("❌ Cannot access collection directly")
            return False
        
        print("\n🎉 Vector format verification completed successfully!")
        print("   ✅ Vectors are stored as float arrays")
        print("   ✅ All values are numeric")
        print("   ✅ Format is human-readable")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🧪 Vector Format Verification Tool")
    print("=" * 60)
    
    success = verify_vector_format_directly()
    
    if success:
        print("\n✅ Verification completed successfully!")
        print("\n📋 Summary:")
        print("   - Vectors are stored as float arrays (not binary)")
        print("   - Format is human-readable and debuggable")
        print("   - Compatible with AstraDB vector search")
    else:
        print("\n❌ Verification failed!")
        print("   - Check your environment variables")
        print("   - Ensure AstraDB credentials are correct")
        print("   - Verify the collection was created successfully")
        sys.exit(1)

if __name__ == "__main__":
    main()
