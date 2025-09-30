# Source Code

This folder contains the source code and supporting files for the Galaxium Travels Graph RAG system.

## 📁 Files in this folder:

### Core System Files
- **`galaxium_graph_rag.py`** - Main system implementation with all classes and functions
- **`demo_graph_rag.py`** - Command-line demo script for testing the system

### Test Files
- **`test_astradb_graph_rag.py`** - Tests for AstraDB integration
- **`test_document_parsing.py`** - Tests for document parsing functionality

### Configuration
- **`requirements.txt`** - Python dependencies for the system
- **`venv/`** - Virtual environment with installed packages

## 🚀 Usage

### Command Line Demo
```bash
python demo_graph_rag.py
```

### Run Tests
```bash
# Test AstraDB integration
python test_astradb_graph_rag.py

# Test document parsing
python test_document_parsing.py
```

### Import the System
```python
from galaxium_graph_rag import GalaxiumGraphRAG

# Initialize the system
graph_rag = GalaxiumGraphRAG(
    documents_path="./97_raw_markdown_files",
    openai_api_key="your_key",
    astra_db_api_endpoint="your_endpoint",
    astra_db_application_token="your_token"
)

# Build the knowledge graph
documents, links_map = graph_rag.build_knowledge_graph()

# Create vector store
graph_rag.create_vector_store()

# Create graph retriever
graph_rag.create_graph_retriever()

# Query the system
results = graph_rag.query("What space travel offerings are available?")
```

## 🎯 Main Entry Point

The main entry point for the system is the **`galaxium_graph_rag_demo.ipynb`** notebook in the parent directory, which provides a complete interactive demonstration of the Graph RAG system with visualizations and step-by-step examples.

## 📦 Dependencies

Install the required packages:
```bash
pip install -r requirements.txt
```

## 🔧 Environment Setup

Make sure to set up your environment variables in the parent directory's `.env` file:
- `OPENAI_API_KEY`
- `ASTRA_DB_API_ENDPOINT`
- `ASTRA_DB_APPLICATION_TOKEN`
- `ASTRA_DB_KEYSPACE` (optional)