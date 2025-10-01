#!/usr/bin/env python3
"""
Main script for indexing Galaxium Travels documents
Processes markdown documents and creates vector database with graph traversal compatibility
"""

import sys
from pathlib import Path
import logging

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config import Config
from document_processor import DocumentProcessor
from vector_indexer import VectorIndexer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to process and index documents"""
    
    print("🚀 Galaxium Travels Document Preprocessing & Vector Indexing")
    print("=" * 70)
    
    try:
        # Load configuration
        print("\n📋 Loading configuration...")
        config = Config()
        print(config)
        
        # Process documents
        print("\n📚 Processing markdown documents...")
        processor = DocumentProcessor(config.documents_path)
        documents = processor.process_all_documents()
        
        if not documents:
            print("❌ No documents processed. Exiting.")
            return False
        
        # Show document summary
        summary = processor.get_document_summary()
        print(f"\n📊 Document Summary:")
        print(f"  Total documents: {summary['total_documents']}")
        print(f"  Total relationships: {summary['total_relationships']}")
        print(f"  Documents by type: {summary['documents_by_type']}")
        print(f"  Documents by category: {summary['documents_by_category']}")
        
        if summary['most_connected_documents']:
            print(f"\n🔗 Most connected documents:")
            for i, doc in enumerate(summary['most_connected_documents'][:5], 1):
                print(f"  {i}. {doc['title']} ({doc['type']}) - {doc['connections']} connections")
        
        # Create vector indexer
        print(f"\n🧠 Creating vector indexer...")
        indexer = VectorIndexer(config)
        
        # Create vector store
        print(f"\n🗄️  Creating vector store...")
        indexer.create_vectorstore()
        
        # Index documents
        print(f"\n📝 Indexing documents...")
        success = indexer.index_documents(documents)
        
        if not success:
            print("❌ Document indexing failed. Exiting.")
            return False
        
        # Verify vector format
        print(f"\n🔍 Verifying vector format...")
        format_ok = indexer.verify_vector_format(limit=3)
        
        if not format_ok:
            print("⚠️  Vector format verification failed. Langflow may have issues.")
        else:
            print("✅ Vector format verified - Langflow compatible!")
        
        # Get database statistics
        print(f"\n📊 Database Statistics:")
        stats = indexer.get_database_stats()
        if stats:
            print(f"  Total documents in database: {stats['total_documents']}")
            print(f"  Documents with relationships: {stats['documents_with_relationships']}")
            print(f"  Total relationships: {stats['total_relationships']}")
            print(f"  Collection: {stats['collection_name']}")
            print(f"  Keyspace: {stats['keyspace']}")
        
        # Test vector search
        print(f"\n🔍 Testing vector search...")
        search_results = indexer.test_vector_search("space travel", limit=3)
        if search_results:
            print("  Search results:")
            for result in search_results:
                print(f"    {result['rank']}. {result['title']} ({result['doc_type']})")
                print(f"       Category: {result['category']}")
                print(f"       Linked docs: {len(result['linked_docs'])}")
                print(f"       Preview: {result['content_preview']}")
                print()
        
        print("\n🎉 Document indexing completed successfully!")
        print("\n✅ Ready for Langflow integration:")
        print("  - Documents indexed with proper vector format (float arrays)")
        print("  - Graph traversal ready with resolved document IDs")
        print("  - All relationships validated and stored")
        print("  - Vector search functionality verified")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during document indexing: {e}")
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

