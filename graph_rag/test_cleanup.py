#!/usr/bin/env python3
"""
Test script to verify that the cleanup didn't break anything
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all imports still work after cleanup"""
    
    print("🧪 Testing Imports After Cleanup")
    print("=" * 40)
    
    try:
        # Test main import
        from galaxium_graph_rag import GalaxiumGraphRAG
        print("✅ Main import successful")
        
        # Test that we can create an instance
        graph_rag = GalaxiumGraphRAG(
            documents_path="./97_raw_markdown_files",
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            astra_db_api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'),
            astra_db_application_token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            astra_db_keyspace=os.getenv('ASTRA_DB_KEYSPACE'),
            astra_db_collection_name=os.getenv('ASTRA_DB_COLLECTION_NAME', 'test_cleanup_collection')
        )
        print("✅ Graph RAG instance created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_file_structure():
    """Test that the file structure is correct"""
    
    print("\n📁 Testing File Structure")
    print("=" * 40)
    
    # Check that directories exist
    required_dirs = ['src', 'tests', 'scripts', 'docs', 'examples', '97_raw_markdown_files']
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            return False
    
    # Check that key files exist
    key_files = [
        'README.md',
        'requirements.txt',
        '.env-template',
        'galaxium_graph_rag_demo.ipynb',
        'src/galaxium_graph_rag.py',
        'tests/test_vector_format.py',
        'scripts/reindex_collection.py'
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def main():
    """Main test function"""
    
    print("🧹 Graph RAG Cleanup Verification")
    print("=" * 50)
    
    # Test file structure
    structure_ok = test_file_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    if structure_ok and imports_ok:
        print("\n🎉 Cleanup successful!")
        print("✅ All files are in the correct locations")
        print("✅ All imports are working")
        print("✅ File structure is clean and organized")
    else:
        print("\n❌ Cleanup issues detected!")
        if not structure_ok:
            print("   - File structure problems")
        if not imports_ok:
            print("   - Import problems")

if __name__ == "__main__":
    main()

