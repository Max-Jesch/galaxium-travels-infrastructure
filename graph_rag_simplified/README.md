# 🚀 Galaxium Travels Document Preprocessing & Vector Indexing

A streamlined system for processing Galaxium Travels markdown documents and creating a vector database with graph traversal compatibility for Langflow integration.

## 🎯 **Purpose**

This system handles only the **data preparation phase** - no querying, no LLM integration, no complex graph traversal. It processes markdown documents and creates a properly formatted vector database that Langflow can use for both semantic search and graph traversal.

## 🏗️ **Architecture**

```
Markdown Documents → Document Parser → Link Resolution → Vector Embeddings → AstraDB Storage (Float Arrays)
```

## 📁 **File Structure**

```
graph_rag_simplified/
├── 97_raw_markdown_files/          # Source markdown documents
├── .env                            # Environment variables (create from .env-template)
├── requirements.txt                # Python dependencies
├── config.py                       # Configuration management
├── document_processor.py           # Markdown parsing and link resolution
├── vector_indexer.py               # OpenAI embeddings and AstraDB storage
├── index_documents.py              # Main indexing script
├── verify_index.py                 # Database verification script
└── README.md                       # This file
```

## 🚀 **Quick Start**

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Configure Environment**
```bash
# Copy and edit the environment template
cp .env-template .env
# Edit .env with your API keys
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ASTRA_DB_API_ENDPOINT`: Your AstraDB endpoint
- `ASTRA_DB_APPLICATION_TOKEN`: Your AstraDB token
- `ASTRA_DB_KEYSPACE`: Your AstraDB keyspace
- `ASTRA_DB_COLLECTION_NAME`: Collection name (default: galaxium_travels_documents_simplified)

### 3. **Index Documents**
```bash
python index_documents.py
```

### 4. **Verify Index**
```bash
python verify_index.py
```

## 🔧 **Key Features**

### **Document Processing**
- ✅ **28 markdown documents** from Galaxium Travels
- ✅ **Metadata extraction** (title, category, type, file path)
- ✅ **Link resolution** - converts markdown links to document IDs
- ✅ **Graph traversal ready** - `linked_docs` contains resolved document IDs

### **Vector Storage**
- ✅ **OpenAI embeddings** for all document content
- ✅ **Float array vectors** - not binary format
- ✅ **Langflow compatible** - vectors accessible as `[0.1, 0.2, ...]`
- ✅ **AstraDB integration** with proper configuration

### **Graph Traversal Compatibility**
- ✅ **Resolved document IDs** in `linked_docs` field
- ✅ **Consistent naming** - predictable document ID generation
- ✅ **Validated relationships** - all links verified to exist
- ✅ **Bidirectional traversal** - Langflow can traverse both directions

## 📊 **Data Model**

### **Document Structure**
```json
{
  "_id": "04_marketing_02_offerings_01_suborbital_experience",
  "content": "document_content",
  "metadata": {
    "title": "Suborbital Experience",
    "category": "marketing",
    "doc_type": "offering",
    "file_path": "04_marketing/02_offerings/01_suborbital_experience.md",
    "linked_docs": [
      "04_marketing_02_offerings_02_earth_orbit_experience",
      "04_marketing_03_spacecraft_specs_galaxium_aurora_explorer_specs"
    ]
  },
  "$vector": [0.011600582860410213, -0.0247, 0.0156, ...]
}
```

## 🛠️ **Usage**

### **Main Indexing Script**
```bash
python index_documents.py
```

This script:
1. Loads configuration and validates environment variables
2. Processes all markdown documents
3. Resolves links to document IDs for graph traversal
4. Generates OpenAI embeddings
5. Stores documents in AstraDB with proper vector format
6. Verifies vector format and functionality

### **Verification Script**
```bash
python verify_index.py
```

This script:
1. Verifies database connection
2. Checks vector format (float arrays vs binary)
3. Validates graph traversal compatibility
4. Tests vector search functionality
5. Shows comprehensive database summary

## 🔍 **Verification Checks**

The system performs several verification checks:

1. **Database Connection** - Ensures AstraDB is accessible
2. **Vector Format** - Verifies vectors are stored as float arrays
3. **Graph Traversal** - Checks that `linked_docs` contains document IDs
4. **Vector Search** - Tests similarity search functionality

## 🎯 **Success Criteria**

- ✅ **All 28 documents** processed and indexed
- ✅ **Vectors stored as `$vector` fields** with float arrays
- ✅ **All links resolved** to valid document IDs
- ✅ **`linked_docs` field contains** actual document IDs, not file paths
- ✅ **Langflow can access vectors** directly from `$vector` field
- ✅ **Langflow can traverse** from any document to its linked documents

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
ASTRA_DB_API_ENDPOINT=your_astradb_endpoint_here
ASTRA_DB_APPLICATION_TOKEN=your_astradb_token_here
ASTRA_DB_KEYSPACE=your_keyspace_here

# Optional
ASTRA_DB_COLLECTION_NAME=galaxium_travels_documents_simplified
```

### **AstraDB Vector Format**
The system uses the proper AstraPy configuration to ensure vectors are stored as float arrays:

```python
api_options = APIOptions(
    serdes_options=SerdesOptions(
        binary_encode_vectors=False,  # This is the key flag!
        custom_datatypes_in_reading=False
    )
)
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Missing environment variables**
   - Check that `.env` file exists and contains all required variables
   - Verify API keys are valid

2. **Vector format issues**
   - Ensure `binary_encode_vectors=False` is set in AstraPy configuration
   - Run verification script to check vector format

3. **Link resolution problems**
   - Check that markdown links use proper syntax `[text](path)`
   - Verify that linked documents exist in the document set

4. **Database connection errors**
   - Verify AstraDB credentials and endpoint
   - Check that keyspace and collection exist

### **Debug Mode**
Enable debug logging by modifying the logging level in the scripts:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 **Performance**

- **Processing time**: ~2-3 minutes for 28 documents
- **Vector generation**: OpenAI embeddings (1536 dimensions)
- **Storage**: AstraDB with float array vectors
- **Memory usage**: Minimal (processes documents in batches)

## 🔮 **Next Steps**

After successful indexing:

1. **Connect to Langflow** - Use the AstraDB collection for vector search
2. **Configure graph traversal** - Use `linked_docs` field for document relationships
3. **Test queries** - Verify both semantic search and graph traversal work
4. **Monitor performance** - Check query response times and accuracy

## 📝 **Document Types**

The system processes these document types:
- **Offerings** - Space travel packages and experiences
- **Spacecraft** - Technical specifications and capabilities
- **Training** - Safety certifications and requirements
- **Research** - Future destinations and technology
- **Corporate** - Company policies and procedures
- **Legal** - Terms of service and compliance
- **Technical** - System architecture and crisis response
- **Finance** - Budget and financial planning
- **IT** - Technology infrastructure
- **Emergency** - Emergency procedures and protocols

## 🎉 **Ready for Langflow!**

Once indexing is complete and verification passes, your database is ready for Langflow integration with:
- ✅ **Proper vector format** for semantic search
- ✅ **Resolved document relationships** for graph traversal
- ✅ **Comprehensive metadata** for filtering and organization
- ✅ **Validated functionality** for reliable operation

---

*This system provides a clean, focused solution for document preprocessing and vector indexing, designed specifically for Langflow integration.*

