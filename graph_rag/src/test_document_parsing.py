#!/usr/bin/env python3
"""
Test script for document parsing and graph building without OpenAI API

This script demonstrates the document parsing and graph building capabilities
without requiring the OpenAI API key.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from galaxium_graph_rag import GalaxiumDocumentParser

def test_document_parsing():
    """Test document parsing and graph building without OpenAI API"""
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    print("🚀 Galaxium Travels Document Parsing Test")
    print("=" * 50)
    
    # Check if documents path exists
    if not Path(DOCUMENTS_PATH).exists():
        print(f"❌ Documents path not found: {DOCUMENTS_PATH}")
        return
    
    # Initialize the document parser
    print("📚 Initializing document parser...")
    try:
        parser = GalaxiumDocumentParser(DOCUMENTS_PATH)
        print("✅ Document parser initialized")
    except Exception as e:
        print(f"❌ Error initializing parser: {e}")
        return
    
    # Parse all documents
    print("\n🔍 Parsing documents...")
    try:
        documents = parser.parse_all_documents()
        print(f"✅ Parsed {len(documents)} documents")
    except Exception as e:
        print(f"❌ Error parsing documents: {e}")
        return
    
    # Build links map
    print("\n🔗 Building document relationships...")
    try:
        links_map = parser.build_links_map()
        total_links = sum(len(links) for links in links_map.values())
        print(f"✅ Built {total_links} document relationships")
    except Exception as e:
        print(f"❌ Error building links map: {e}")
        return
    
    # Show document statistics
    print("\n📊 Document Statistics:")
    
    # Count by type
    doc_types = {}
    doc_categories = {}
    
    for doc_id, doc in documents.items():
        doc_type = doc.doc_type
        category = doc.metadata.get('category', 'Unknown')
        
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        doc_categories[category] = doc_categories.get(category, 0) + 1
    
    print(f"   📄 Total documents: {len(documents)}")
    print(f"   🔗 Total relationships: {total_links}")
    print(f"   📂 Document types: {doc_types}")
    print(f"   🏷️  Document categories: {doc_categories}")
    
    # Show most connected documents
    print("\n🔗 Most connected documents:")
    connection_counts = [(doc_id, len(links)) for doc_id, links in links_map.items()]
    connection_counts.sort(key=lambda x: x[1], reverse=True)
    
    for i, (doc_id, count) in enumerate(connection_counts[:10], 1):
        if doc_id in documents:
            doc = documents[doc_id]
            print(f"   {i}. {doc.title} ({doc.doc_type}) - {count} connections")
    
    # Show sample documents
    print("\n📄 Sample Documents:")
    sample_count = 0
    for doc_id, doc in documents.items():
        if sample_count >= 5:
            break
        print(f"\n   Document: {doc.title}")
        print(f"   Type: {doc.doc_type}")
        print(f"   Category: {doc.metadata.get('category', 'Unknown')}")
        print(f"   Links: {len(doc.linked_docs)}")
        print(f"   Content preview: {doc.content[:200]}...")
        sample_count += 1
    
    # Show relationship examples
    print("\n🔗 Relationship Examples:")
    relationship_count = 0
    for doc_id, doc in documents.items():
        if len(links_map.get(doc_id, [])) > 0 and relationship_count < 3:
            print(f"\n   Document: {doc.title}")
            print(f"   Type: {doc.doc_type}")
            print(f"   Linked to {len(links_map[doc_id])} documents:")
            
            for linked_doc_id in links_map[doc_id][:3]:  # Show first 3 links
                if linked_doc_id in documents:
                    linked_doc = documents[linked_doc_id]
                    print(f"     - {linked_doc.title} ({linked_doc.doc_type})")
            
            relationship_count += 1
    
    # Show link patterns
    print("\n🔍 Link Pattern Analysis:")
    
    # Count different types of links
    link_patterns = {
        'relative_paths': 0,
        'absolute_paths': 0,
        'same_category': 0,
        'cross_category': 0
    }
    
    for doc_id, doc in documents.items():
        for link in doc.linked_docs:
            if link.startswith('../'):
                link_patterns['relative_paths'] += 1
            elif link.startswith('/'):
                link_patterns['absolute_paths'] += 1
            else:
                link_patterns['relative_paths'] += 1
        
        # Check category relationships
        doc_category = doc.metadata.get('category', 'Unknown')
        for linked_doc_id in links_map.get(doc_id, []):
            if linked_doc_id in documents:
                linked_doc = documents[linked_doc_id]
                linked_category = linked_doc.metadata.get('category', 'Unknown')
                if doc_category == linked_category:
                    link_patterns['same_category'] += 1
                else:
                    link_patterns['cross_category'] += 1
    
    print(f"   📁 Relative path links: {link_patterns['relative_paths']}")
    print(f"   📁 Absolute path links: {link_patterns['absolute_paths']}")
    print(f"   🏷️  Same category links: {link_patterns['same_category']}")
    print(f"   🔄 Cross category links: {link_patterns['cross_category']}")
    
    # Show document structure
    print("\n📁 Document Structure:")
    structure = {}
    for doc_id, doc in documents.items():
        path_parts = doc.file_path.split('/')
        if len(path_parts) >= 2:
            category = path_parts[-2]  # Second to last part
            if category not in structure:
                structure[category] = []
            structure[category].append(doc.title)
    
    for category, docs in structure.items():
        print(f"   📂 {category}: {len(docs)} documents")
        for doc_title in docs[:3]:  # Show first 3 documents
            print(f"     - {doc_title}")
        if len(docs) > 3:
            print(f"     ... and {len(docs) - 3} more")
    
    print("\n✅ Document parsing test completed!")
    print("\n💡 The system successfully parsed all documents and built relationship mappings.")
    print("   To use the full Graph RAG system with vector search and LLM responses,")
    print("   set your OPENAI_API_KEY environment variable and run the main script.")

if __name__ == "__main__":
    test_document_parsing()
