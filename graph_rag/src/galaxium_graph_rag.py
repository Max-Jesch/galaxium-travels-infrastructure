#!/usr/bin/env python3
"""
Galaxium Travels Graph RAG System

This script implements a graph-based retrieval augmented generation (RAG) system
for the Galaxium Travels markdown documents. It creates a knowledge graph from
the document relationships and enables sophisticated querying with graph traversal.

Features:
- Document parsing and metadata extraction
- Knowledge graph construction from document relationships
- Vector embeddings for semantic search
- Graph traversal for related content discovery
- Query processing with context from connected documents
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging

# Core libraries
import pandas as pd
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_astradb import AstraDBVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_graph_retriever import GraphRetriever
from graph_retriever.strategies import Eager

# AstraPy configuration for plain float arrays
from astrapy.api_options import APIOptions, SerdesOptions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentNode:
    """Represents a document node in the knowledge graph"""
    doc_id: str
    title: str
    content: str
    file_path: str
    doc_type: str
    metadata: Dict[str, Any]
    linked_docs: List[str] = None
    
    def __post_init__(self):
        if self.linked_docs is None:
            self.linked_docs = []

class GalaxiumDocumentParser:
    """Parser for Galaxium Travels markdown documents"""
    
    def __init__(self, documents_path: str):
        self.documents_path = Path(documents_path)
        self.documents = {}
        self.links_map = {}
        
    def extract_links_from_content(self, content: str) -> List[str]:
        """Extract markdown links from document content"""
        # Pattern to match markdown links: [text](path)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        # Also look for relative path references
        relative_path_pattern = r'\[([^\]]+)\]\(\.\.?/[^)]+\)'
        relative_links = re.findall(relative_path_pattern, content)
        
        all_links = []
        for link_text, link_path in links:
            # Convert relative paths to absolute
            if link_path.startswith('../'):
                # Remove ../ and convert to proper path
                clean_path = link_path.replace('../', '')
                all_links.append(clean_path)
            elif link_path.startswith('./'):
                all_links.append(link_path[2:])
            else:
                all_links.append(link_path)
                
        return all_links
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from document frontmatter and content"""
        metadata = {}
        
        # Extract document version, dates, etc. from headers
        version_match = re.search(r'\*\*Document Version\*\*:\s*([^\n]+)', content)
        if version_match:
            metadata['version'] = version_match.group(1).strip()
            
        effective_date_match = re.search(r'\*\*Effective Date\*\*:\s*([^\n]+)', content)
        if effective_date_match:
            metadata['effective_date'] = effective_date_match.group(1).strip()
            
        prepared_by_match = re.search(r'\*\*Prepared by\*\*:\s*([^\n]+)', content)
        if prepared_by_match:
            metadata['prepared_by'] = prepared_by_match.group(1).strip()
            
        approved_by_match = re.search(r'\*\*Approved by\*\*:\s*([^\n]+)', content)
        if approved_by_match:
            metadata['approved_by'] = approved_by_match.group(1).strip()
            
        # Extract document type from path
        if 'offerings' in str(self.documents_path):
            metadata['category'] = 'offerings'
        elif 'spacecraft_specs' in str(self.documents_path):
            metadata['category'] = 'spacecraft'
        elif 'training' in str(self.documents_path):
            metadata['category'] = 'training'
        elif 'research' in str(self.documents_path):
            metadata['category'] = 'research'
        elif 'corporate' in str(self.documents_path):
            metadata['category'] = 'corporate'
        elif 'hr' in str(self.documents_path):
            metadata['category'] = 'hr'
        elif 'marketing' in str(self.documents_path):
            metadata['category'] = 'marketing'
        elif 'technical' in str(self.documents_path):
            metadata['category'] = 'technical'
        elif 'legal' in str(self.documents_path):
            metadata['category'] = 'legal'
        elif 'finance' in str(self.documents_path):
            metadata['category'] = 'finance'
        elif 'it' in str(self.documents_path):
            metadata['category'] = 'it'
        elif 'emergency' in str(self.documents_path):
            metadata['category'] = 'emergency'
        else:
            metadata['category'] = 'general'
            
        return metadata
    
    def determine_doc_type(self, file_path: str, content: str) -> str:
        """Determine document type based on path and content"""
        path_str = str(file_path).lower()
        
        if 'offerings' in path_str:
            return 'offering'
        elif 'spacecraft' in path_str or 'specs' in path_str:
            return 'spacecraft'
        elif 'training' in path_str or 'certification' in path_str:
            return 'training'
        elif 'research' in path_str:
            return 'research'
        elif 'corporate' in path_str:
            return 'corporate'
        elif 'hr' in path_str:
            return 'hr'
        elif 'marketing' in path_str:
            return 'marketing'
        elif 'technical' in path_str:
            return 'technical'
        elif 'legal' in path_str:
            return 'legal'
        elif 'finance' in path_str:
            return 'finance'
        elif 'it' in path_str:
            return 'it'
        elif 'emergency' in path_str:
            return 'emergency'
        else:
            return 'general'
    
    def parse_document(self, file_path: Path) -> DocumentNode:
        """Parse a single markdown document"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title (first # heading)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else file_path.stem
            
            # Extract links
            links = self.extract_links_from_content(content)
            
            # Extract metadata
            metadata = self.extract_metadata(content)
            metadata['file_path'] = str(file_path)
            metadata['file_name'] = file_path.name
            
            # Determine document type
            doc_type = self.determine_doc_type(str(file_path), content)
            
            # Create document ID
            doc_id = str(file_path.relative_to(self.documents_path)).replace('/', '_').replace('.md', '')
            
            return DocumentNode(
                doc_id=doc_id,
                title=title,
                content=content,
                file_path=str(file_path),
                doc_type=doc_type,
                metadata=metadata,
                linked_docs=links
            )
            
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {e}")
            return None
    
    def parse_all_documents(self) -> Dict[str, DocumentNode]:
        """Parse all markdown documents in the directory"""
        documents = {}
        
        # Find all markdown files recursively
        md_files = list(self.documents_path.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")
        
        for file_path in md_files:
            doc = self.parse_document(file_path)
            if doc:
                documents[doc.doc_id] = doc
                logger.info(f"Parsed: {doc.title} ({doc.doc_type})")
        
        self.documents = documents
        return documents
    
    def build_links_map(self) -> Dict[str, List[str]]:
        """Build a map of document relationships"""
        links_map = {}
        
        for doc_id, doc in self.documents.items():
            links_map[doc_id] = []
            
            for link in doc.linked_docs:
                # Try to find matching documents
                for other_doc_id, other_doc in self.documents.items():
                    if (link in other_doc.file_path or 
                        link in other_doc.title.lower() or
                        any(link in path_part for path_part in other_doc.file_path.split('/'))):
                        links_map[doc_id].append(other_doc_id)
        
        self.links_map = links_map
        return links_map

class GalaxiumGraphRAG:
    """Main Graph RAG system for Galaxium Travels documents"""
    
    def __init__(self, documents_path: str, openai_api_key: str = None, 
                 astra_db_api_endpoint: str = None, astra_db_application_token: str = None,
                 astra_db_keyspace: str = None, astra_db_collection_name: str = None):
        self.documents_path = documents_path
        self.parser = GalaxiumDocumentParser(documents_path)
        self.vectorstore = None
        self.retriever = None
        self.documents = {}
        self.links_map = {}
        
        # Initialize OpenAI
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key
        
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        # AstraDB configuration
        self.astra_db_api_endpoint = astra_db_api_endpoint or os.getenv('ASTRA_DB_API_ENDPOINT')
        self.astra_db_application_token = astra_db_application_token or os.getenv('ASTRA_DB_APPLICATION_TOKEN')
        self.astra_db_keyspace = astra_db_keyspace or os.getenv('ASTRA_DB_KEYSPACE')
        self.astra_db_collection_name = astra_db_collection_name or os.getenv('ASTRA_DB_COLLECTION_NAME', 'galaxium_travels_documents_2')
        
    def build_knowledge_graph(self):
        """Build the knowledge graph from documents"""
        logger.info("Building knowledge graph...")
        
        # Parse all documents
        self.documents = self.parser.parse_all_documents()
        
        # Build links map
        self.links_map = self.parser.build_links_map()
        
        logger.info(f"Built knowledge graph with {len(self.documents)} documents")
        logger.info(f"Total relationships: {sum(len(links) for links in self.links_map.values())}")
        
        return self.documents, self.links_map
    
    def create_vector_store(self):
        """Create vector store from documents"""
        logger.info("Creating vector store...")
        
        # Convert documents to LangChain format
        langchain_docs = []
        
        for doc_id, doc in self.documents.items():
            # Create metadata with relationship information
            metadata = doc.metadata.copy()
            metadata.update({
                'doc_id': doc_id,
                'doc_type': doc.doc_type,
                'title': doc.title,
                'file_path': doc.file_path,
                'linked_docs': doc.linked_docs
            })
            
            # Create LangChain document
            langchain_doc = Document(
                page_content=doc.content,
                metadata=metadata
            )
            langchain_docs.append(langchain_doc)
        
        # Create AstraDB vector store
        if self.astra_db_api_endpoint and self.astra_db_application_token:
            logger.info(f"Using AstraDB vector store with collection: {self.astra_db_collection_name}")
            
            # Configure AstraPy to use plain float arrays instead of binary encoding
            api_options = APIOptions(
                serdes_options=SerdesOptions(
                    binary_encode_vectors=False,
                    custom_datatypes_in_reading=False
                )
            )
            
            self.vectorstore = AstraDBVectorStore(
                embedding=self.embeddings,
                collection_name=self.astra_db_collection_name,
                api_endpoint=self.astra_db_api_endpoint,
                token=self.astra_db_application_token,
                namespace=self.astra_db_keyspace,
                pre_delete_collection=True,  # Clear existing data
                api_options=api_options,  # Use plain float arrays
            )
        else:
            logger.info("Using in-memory vector store (AstraDB credentials not provided)...")
            self.vectorstore = InMemoryVectorStore(self.embeddings)
        
        # Add documents to vector store using standard method
        if langchain_docs:
            logger.info(f"Adding {len(langchain_docs)} documents to vector store...")
            self.vectorstore.add_documents(langchain_docs)
            logger.info(f"Successfully added {len(langchain_docs)} documents to vector store")
        else:
            logger.warning("No documents to add to vector store")
        
        logger.info(f"Created vector store with {len(langchain_docs)} documents")
    
    def get_database_object(self):
        """Get direct access to AstraDB database object for custom operations"""
        if not self.astra_db_api_endpoint or not self.astra_db_application_token:
            return None
        
        try:
            from astrapy import DataAPIClient
            
            # Configure AstraPy to use plain float arrays instead of binary encoding
            api_options = APIOptions(
                serdes_options=SerdesOptions(
                    binary_encode_vectors=False,
                    custom_datatypes_in_reading=False
                )
            )
            
            client = DataAPIClient(
                token=self.astra_db_application_token,
                api_options=api_options
            )
            return client.get_database(
                api_endpoint=self.astra_db_api_endpoint,
                token=self.astra_db_application_token,
                keyspace=self.astra_db_keyspace,
            )
        except Exception as e:
            logger.error(f"Error getting database object: {e}")
            return None
    
    def get_collection_object(self):
        """Get direct access to AstraDB collection for custom operations"""
        database = self.get_database_object()
        if not database:
            return None
        
        try:
            return database.get_collection(
                self.astra_db_collection_name, 
                keyspace=self.astra_db_keyspace
            )
        except Exception as e:
            logger.error(f"Error getting collection object: {e}")
            return None
    
    def inspect_vector_storage(self, limit: int = 5):
        """Inspect how vectors are actually stored in the database"""
        collection = self.get_collection_object()
        if not collection:
            logger.error("Cannot inspect vector storage - no collection access")
            return None
        
        try:
            # Get a few documents to inspect their structure
            documents = list(collection.find({}, limit=limit))
            logger.info(f"Retrieved {len(documents)} documents for inspection")
            
            for i, doc in enumerate(documents):
                logger.info(f"\nDocument {i+1}:")
                logger.info(f"  ID: {doc.get('_id', 'N/A')}")
                logger.info(f"  Content length: {len(doc.get('content', ''))}")
                logger.info(f"  Metadata keys: {list(doc.get('metadata', {}).keys())}")
                
                # Check for vector field
                if '$vector' in doc:
                    vector = doc['$vector']
                    if isinstance(vector, list):
                        logger.info(f"  Vector: Array with {len(vector)} dimensions")
                        logger.info(f"  Vector sample: {vector[:5]}...")
                    elif isinstance(vector, dict) and '$binary' in vector:
                        logger.info(f"  Vector: Binary format ({len(vector['$binary'])} chars)")
                    else:
                        logger.info(f"  Vector: {type(vector)} format")
                else:
                    logger.info("  Vector: No $vector field found")
                
                # Check for other vector-related fields
                vector_fields = [k for k in doc.keys() if 'vector' in k.lower()]
                if vector_fields:
                    logger.info(f"  Other vector fields: {vector_fields}")
                
            return documents
            
        except Exception as e:
            logger.error(f"Error inspecting vector storage: {e}")
            return None
        
    def create_graph_retriever(self):
        """Create graph retriever with edge traversal"""
        logger.info("Creating graph retriever...")
        
        # Define edges for graph traversal
        # These edges will be used to traverse from one document to related documents
        edges = [
            ("doc_id", "linked_docs"),  # Direct document relationships
            ("doc_type", "doc_type"),   # Same type relationships
            ("category", "category")    # Same category relationships
        ]
        
        # Create graph retriever
        self.retriever = GraphRetriever(
            store=self.vectorstore,
            edges=edges,
            strategy=Eager(
                start_k=5,      # Initial documents to retrieve
                adjacent_k=10,   # Related documents to traverse to
                select_k=20,     # Total documents to return
                max_depth=2      # Maximum traversal depth
            )
        )
        
        logger.info("Graph retriever created successfully")
    
    def query(self, question: str, include_context: bool = True) -> Dict[str, Any]:
        """Query the graph RAG system"""
        logger.info(f"Processing query: {question}")
        
        # Retrieve relevant documents using graph traversal
        retrieved_docs = self.retriever.invoke(question)
        
        # Compile results
        results = {
            'question': question,
            'retrieved_documents': [],
            'related_documents': {},
            'context': '',
            'answer': ''
        }
        
        # Process retrieved documents
        for doc in retrieved_docs:
            doc_info = {
                'title': doc.metadata.get('title', 'Unknown'),
                'doc_type': doc.metadata.get('doc_type', 'Unknown'),
                'category': doc.metadata.get('category', 'Unknown'),
                'content': doc.page_content[:500] + '...' if len(doc.page_content) > 500 else doc.page_content,
                'similarity_score': doc.metadata.get('_similarity_score', 0),
                'depth': doc.metadata.get('_depth', 0)
            }
            results['retrieved_documents'].append(doc_info)
        
        # Group documents by type
        doc_types = {}
        for doc in retrieved_docs:
            doc_type = doc.metadata.get('doc_type', 'Unknown')
            if doc_type not in doc_types:
                doc_types[doc_type] = []
            doc_types[doc_type].append(doc)
        
        results['related_documents'] = {
            doc_type: [doc.metadata.get('title', 'Unknown') for doc in docs]
            for doc_type, docs in doc_types.items()
        }
        
        if include_context:
            # Create context for LLM
            context_parts = []
            for doc in retrieved_docs[:10]:  # Limit to top 10 documents
                context_parts.append(f"Document: {doc.metadata.get('title', 'Unknown')}")
                context_parts.append(f"Type: {doc.metadata.get('doc_type', 'Unknown')}")
                context_parts.append(f"Content: {doc.page_content[:1000]}...")
                context_parts.append("---")
            
            results['context'] = "\n".join(context_parts)
            
            # Generate answer using LLM
            prompt = f"""
            Based on the following Galaxium Travels documents, please answer the question: {question}
            
            Documents:
            {results['context']}
            
            Please provide a comprehensive answer based on the information in these documents.
            """
            
            try:
                response = self.llm.invoke(prompt)
                results['answer'] = response.content
            except Exception as e:
                logger.error(f"Error generating answer: {e}")
                results['answer'] = "Unable to generate answer at this time."
        
        return results
    
    def get_document_relationships(self, doc_id: str) -> Dict[str, Any]:
        """Get relationships for a specific document"""
        if doc_id not in self.documents:
            return {}
        
        doc = self.documents[doc_id]
        relationships = {
            'document': {
                'id': doc_id,
                'title': doc.title,
                'type': doc.doc_type,
                'category': doc.metadata.get('category', 'Unknown')
            },
            'linked_documents': [],
            'incoming_links': []
        }
        
        # Get outgoing links
        for linked_doc_id in self.links_map.get(doc_id, []):
            if linked_doc_id in self.documents:
                linked_doc = self.documents[linked_doc_id]
                relationships['linked_documents'].append({
                    'id': linked_doc_id,
                    'title': linked_doc.title,
                    'type': linked_doc.doc_type
                })
        
        # Get incoming links
        for other_doc_id, links in self.links_map.items():
            if doc_id in links and other_doc_id != doc_id:
                other_doc = self.documents[other_doc_id]
                relationships['incoming_links'].append({
                    'id': other_doc_id,
                    'title': other_doc.title,
                    'type': other_doc.doc_type
                })
        
        return relationships
    
    def visualize_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        stats = {
            'total_documents': len(self.documents),
            'total_relationships': sum(len(links) for links in self.links_map.values()),
            'documents_by_type': {},
            'documents_by_category': {},
            'most_connected_documents': []
        }
        
        # Count by type
        for doc in self.documents.values():
            doc_type = doc.doc_type
            category = doc.metadata.get('category', 'Unknown')
            
            stats['documents_by_type'][doc_type] = stats['documents_by_type'].get(doc_type, 0) + 1
            stats['documents_by_category'][category] = stats['documents_by_category'].get(category, 0) + 1
        
        # Find most connected documents
        connection_counts = [(doc_id, len(links)) for doc_id, links in self.links_map.items()]
        connection_counts.sort(key=lambda x: x[1], reverse=True)
        
        for doc_id, count in connection_counts[:10]:
            if doc_id in self.documents:
                doc = self.documents[doc_id]
                stats['most_connected_documents'].append({
                    'title': doc.title,
                    'type': doc.doc_type,
                    'connections': count
                })
        
        return stats

def main():
    """Main function to demonstrate the Graph RAG system"""
    
    # Configuration
    DOCUMENTS_PATH = "/Users/max/Library/CloudStorage/OneDrive-IBM/01_CODE/galaxium-travels-infrastructure/graph_rag/97_raw_markdown_files"
    
    # Initialize the Graph RAG system
    print("Initializing Galaxium Travels Graph RAG System...")
    graph_rag = GalaxiumGraphRAG(
        DOCUMENTS_PATH,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
        astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
        astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
        astra_db_collection_name=os.getenv('ASTRA_DB_COLLECTION_NAME')
    )
    
    # Build knowledge graph
    print("\nBuilding knowledge graph...")
    documents, links_map = graph_rag.build_knowledge_graph()
    
    # Create vector store
    print("\nCreating vector store...")
    graph_rag.create_vector_store()
    
    # Inspect vector storage format
    print("\nInspecting vector storage format...")
    graph_rag.inspect_vector_storage(limit=3)
    
    # Create graph retriever
    print("\nCreating graph retriever...")
    graph_rag.create_graph_retriever()
    
    # Get graph statistics
    print("\nGraph Statistics:")
    stats = graph_rag.visualize_graph_stats()
    print(f"Total documents: {stats['total_documents']}")
    print(f"Total relationships: {stats['total_relationships']}")
    print(f"Documents by type: {stats['documents_by_type']}")
    print(f"Documents by category: {stats['documents_by_category']}")
    
    # Example queries
    example_queries = [
        "What are the different space travel offerings available?",
        "What safety certifications are required for lunar missions?",
        "What spacecraft are used for different types of missions?",
        "What are the future destinations being planned?",
        "What training is required for space missions?"
    ]
    
    print("\n" + "="*80)
    print("EXAMPLE QUERIES AND RESULTS")
    print("="*80)
    
    for query in example_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        try:
            results = graph_rag.query(query)
            
            print(f"Retrieved {len(results['retrieved_documents'])} documents")
            print(f"Document types: {list(results['related_documents'].keys())}")
            
            if results['answer']:
                print(f"\nAnswer: {results['answer'][:500]}...")
            
        except Exception as e:
            print(f"Error processing query: {e}")
        
        print("\n" + "-" * 60)
    
    # Show document relationships for a specific document
    print("\n" + "="*80)
    print("DOCUMENT RELATIONSHIPS EXAMPLE")
    print("="*80)
    
    # Find a document with relationships
    for doc_id, doc in documents.items():
        if len(links_map.get(doc_id, [])) > 0:
            print(f"\nDocument: {doc.title}")
            relationships = graph_rag.get_document_relationships(doc_id)
            print(f"Linked documents: {len(relationships['linked_documents'])}")
            print(f"Incoming links: {len(relationships['incoming_links'])}")
            break

if __name__ == "__main__":
    main()
