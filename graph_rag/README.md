# 🚀 Galaxium Travels Graph RAG System

A sophisticated graph-based retrieval augmented generation (RAG) system for the Galaxium Travels markdown documents. This system creates a knowledge graph from document relationships and enables intelligent querying with graph traversal capabilities.

## 📁 Project Structure

```
graph_rag/
├── 📖 README.md                           # This file
├── 📦 requirements.txt                    # Python dependencies
├── 🔧 .env-template                      # Environment configuration template
├── 📚 97_raw_markdown_files/             # Source documents (28 markdown files)
├── 🎯 galaxium_graph_rag_demo.ipynb      # Main interactive demo notebook
├── 💻 src/                               # Core source code
│   ├── galaxium_graph_rag.py            # Main Graph RAG implementation
│   ├── demo_graph_rag.py                # Command-line demo
│   ├── test_*.py                         # Unit tests
│   └── venv/                            # Virtual environment
├── 🧪 tests/                             # Test scripts
│   ├── test_vector_format.py            # Vector format tests
│   └── test_collection_config.py        # Collection configuration tests
├── 🛠️ scripts/                          # Utility scripts
│   ├── reindex_collection.py            # Full re-indexing script
│   ├── trigger_reindexing.py            # Interactive re-indexing
│   ├── debug_vector_storage.py          # Vector storage debugging
│   ├── check_database_vectors.py        # Database vector inspection
│   └── verify_vector_format.py          # Vector format verification
├── 📖 docs/                             # Documentation
│   ├── CONVERSATION_SUMMARY.md          # Development history
│   └── vector_format_summary.md         # Vector format analysis
└── 🎨 examples/                         # Example scripts
    └── demo_vector_format_fix.py        # Vector format demonstration
```

## 🚀 Quick Start

### Option 1: Interactive Demo (Recommended)
```bash
# Open the main notebook
jupyter notebook galaxium_graph_rag_demo.ipynb
```

### Option 2: Command Line
```bash
# Run the command-line demo
python src/demo_graph_rag.py
```

### Option 3: Re-indexing
```bash
# Re-index documents to a new collection
python scripts/reindex_collection.py --collection my_new_collection
```

## 🔧 Configuration

Copy the environment template and fill in your credentials:
```bash
cp .env-template .env
# Edit .env with your API keys
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ASTRA_DB_API_ENDPOINT`: Your AstraDB endpoint
- `ASTRA_DB_APPLICATION_TOKEN`: Your AstraDB token
- `ASTRA_DB_COLLECTION_NAME`: Collection name (default: galaxium_travels_documents_2)

## 🧪 Testing

Run the test suite:
```bash
# Test vector format
python tests/test_vector_format.py

# Test collection configuration
python tests/test_collection_config.py
```

## 🛠️ Scripts

### Re-indexing
```bash
# Full re-indexing with options
python scripts/reindex_collection.py --collection galaxium_travels_documents_2

# Interactive re-indexing
python scripts/trigger_reindexing.py

# Force re-indexing (no confirmation)
python scripts/reindex_collection.py --force
```

### Debugging
```bash
# Debug vector storage
python scripts/debug_vector_storage.py

# Check database vectors
python scripts/check_database_vectors.py

# Verify vector format
python scripts/verify_vector_format.py
```

## 📊 System Capabilities

- **28 markdown documents** from Galaxium Travels
- **40+ relationships** discovered automatically
- **12 document types**: corporate, spacecraft, offerings, training, etc.
- **Enterprise-grade storage** with AstraDB integration
- **Interactive visualizations** with NetworkX and Plotly
- **Graph traversal** for related content discovery
- **LLM integration** with GPT-4 for contextual responses

## 🎯 Key Features

- **Document Parsing**: Automatic extraction of content and relationships
- **Knowledge Graph Construction**: Builds relationships from markdown links
- **Vector Embeddings**: OpenAI embeddings for semantic search
- **Graph Traversal**: Finds related documents through relationships
- **LLM Integration**: GPT-4 for contextual responses
- **Enterprise Storage**: AstraDB for production use
- **Interactive Visualizations**: Clear graphs with readable file names and arrows

## 📖 Documentation

- **Development History**: `docs/CONVERSATION_SUMMARY.md`
- **Vector Format Analysis**: `docs/vector_format_summary.md`
- **Source Code Docs**: `src/README.md`

## 🚀 Next Steps

1. **Web Interface**: Create Flask/FastAPI web app
2. **API Endpoints**: Expose system via REST API
3. **Chat Interface**: Build conversational interface
4. **Performance Optimization**: Caching and batch processing
5. **Additional Visualizations**: More graph analysis tools
6. **Integration**: Connect with other business systems

---

*This system provides a complete Graph RAG solution for enterprise document management with advanced graph traversal and intelligent querying capabilities.*