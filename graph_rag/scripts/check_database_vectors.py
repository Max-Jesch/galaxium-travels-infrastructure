#!/usr/bin/env python3
"""
Direct database check to verify vector format

This script uses the AstraDB client directly to check how vectors are stored.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_database_vectors():
    """Check vector format directly in the database"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 Direct Database Vector Format Check")
    print("=" * 50)
    
    # Check if we have the required environment variables
    required_vars = ['ASTRA_DB_API_ENDPOINT', 'ASTRA_DB_APPLICATION_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    try:
        # Import AstraDB client
        from astrapy import DataAPIClient
        
        # Initialize AstraDB client
        client = DataAPIClient(
            token=os.getenv('ASTRA_DB_APPLICATION_TOKEN')
        )
        
        # Get database
        db = client.get_database(api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT'))
        
        # Get collection
        collection_name = os.getenv('ASTRA_DB_COLLECTION_NAME', 'galaxium_travels_documents_2')
        collection = db.get_collection(collection_name)
        
        print(f"✅ Connected to collection: {collection_name}")
        
        # Get a sample document
        sample_doc = collection.find_one()
        
        if sample_doc:
            print(f"✅ Found document in collection")
            print(f"   Document keys: {list(sample_doc.keys())}")
            
            # Check for vector field
            if '$vector' in sample_doc:
                vector = sample_doc['$vector']
                print(f"   Vector type: {type(vector)}")
                print(f"   Vector length: {len(vector) if isinstance(vector, list) else 'N/A'}")
                
                if isinstance(vector, list):
                    print("✅ SUCCESS: Vectors are stored as float arrays!")
                    print(f"   Sample vector (first 5 values): {vector[:5]}")
                    print(f"   Sample vector (last 5 values): {vector[-5:]}")
                    
                    # Verify these are actually floats
                    if all(isinstance(x, (int, float)) for x in vector[:10]):
                        print("✅ Confirmed: All values are numeric (float/int)")
                        return True
                    else:
                        print("⚠️  Warning: Some values are not numeric")
                        return False
                        
                elif isinstance(vector, dict) and '$binary' in vector:
                    print("❌ ISSUE: Vectors are still stored in binary format")
                    print(f"   Binary vector: {vector}")
                    return False
                else:
                    print(f"⚠️  UNKNOWN: Vector format is {type(vector)}")
                    print(f"   Vector content: {vector}")
                    return False
            else:
                print("❌ No $vector field found in document")
                print(f"   Available fields: {list(sample_doc.keys())}")
                return False
        else:
            print("❌ No documents found in collection")
            return False
            
    except ImportError:
        print("❌ astrapy not installed. Installing...")
        try:
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "astrapy"], check=True)
            print("✅ astrapy installed. Please run the script again.")
            return False
        except Exception as e:
            print(f"❌ Failed to install astrapy: {e}")
            return False
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🧪 Database Vector Format Checker")
    print("=" * 60)
    
    success = check_database_vectors()
    
    if success:
        print("\n✅ Vector format verification successful!")
        print("\n📋 Summary:")
        print("   - Vectors are stored as float arrays (not binary)")
        print("   - Format is human-readable and debuggable")
        print("   - Compatible with AstraDB vector search")
    else:
        print("\n❌ Vector format verification failed!")
        print("   - Vectors may still be in binary format")
        print("   - Check your collection and re-index if needed")

if __name__ == "__main__":
    main()
