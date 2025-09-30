#!/usr/bin/env python3
"""
Test script for Galaxium Graph RAG System with AstraDB

This script demonstrates the Graph RAG system using AstraDB as the vector store,
just like in the original Jupyter notebook.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from galaxium_graph_rag import GalaxiumGraphRAG

def test_astradb_graph_rag():
    """Test the Graph RAG system with AstraDB"""
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    print("🚀 Galaxium Travels Graph RAG System with AstraDB")
    print("=" * 60)
    
    # Check if documents path exists
    if not Path(DOCUMENTS_PATH).exists():
        print(f"❌ Documents path not found: {DOCUMENTS_PATH}")
        return
    
    # Check environment variables
    print("🔑 Checking environment variables...")
    required_vars = ['OPENAI_API_KEY', 'ASTRA_DB_API_ENDPOINT', 'ASTRA_DB_APPLICATION_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set these variables in your .env file or environment")
        return
    
    print("✅ All required environment variables found")
    
    # Initialize the Graph RAG system
    print("\n📚 Initializing Graph RAG system with AstraDB...")
    try:
        graph_rag = GalaxiumGraphRAG(
            DOCUMENTS_PATH,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE')
        )
        print("✅ Graph RAG system initialized")
    except Exception as e:
        print(f"❌ Error initializing Graph RAG: {e}")
        return
    
    # Build knowledge graph
    print("\n🔗 Building knowledge graph...")
    try:
        documents, links_map = graph_rag.build_knowledge_graph()
        print(f"✅ Knowledge graph built with {len(documents)} documents")
        print(f"📊 Total relationships: {sum(len(links) for links in links_map.values())}")
    except Exception as e:
        print(f"❌ Error building knowledge graph: {e}")
        return
    
    # Create vector store (AstraDB)
    print("\n🧠 Creating AstraDB vector store...")
    try:
        graph_rag.create_vector_store()
        print("✅ AstraDB vector store created")
    except Exception as e:
        print(f"❌ Error creating AstraDB vector store: {e}")
        return
    
    # Create graph retriever
    print("\n🔍 Creating graph retriever...")
    try:
        graph_rag.create_graph_retriever()
        print("✅ Graph retriever created")
    except Exception as e:
        print(f"❌ Error creating graph retriever: {e}")
        return
    
    # Get graph statistics
    print("\n📈 Graph Statistics:")
    try:
        stats = graph_rag.visualize_graph_stats()
        print(f"   📄 Total documents: {stats['total_documents']}")
        print(f"   🔗 Total relationships: {stats['total_relationships']}")
        print(f"   📂 Documents by type: {stats['documents_by_type']}")
        print(f"   🏷️  Documents by category: {stats['documents_by_category']}")
        
        print("\n🔗 Most connected documents:")
        for i, doc in enumerate(stats['most_connected_documents'][:5], 1):
            print(f"   {i}. {doc['title']} ({doc['type']}) - {doc['connections']} connections")
            
    except Exception as e:
        print(f"❌ Error getting graph statistics: {e}")
    
    # Test queries with AstraDB
    test_queries = [
        "What space travel offerings are available?",
        "What safety training is required for lunar missions?",
        "What spacecraft are used for different missions?",
        "What are the future space destinations?",
        "What are the pricing options for space travel?"
    ]
    
    print("\n" + "=" * 80)
    print("🔍 TESTING QUERIES WITH ASTRA DB")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 60)
        
        try:
            # Query with full LLM response
            results = graph_rag.query(query, include_context=True)
            
            print(f"📊 Retrieved {len(results['retrieved_documents'])} documents")
            
            # Show document types
            doc_types = {}
            for doc in results['retrieved_documents']:
                doc_type = doc['doc_type']
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            print(f"📂 Document types: {doc_types}")
            
            # Show top documents
            print("📄 Top documents:")
            for j, doc in enumerate(results['retrieved_documents'][:3], 1):
                print(f"   {j}. {doc['title']} ({doc['doc_type']}) - Score: {doc['similarity_score']:.3f}")
            
            # Show LLM response
            if results['answer']:
                print(f"\n🤖 AI Response:")
                print(f"{results['answer'][:500]}...")  # Truncate for readability
            else:
                print("\n❌ No AI response generated")
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        print("\n" + "-" * 60)
    
    # Show document relationships
    print("\n" + "=" * 80)
    print("🔗 DOCUMENT RELATIONSHIPS")
    print("=" * 80)
    
    try:
        # Find a document with relationships
        for doc_id, doc in documents.items():
            if len(links_map.get(doc_id, [])) > 0:
                print(f"\n📄 Document: {doc.title}")
                print(f"🏷️  Type: {doc.doc_type}")
                print(f"📂 Category: {doc.metadata.get('category', 'Unknown')}")
                
                relationships = graph_rag.get_document_relationships(doc_id)
                print(f"🔗 Linked documents: {len(relationships['linked_documents'])}")
                print(f"⬅️  Incoming links: {len(relationships['incoming_links'])}")
                
                if relationships['linked_documents']:
                    print("   Connected to:")
                    for link in relationships['linked_documents'][:3]:
                        print(f"     - {link['title']} ({link['type']})")
                
                break
    except Exception as e:
        print(f"❌ Error showing relationships: {e}")
    
    print("\n✅ AstraDB Graph RAG system test completed!")
    print("\n💡 The system successfully demonstrates:")
    print("   - Document parsing and relationship detection")
    print("   - AstraDB vector store integration")
    print("   - Graph traversal for related content discovery")
    print("   - LLM integration for intelligent responses")
    print("   - Knowledge graph statistics and insights")

if __name__ == "__main__":
    test_astradb_graph_rag()
