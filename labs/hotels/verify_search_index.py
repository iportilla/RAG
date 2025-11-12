"""
Azure Search Index Verification Script
Use this to test your search configuration and verify fields
"""

import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Load environment variables
load_dotenv()

SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "")
SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "hotels-sample-index")

def test_search():
    """Test basic search functionality"""
    
    print("=" * 60)
    print("AZURE SEARCH INDEX VERIFICATION")
    print("=" * 60)
    
    # Initialize client
    try:
        credential = AzureKeyCredential(SEARCH_API_KEY)
        search_client = SearchClient(
            endpoint=SEARCH_SERVICE_ENDPOINT,
            index_name=SEARCH_INDEX_NAME,
            credential=credential
        )
        print("✅ Successfully connected to Azure Search")
        print(f"   Endpoint: {SEARCH_SERVICE_ENDPOINT}")
        print(f"   Index: {SEARCH_INDEX_NAME}\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Test 1: Get all documents
    print("-" * 60)
    print("TEST 1: Retrieving all documents")
    print("-" * 60)
    try:
        results = search_client.search(
            search_text="*",
            include_total_count=True,
            top=5
        )
        total_count = results.get_count()
        print(f"✅ Total documents in index: {total_count}")
        
        # Show first document
        first_doc = next(results, None)
        if first_doc:
            print(f"\n📄 Sample document fields:")
            for key in first_doc.keys():
                if not key.startswith('@'):
                    value = first_doc.get(key)
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"   - {key}: {value}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Search for "pool"
    print("\n" + "-" * 60)
    print("TEST 2: Searching for 'pool'")
    print("-" * 60)
    try:
        results = search_client.search(
            search_text="pool",
            include_total_count=True,
            select=["HotelName", "Description", "Tags"]
        )
        total_count = results.get_count()
        print(f"✅ Found {total_count} hotels with 'pool'")
        
        if total_count > 0:
            print("\n🏨 Hotels with pools:")
            for idx, hotel in enumerate(results, 1):
                print(f"\n   {idx}. {hotel.get('HotelName', 'Unknown')}")
                
                # Check where "pool" appears
                desc = hotel.get('Description', '')
                tags = hotel.get('Tags', [])
                
                if 'pool' in desc.lower():
                    print(f"      ✓ Found in Description")
                if tags and any('pool' in str(tag).lower() for tag in tags):
                    print(f"      ✓ Found in Tags: {tags}")
        else:
            print("⚠️  No hotels found with 'pool'")
            print("\nPossible reasons:")
            print("   1. The word 'pool' doesn't exist in any searchable fields")
            print("   2. The Description or Tags fields are not marked as 'Searchable'")
            print("   3. The data doesn't contain pool information")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Search without specifying fields (let index decide)
    print("\n" + "-" * 60)
    print("TEST 3: Searching 'pool' using default searchable fields")
    print("-" * 60)
    print("ℹ️  Not specifying search_fields - Azure Search will use all 'Searchable' fields")
    try:
        results = search_client.search(
            search_text="pool",
            include_total_count=True,
            select=["HotelName", "Description", "Tags"]
        )
        total_count = results.get_count()
        print(f"✅ Found {total_count} hotels using default searchable fields")
        
        if total_count > 0:
            for idx, hotel in enumerate(results, 1):
                print(f"   {idx}. {hotel.get('HotelName', 'Unknown')}")
        else:
            print("⚠️  This means 'pool' is not in any searchable fields in your index")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Search for common terms
    print("\n" + "-" * 60)
    print("TEST 4: Testing other common search terms")
    print("-" * 60)
    
    test_terms = ["beach", "spa", "wifi", "restaurant", "luxury"]
    for term in test_terms:
        try:
            results = search_client.search(
                search_text=term,
                include_total_count=True,
                top=0  # Just get count
            )
            count = results.get_count()
            print(f"   '{term}': {count} results")
        except Exception as e:
            print(f"   '{term}': Error - {e}")
    
    # Test 5: Check a specific hotel's full content
    print("\n" + "-" * 60)
    print("TEST 5: Examining a hotel's full content")
    print("-" * 60)
    try:
        results = search_client.search(
            search_text="*",
            top=1
        )
        hotel = next(results, None)
        if hotel:
            print(f"🏨 {hotel.get('HotelName', 'Unknown Hotel')}")
            print(f"\n   Description:")
            desc = hotel.get('Description', 'N/A')
            print(f"   {desc[:300]}...")
            
            tags = hotel.get('Tags', [])
            if tags:
                print(f"\n   Tags: {tags}")
            
            # Check for pool mentions
            full_text = desc.lower()
            if 'pool' in full_text:
                print(f"\n   ✅ This hotel mentions 'pool' in description!")
            else:
                print(f"\n   ⚠️  This hotel does NOT mention 'pool'")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - If pool searches return 0 results, the data may not contain 'pool'")
    print("   - Check if Description/Tags fields are marked as 'Searchable' in Azure Portal")
    print("   - Try searching for terms that appear in the sample hotel above")
    print("   - The hotels-sample data may have different amenities than expected")
    print("\n")

if __name__ == "__main__":
    test_search()
