#!/usr/bin/env python3
"""
Document processor for Galaxium Travels markdown documents
Handles parsing, metadata extraction, and link resolution for graph traversal compatibility
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessedDocument:
    """Represents a processed document with resolved links"""
    doc_id: str
    title: str
    content: str
    file_path: str
    doc_type: str
    category: str
    linked_docs: List[str]  # Resolved document IDs for graph traversal
    metadata: Dict[str, Any]

class DocumentProcessor:
    """Processes markdown documents and resolves links for graph traversal"""
    
    def __init__(self, documents_path: Path):
        self.documents_path = documents_path
        self.documents: Dict[str, ProcessedDocument] = {}
        
    def generate_document_id(self, file_path: Path) -> str:
        """Generate consistent document ID from file path"""
        relative_path = file_path.relative_to(self.documents_path)
        # Convert: 04_marketing/02_offerings/01_suborbital_experience.md
        # To: 04_marketing_02_offerings_01_suborbital_experience
        doc_id = str(relative_path).replace('/', '_').replace('.md', '')
        return doc_id
    
    def extract_title(self, content: str, file_path: Path) -> str:
        """Extract title from first # heading or use filename"""
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        return file_path.stem
    
    def extract_links_from_content(self, content: str) -> List[str]:
        """Extract markdown links from document content"""
        # Pattern to match markdown links: [text](path)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
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
    
    def determine_category_and_type(self, file_path: Path) -> tuple[str, str]:
        """Determine document category and type from file path"""
        path_str = str(file_path).lower()
        
        # Determine category
        if '01_corporate' in path_str:
            category = 'corporate'
        elif '02_customer_service' in path_str:
            category = 'customer_service'
        elif '03_hr' in path_str:
            category = 'hr'
        elif '04_marketing' in path_str:
            category = 'marketing'
        elif '05_legal' in path_str:
            category = 'legal'
        elif '06_technical' in path_str:
            category = 'technical'
        elif '07_finance' in path_str:
            category = 'finance'
        elif '08_it' in path_str:
            category = 'it'
        elif '09_emergency' in path_str:
            category = 'emergency'
        else:
            category = 'general'
        
        # Determine document type
        if 'offerings' in path_str:
            doc_type = 'offering'
        elif 'spacecraft' in path_str or 'specs' in path_str:
            doc_type = 'spacecraft'
        elif 'training' in path_str or 'certification' in path_str:
            doc_type = 'training'
        elif 'research' in path_str:
            doc_type = 'research'
        elif 'corporate' in path_str:
            doc_type = 'corporate'
        elif 'hr' in path_str:
            doc_type = 'hr'
        elif 'marketing' in path_str:
            doc_type = 'marketing'
        elif 'technical' in path_str:
            doc_type = 'technical'
        elif 'legal' in path_str:
            doc_type = 'legal'
        elif 'finance' in path_str:
            doc_type = 'finance'
        elif 'it' in path_str:
            doc_type = 'it'
        elif 'emergency' in path_str:
            doc_type = 'emergency'
        else:
            doc_type = 'general'
        
        return category, doc_type
    
    def extract_metadata(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from document content"""
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
        
        return metadata
    
    def resolve_links(self, raw_links: List[str], all_documents: Dict[str, ProcessedDocument]) -> List[str]:
        """Resolve markdown links to document IDs for graph traversal"""
        resolved_links = []
        
        for link_path in raw_links:
            # Try to find matching document
            for doc_id, doc in all_documents.items():
                if (link_path in doc.file_path or 
                    link_path in doc.title.lower() or
                    any(link_path in path_part for path_part in doc.file_path.split('/'))):
                    resolved_links.append(doc_id)
                    break
        
        return resolved_links
    
    def parse_document(self, file_path: Path) -> Optional[ProcessedDocument]:
        """Parse a single markdown document"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate document ID
            doc_id = self.generate_document_id(file_path)
            
            # Extract title
            title = self.extract_title(content, file_path)
            
            # Extract links
            raw_links = self.extract_links_from_content(content)
            
            # Determine category and type
            category, doc_type = self.determine_category_and_type(file_path)
            
            # Extract metadata
            metadata = self.extract_metadata(content, file_path)
            metadata.update({
                'file_path': str(file_path),
                'file_name': file_path.name,
                'category': category,
                'doc_type': doc_type
            })
            
            return ProcessedDocument(
                doc_id=doc_id,
                title=title,
                content=content,
                file_path=str(file_path),
                doc_type=doc_type,
                category=category,
                linked_docs=[],  # Will be resolved later
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {e}")
            return None
    
    def process_all_documents(self) -> Dict[str, ProcessedDocument]:
        """Process all markdown documents and resolve links"""
        logger.info("Processing markdown documents...")
        
        # First pass: parse all documents
        md_files = list(self.documents_path.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")
        
        for file_path in md_files:
            doc = self.parse_document(file_path)
            if doc:
                self.documents[doc.doc_id] = doc
                logger.info(f"Parsed: {doc.title} ({doc.doc_type})")
        
        # Second pass: resolve links
        logger.info("Resolving document links...")
        for doc_id, doc in self.documents.items():
            # Re-extract links for this document
            raw_links = self.extract_links_from_content(doc.content)
            # Resolve to document IDs
            resolved_links = self.resolve_links(raw_links, self.documents)
            doc.linked_docs = resolved_links
            
            if resolved_links:
                logger.info(f"  {doc.title}: {len(resolved_links)} linked documents")
        
        total_relationships = sum(len(doc.linked_docs) for doc in self.documents.values())
        logger.info(f"Processed {len(self.documents)} documents with {total_relationships} relationships")
        
        return self.documents
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Get summary of processed documents"""
        summary = {
            'total_documents': len(self.documents),
            'total_relationships': sum(len(doc.linked_docs) for doc in self.documents.values()),
            'documents_by_type': {},
            'documents_by_category': {},
            'most_connected_documents': []
        }
        
        # Count by type and category
        for doc in self.documents.values():
            doc_type = doc.doc_type
            category = doc.category
            
            summary['documents_by_type'][doc_type] = summary['documents_by_type'].get(doc_type, 0) + 1
            summary['documents_by_category'][category] = summary['documents_by_category'].get(category, 0) + 1
        
        # Find most connected documents
        connection_counts = [(doc_id, len(doc.linked_docs)) for doc_id, doc in self.documents.items()]
        connection_counts.sort(key=lambda x: x[1], reverse=True)
        
        for doc_id, count in connection_counts[:10]:
            doc = self.documents[doc_id]
            summary['most_connected_documents'].append({
                'title': doc.title,
                'type': doc.doc_type,
                'connections': count
            })
        
        return summary

