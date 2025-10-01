# =============================================================================
# CONFIGURATION FILE FOR GRAPH RAG SYSTEM
# =============================================================================

# Data Configuration
DATA_DIRECTORY = "97_raw_markdown_files"
COLLECTION_NAME = "galaxium_travels"

# Document Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embedding Configuration
EMBEDDING_DIMENSIONS = 384

# AstraDB Configuration
BATCH_SIZE = 50
DEFAULT_KEYSPACE = "default_keyspace"

# Display Configuration
MAX_SUMMARY_ITEMS = 5
MAX_RELATIONSHIP_ITEMS = 10

# Environment Variables (set these in your .env file)
REQUIRED_ENV_VARS = [
    "ASTRA_DB_APPLICATION_TOKEN",
    "ASTRA_DB_API_ENDPOINT",
    "ASTRA_DB_KEYSPACE"
]

OPTIONAL_ENV_VARS = [
    "OPENAI_API_KEY"  # If not set, will use simple test embeddings
]

def check_environment():
    """Check if required environment variables are set."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True

def get_config_summary():
    """Get a summary of current configuration."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    config = {
        "Data Directory": DATA_DIRECTORY,
        "Collection Name": COLLECTION_NAME,
        "Chunk Size": CHUNK_SIZE,
        "Chunk Overlap": CHUNK_OVERLAP,
        "Embedding Dimensions": EMBEDDING_DIMENSIONS,
        "Batch Size": BATCH_SIZE,
        "OpenAI API Key": "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Not set",
        "AstraDB Token": "✅ Set" if os.getenv("ASTRA_DB_APPLICATION_TOKEN") else "❌ Not set",
        "AstraDB Endpoint": "✅ Set" if os.getenv("ASTRA_DB_API_ENDPOINT") else "❌ Not set",
    }
    
    print("\n" + "="*50)
    print("🔧 CONFIGURATION SUMMARY")
    print("="*50)
    for key, value in config.items():
        print(f"{key}: {value}")
    print("="*50)
    
    return config

