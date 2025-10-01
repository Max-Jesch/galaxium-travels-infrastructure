# Galaxium Travels RAG Sample

This directory contains a simple RAG (Retrieval-Augmented Generation) implementation for Galaxium Travels using OpenAI embeddings and AstraDB vector store.

## Overview

The script demonstrates how to:
- Load sample documents from the `sample_docs/` directory
- Create OpenAI embeddings for document chunks
- Store embeddings in AstraDB vector store
- Perform semantic search queries

## Files

- `simple_rag_script.py` - Main RAG implementation script
- `requirements.txt` - Python dependencies
- `sample_docs/` - Sample markdown documents about Galaxium Travels services
- `datastax_ingestion_code.py` - Reference implementation from DataStax

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

You need to set the following environment variables:

```bash
export ASTRA_DB_APPLICATION_TOKEN="your_astra_token_here"
export ASTRA_DB_API_ENDPOINT="https://your-database-id-your-region.apps.astra.datastax.com"
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. Create AstraDB Database and Collection

Before running the script, ensure you have:
1. An AstraDB database created
2. A collection created (the script will use "galaxium_travels_rag" by default)
3. The appropriate API endpoint and token

## Usage

### Basic Usage

```bash
python simple_rag_script.py
```

The script will:
1. Load all markdown documents from `sample_docs/`
2. Split them into chunks for better retrieval
3. Generate OpenAI embeddings for each chunk
4. Store embeddings in AstraDB
5. Perform example searches to demonstrate functionality

### Example Searches

The script includes several example searches:
- Suborbital experience information
- Pricing options
- Safety features
- ISS visit details with similarity scores

## Customization

### Modify Search Queries

You can modify the search queries in the `main()` function:

```python
# Example custom search
results = rag.search("your custom query here", k=5)
```

### Adjust Chunking Parameters

Modify the text splitter in the `GalaxiumRAG` class:

```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # Increase for larger chunks
    chunk_overlap=300,  # Increase for more overlap
    length_function=len,
)
```

### Change Collection Settings

Update the collection name and namespace:

```python
rag = GalaxiumRAG(
    astra_token=ASTRA_TOKEN,
    astra_endpoint=ASTRA_ENDPOINT,
    openai_api_key=OPENAI_API_KEY,
    collection_name="your_collection_name",
    namespace="your_namespace"
)
```

## Sample Documents

The `sample_docs/` directory contains three sample documents:

1. **01_suborbital_experience.md** - Information about suborbital space flights
2. **02_earth_orbit_experience.md** - Details about orbital luxury experiences
3. **03_iss_visit.md** - International Space Station visit information

## API Reference

### GalaxiumRAG Class

#### Methods

- `load_documents(docs_dir)` - Load documents from directory
- `chunk_documents(documents)` - Split documents into chunks
- `setup_vector_store()` - Initialize AstraDB vector store
- `ingest_documents(documents)` - Store documents in vector store
- `search(query, k)` - Search for relevant documents
- `search_with_scores(query, k)` - Search with similarity scores

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Ensure all required environment variables are set
   - Check that the AstraDB token and endpoint are correct

2. **AstraDB Connection Issues**
   - Verify your database is active
   - Check that the API endpoint is correct
   - Ensure the collection exists or can be created

3. **OpenAI API Issues**
   - Verify your OpenAI API key is valid
   - Check that you have sufficient API credits
   - Ensure the API key has the necessary permissions

4. **Import Errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version compatibility

### Logging

The script uses Python's logging module. To see detailed logs:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

This is a basic RAG implementation. For production use, consider:

1. **Enhanced Chunking**: Implement more sophisticated document chunking strategies
2. **Metadata Filtering**: Add metadata-based filtering for more precise searches
3. **Hybrid Search**: Combine semantic and keyword search
4. **Query Processing**: Add query preprocessing and expansion
5. **Caching**: Implement result caching for better performance
6. **Monitoring**: Add logging and monitoring for production use

## License

This sample code is provided for educational and demonstration purposes.

