# 🚀 Galaxium Travels Graph RAG System

A sophisticated graph-based retrieval augmented generation (RAG) system for the Galaxium Travels markdown documents. This system creates a knowledge graph from document relationships and enables intelligent querying with graph traversal capabilities.

## 🌟 Features

- **Document Parsing**: Automatically extracts content and metadata from markdown files
- **Knowledge Graph Construction**: Builds relationships between documents based on internal links
- **Vector Embeddings**: Uses OpenAI embeddings for semantic search
- **Graph Traversal**: Traverses document relationships to find related content
- **Intelligent Querying**: Combines semantic search with graph traversal for comprehensive results
- **LLM Integration**: Uses GPT-4 for generating contextual answers
- **Interactive Visualizations**: NetworkX and Plotly graphs with clear arrows and readable file names

## 🏗️ Architecture

The system consists of several key components:

1. **Document Parser**: Extracts content, metadata, and relationships from markdown files
2. **Knowledge Graph Builder**: Creates a graph structure from document relationships
3. **Vector Store**: Stores document embeddings for semantic search (AstraDB)
4. **Graph Retriever**: Combines vector search with graph traversal
5. **LLM Integration**: Generates intelligent responses using GPT-4

## 📁 Project Structure

```
graph_rag/
├── galaxium_graph_rag_demo.ipynb    # 🎯 MAIN ENTRY POINT - Interactive Demo
├── README.md                        # 📖 This documentation
├── requirements.txt                 # 📦 Python dependencies
├── .env                            # 🔧 Environment configuration
├── .env-template                   # 🔧 Environment template
├── 97_raw_markdown_files/          # 📚 Source documents (28 markdown files)
└── src/                            # 💻 Source code & supporting files
    ├── galaxium_graph_rag.py       # 🧠 Core system implementation
    ├── demo_graph_rag.py           # 🚀 Command-line demo script
    ├── test_astradb_graph_rag.py    # 🧪 AstraDB integration tests
    ├── test_document_parsing.py    # 🧪 Document parsing tests
    ├── venv/                        # 🐍 Virtual environment
    └── README.md                    # 📖 Source code documentation
```

## 🚀 Quick Start

### Option 1: Interactive Demo (Recommended)
1. **Open the main notebook**: `galaxium_graph_rag_demo.ipynb`
2. **Follow the step-by-step guide** in the notebook
3. **Run all cells** to see the complete system in action

### Option 2: Command Line
1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set up environment variables** (see Configuration section)
3. **Run the demo**: `python src/demo_graph_rag.py`

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the root directory with:

```bash
OPENAI_API_KEY=your_openai_api_key_here
ASTRA_DB_API_ENDPOINT=your_astradb_endpoint_here
ASTRA_DB_APPLICATION_TOKEN=your_astradb_token_here
ASTRA_DB_KEYSPACE=your_keyspace_here  # Optional
```

### Dependencies
Install required packages:
```bash
pip install -r requirements.txt
```

### Vector Storage Format

The system is configured to store vectors in AstraDB as **float arrays** instead of binary format for better readability and debugging:

**Before (Binary Format):**
```json
"$vector": {"$binary": "PM8/ZLuBuZe8aukOvGsiK7zz1X..."}
```

**After (Float Array Format):**
```json
"$vector": [0.011600582860410213, -0.0247, 0.0156, ...]
```

This is achieved through a custom vector insertion method (`_add_documents_with_float_vectors`) that:
- Bypasses LangChain's default binary encoding
- Directly inserts documents with float array vectors
- Maintains compatibility with AstraDB's vector search capabilities
- Provides better debugging and inspection capabilities

### Re-indexing Documents

When you need to re-index documents into a new collection or update existing data:

**Full Re-indexing:**
```bash
python reindex_collection.py --collection galaxium_travels_documents_2
```

**Quick Re-indexing:**
```bash
python trigger_reindexing.py
```

**Force Re-indexing (no confirmation):**
```bash
python reindex_collection.py --force
```

**Programmatic Re-indexing:**
```python
# Create new collection with different name
graph_rag = GalaxiumGraphRAG(
    documents_path,
    astra_db_collection_name="my_new_collection"
)
graph_rag.build_knowledge_graph()
graph_rag.create_vector_store()  # This creates the new collection
```

## 📊 System Capabilities

### Document Analysis
- **28 markdown documents** from Galaxium Travels
- **12 document types**: corporate, spacecraft, offerings, training, etc.
- **40+ relationships** between documents
- **Automatic link detection** from markdown files

### Graph Visualization
- **Interactive Plotly graphs** with zoom and hover
- **NetworkX static visualizations** with clear arrows
- **Focused views** for most connected documents
- **Full file names** for maximum readability
- **Color-coded nodes** by document type

### Query Capabilities
- **Semantic search** using OpenAI embeddings
- **Graph traversal** to find related documents
- **Contextual responses** using GPT-4
- **Multi-hop reasoning** across document relationships

## 🎯 Use Cases

- **Customer Service**: Answer questions about space travel offerings
- **Knowledge Management**: Find related documents and procedures
- **Research & Development**: Explore future destinations and technologies
- **Safety & Training**: Understand safety requirements and procedures
- **Business Intelligence**: Analyze pricing and market opportunities

## 🧪 Testing

Run the test suites:
```bash
# Test AstraDB integration
python src/test_astradb_graph_rag.py

# Test document parsing
python src/test_document_parsing.py
```

## 📈 Performance

- **28 documents** processed and indexed
- **40+ relationships** discovered automatically
- **Sub-second query response** times
- **Enterprise-grade storage** with AstraDB
- **Scalable architecture** for larger document collections

## 🔧 Advanced Features

### Graph Visualization
- **Clear arrows** showing document relationships
- **Readable file names** without truncation
- **Multiple visualization options** (static, interactive, focused)
- **Professional styling** with color-coded document types

### Query Processing
- **Intelligent retrieval** combining semantic and graph search
- **Context-aware responses** using document relationships
- **Multi-document reasoning** across the knowledge graph
- **Real-time processing** with live query capabilities

## 📚 Documentation

- **Main Demo**: `galaxium_graph_rag_demo.ipynb` - Complete interactive walkthrough
- **Source Code**: `src/README.md` - Technical documentation
- **System Overview**: Built-in documentation in the notebook

## 🌟 Key Highlights

- **Professional Structure**: Clean, organized folder layout
- **Interactive Demo**: Step-by-step notebook with live examples
- **Visual Excellence**: Clear graphs with readable file names and arrows
- **Enterprise Ready**: AstraDB integration for production use
- **Comprehensive Testing**: Full test coverage for all components

---

*Built for Galaxium Travels - Where luxury meets the infinite.* 🌟