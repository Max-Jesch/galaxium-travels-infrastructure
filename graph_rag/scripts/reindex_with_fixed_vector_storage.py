#!/usr/bin/env python3
"""
Re-indexing script with fixed vector storage approach
This script uses the updated implementation that follows the working Langflow pattern
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from galaxium_graph_rag import GalaxiumGraphRAG

def reindex_collection():
    """Re-index all documents into a new collection with fixed vector storage"""
    
    print("🚀 Galaxium Travels Re-indexing with Fixed Vector Storage")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    # Create a new collection name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_collection_name = f"galaxium_travels_documents_v3_{timestamp}"
    
    print(f"📁 Documents path: {DOCUMENTS_PATH}")
    print(f"🗄️  New collection: {new_collection_name}")
    
    # Check environment variables
    required_env_vars = [
        'OPENAI_API_KEY',
        'ASTRA_DB_API_ENDPOINT', 
        'ASTRA_DB_APPLICATION_TOKEN',
        'ASTRA_DB_KEYSPACE'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these variables before running the script.")
        return False
    
    print("✅ All required environment variables are set")
    
    try:
        # Initialize the Graph RAG system with new collection
        print("\n🔧 Initializing Graph RAG system...")
        graph_rag = GalaxiumGraphRAG(
            DOCUMENTS_PATH,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
            astra_db_collection_name=new_collection_name
        )
        
        # Step 1: Build knowledge graph
        print("\n📚 Building knowledge graph...")
        start_time = time.time()
        documents, links_map = graph_rag.build_knowledge_graph()
        build_time = time.time() - start_time
        
        print(f"✅ Knowledge graph built in {build_time:.2f} seconds")
        print(f"   - Documents: {len(documents)}")
        print(f"   - Relationships: {sum(len(links) for links in links_map.values())}")
        
        # Step 2: Create vector store with fixed approach
        print("\n🔍 Creating vector store with fixed vector storage...")
        start_time = time.time()
        graph_rag.create_vector_store()
        vector_time = time.time() - start_time
        
        print(f"✅ Vector store created in {vector_time:.2f} seconds")
        
        # Step 3: Inspect vector storage format
        print("\n🔬 Inspecting vector storage format...")
        print("-" * 40)
        stored_docs = graph_rag.inspect_vector_storage(limit=5)
        
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
                    elif isinstance(vector, dict) and '$binary' in vector:
                        vector_formats.append("Binary")
                    else:
                        vector_formats.append(f"{type(vector).__name__}")
            
            print(f"📊 Vector storage analysis:")
            print(f"   - Documents with vectors: {sum(1 for doc in stored_docs if '$vector' in doc)}")
            print(f"   - Vector formats found: {set(vector_formats)}")
            
            if has_vector_fields:
                print("   - ✅ Vector fields are present in documents")
            else:
                print("   - ℹ️  Vectors stored internally by LangChain/AstraDB")
        else:
            print("❌ Failed to inspect vector storage")
            return False
        
        # Step 4: Create graph retriever
        print("\n🕸️  Creating graph retriever...")
        start_time = time.time()
        graph_rag.create_graph_retriever()
        retriever_time = time.time() - start_time
        
        print(f"✅ Graph retriever created in {retriever_time:.2f} seconds")
        
        # Step 5: Test the system
        print("\n🧪 Testing the re-indexed system...")
        test_queries = [
            "What are the different space travel offerings?",
            "What safety certifications are required?",
            "What spacecraft are available?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Test {i}: {query}")
            try:
                start_time = time.time()
                results = graph_rag.query(query)
                query_time = time.time() - start_time
                
                print(f"   ✅ Query successful ({query_time:.2f}s)")
                print(f"   📄 Retrieved: {len(results['retrieved_documents'])} documents")
                print(f"   📝 Answer: {results['answer'][:100]}...")
                
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
        
        # Step 6: Get final statistics
        print("\n📈 Final Statistics:")
        stats = graph_rag.visualize_graph_stats()
        print(f"   - Total documents: {stats['total_documents']}")
        print(f"   - Total relationships: {stats['total_relationships']}")
        print(f"   - Documents by type: {stats['documents_by_type']}")
        print(f"   - Documents by category: {stats['documents_by_category']}")
        
        # Step 7: Summary
        total_time = build_time + vector_time + retriever_time
        print(f"\n🎉 Re-indexing completed successfully!")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"🗄️  Collection: {new_collection_name}")
        print(f"📊 Documents indexed: {len(documents)}")
        
        # Update environment variable for future use
        print(f"\n💡 To use this collection, set:")
        print(f"   export ASTRA_DB_COLLECTION_NAME={new_collection_name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Re-indexing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = reindex_collection()
    
    if success:
        print("\n✅ Re-indexing completed successfully!")
        print("🎯 The new collection uses the fixed vector storage approach")
    else:
        print("\n❌ Re-indexing failed!")
        print("🔧 Please check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()

