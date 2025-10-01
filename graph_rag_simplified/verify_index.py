#!/usr/bin/env python3
"""
Verification script for Galaxium Travels document index
Checks database contents, vector format, and graph traversal compatibility
"""

import sys
from pathlib import Path
import logging

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config import Config
from vector_indexer import VectorIndexer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_database_connection():
    """Verify database connection and basic access"""
    print("🔌 Verifying database connection...")
    
    try:
        config = Config()
        indexer = VectorIndexer(config)
        
        # Test basic connection
        stats = indexer.get_database_stats()
        if stats and stats.get('total_documents', 0) > 0:
            print(f"✅ Database connection successful")
            print(f"   Collection: {stats['collection_name']}")
            print(f"   Keyspace: {stats['keyspace']}")
            print(f"   Total documents: {stats['total_documents']}")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def verify_vector_format():
    """Verify that vectors are stored as float arrays"""
    print("\n🧮 Verifying vector format...")
    
    try:
        config = Config()
        indexer = VectorIndexer(config)
        
        format_ok = indexer.verify_vector_format(limit=5)
        
        if format_ok:
            print("✅ Vector format verified - Langflow compatible!")
            return True
        else:
            print("❌ Vector format verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Vector format verification error: {e}")
        return False

def verify_graph_traversal():
    """Verify graph traversal compatibility"""
    print("\n🔗 Verifying graph traversal compatibility...")
    
    try:
        config = Config()
        indexer = VectorIndexer(config)
        
        # Get sample documents with relationships
        sample_docs = list(indexer.collection.find({}, limit=10))
        
        docs_with_links = 0
        total_relationships = 0
        valid_relationships = 0
        
        for doc in sample_docs:
            metadata = doc.get('metadata', {})
            linked_docs = metadata.get('linked_docs', [])
            
            if linked_docs:
                docs_with_links += 1
                total_relationships += len(linked_docs)
                
                # Check if linked document IDs are valid (not file paths)
                for link in linked_docs:
                    if not link.startswith('/') and not link.endswith('.md'):
                        valid_relationships += 1
        
        print(f"   Documents with relationships: {docs_with_links}")
        print(f"   Total relationships: {total_relationships}")
        print(f"   Valid document ID relationships: {valid_relationships}")
        
        if valid_relationships > 0:
            print("✅ Graph traversal compatibility verified!")
            return True
        else:
            print("❌ No valid document ID relationships found")
            return False
            
    except Exception as e:
        print(f"❌ Graph traversal verification error: {e}")
        return False

def verify_vector_search():
    """Verify vector search functionality"""
    print("\n🔍 Verifying vector search functionality...")
    
    try:
        config = Config()
        indexer = VectorIndexer(config)
        
        # Create vector store for testing (without deleting existing data)
        from langchain_astradb import AstraDBVectorStore
        from astrapy.api_options import APIOptions, SerdesOptions
        
        # Configure AstraPy to use plain float arrays instead of binary encoding
        api_options = APIOptions(
            serdes_options=SerdesOptions(
                binary_encode_vectors=False,
                custom_datatypes_in_reading=False
            )
        )
        
        indexer.vectorstore = AstraDBVectorStore(
            embedding=indexer.embeddings,
            collection_name=config.astra_db_collection_name,
            api_endpoint=config.astra_db_api_endpoint,
            token=config.astra_db_application_token,
            namespace=config.astra_db_keyspace,
            pre_delete_collection=False,  # Don't delete existing data
            api_options=api_options,
        )
        
        # Test multiple queries
        test_queries = [
            "space travel",
            "lunar mission",
            "safety training",
            "spacecraft specifications"
        ]
        
        all_working = True
        
        for query in test_queries:
            results = indexer.test_vector_search(query, limit=2)
            if results:
                print(f"   ✅ Query '{query}': {len(results)} results")
            else:
                print(f"   ❌ Query '{query}': No results")
                all_working = False
        
        if all_working:
            print("✅ Vector search functionality verified!")
            return True
        else:
            print("❌ Vector search functionality issues detected")
            return False
            
    except Exception as e:
        print(f"❌ Vector search verification error: {e}")
        return False

def show_database_summary():
    """Show comprehensive database summary"""
    print("\n📊 Database Summary:")
    
    try:
        config = Config()
        indexer = VectorIndexer(config)
        
        stats = indexer.get_database_stats()
        if stats:
            print(f"   Total documents: {stats['total_documents']}")
            print(f"   Documents with relationships: {stats['documents_with_relationships']}")
            print(f"   Total relationships: {stats['total_relationships']}")
            print(f"   Collection: {stats['collection_name']}")
            print(f"   Keyspace: {stats['keyspace']}")
            
            # Show sample documents
            print(f"\n📄 Sample Documents:")
            sample_docs = list(indexer.collection.find({}, limit=5))
            for i, doc in enumerate(sample_docs, 1):
                metadata = doc.get('metadata', {})
                print(f"   {i}. {metadata.get('title', 'Unknown')}")
                print(f"      Type: {metadata.get('doc_type', 'Unknown')}")
                print(f"      Category: {metadata.get('category', 'Unknown')}")
                print(f"      Linked docs: {len(metadata.get('linked_docs', []))}")
                print()
        
    except Exception as e:
        print(f"❌ Error getting database summary: {e}")

def main():
    """Main verification function"""
    
    print("🔍 Galaxium Travels Document Index Verification")
    print("=" * 60)
    
    # Run all verification checks
    checks = [
        ("Database Connection", verify_database_connection),
        ("Vector Format", verify_vector_format),
        ("Graph Traversal", verify_graph_traversal),
        ("Vector Search", verify_vector_search)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results[check_name] = False
    
    # Show summary
    print("\n" + "=" * 60)
    print("📋 Verification Summary:")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check_name}: {status}")
        if not passed:
            all_passed = False
    
    # Show database summary
    show_database_summary()
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All verification checks passed!")
        print("✅ Database is ready for Langflow integration")
    else:
        print("⚠️  Some verification checks failed")
        print("❌ Database may have issues with Langflow integration")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
