#!/bin/bash

# Re-indexing script for Galaxium Travels with fixed vector storage
# This script re-indexes all documents into a new collection using the updated approach

echo "🚀 Galaxium Travels Re-indexing Script"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "src/galaxium_graph_rag.py" ]; then
    echo "❌ Error: Please run this script from the graph_rag directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: .../galaxium-travels-infrastructure/graph_rag"
    exit 1
fi

# Check for required environment variables
echo "🔍 Checking environment variables..."

required_vars=("OPENAI_API_KEY" "ASTRA_DB_API_ENDPOINT" "ASTRA_DB_APPLICATION_TOKEN" "ASTRA_DB_KEYSPACE")

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please set these variables before running the script."
    echo "Example:"
    echo "   export OPENAI_API_KEY='your-key'"
    echo "   export ASTRA_DB_API_ENDPOINT='your-endpoint'"
    echo "   export ASTRA_DB_APPLICATION_TOKEN='your-token'"
    echo "   export ASTRA_DB_KEYSPACE='your-keyspace'"
    exit 1
fi

echo "✅ All required environment variables are set"

# Choose re-indexing mode
echo ""
echo "Choose re-indexing mode:"
echo "1) Quick re-index (minimal output)"
echo "2) Full re-index (with testing and inspection)"
echo "3) Test vector storage fix only"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🚀 Running quick re-index..."
        python3 scripts/quick_reindex.py
        ;;
    2)
        echo "🚀 Running full re-index with testing..."
        python3 scripts/reindex_with_fixed_vector_storage.py
        ;;
    3)
        echo "🧪 Testing vector storage fix..."
        python3 scripts/test_vector_storage_fix.py
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎯 Re-indexing script completed!"

