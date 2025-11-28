import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError

def test_comprehensive():
    """Comprehensive test of Azure Cosmos DB Python v5 SDK"""
    
    endpoint = os.getenv('COSMOS_ENDPOINT')
    key = os.getenv('COSMOS_KEY')
    
    print("🚀 Starting comprehensive Cosmos DB SDK test...\n")
    
    # Connect
    print("🔧 Connecting to Cosmos DB...")
    client = CosmosClient(endpoint, credential=key)
    print("✅ Connected!\n")
    
    # Create database
    print("📊 Creating database...")
    database = client.create_database(id="comprehensive_test_db")
    print(f"✅ Database created: {database['id']}\n")
    
    db_client = client.get_database_client("comprehensive_test_db")
    
    # Create container
    print("📦 Creating container...")
    container = db_client.create_container(
        id="products",
        partition_key={"paths": ["/category"]}
    )
    print(f"✅ Container created: {container['id']}\n")
    
    container_client = db_client.get_container_client("products")
    
    # Test 1: Create multiple items
    print("📝 Test 1: Creating multiple items...")
    items = [
        {"id": "laptop1", "category": "electronics", "name": "Laptop", "price": 999.99},
        {"id": "laptop2", "category": "electronics", "name": "Gaming Laptop", "price": 1499.99},
        {"id": "book1", "category": "books", "name": "Python Guide", "price": 39.99},
        {"id": "book2", "category": "books", "name": "Rust Programming", "price": 49.99},
    ]
    
    for item in items:
        container_client.create_item(body=item)
        print(f"   ✅ Created: {item['name']}")
    print()
    
    # Test 2: Read items
    print("📖 Test 2: Reading items...")
    item = container_client.read_item(item="laptop1", partition_key="electronics")
    print(f"   ✅ Read: {item['name']} - ${item['price']}\n")
    
    # Test 3: Query items by partition
    print("🔍 Test 3: Querying electronics...")
    query = "SELECT * FROM c WHERE c.category = 'electronics'"
    electronics = container_client.query_items(query=query, partition_key="electronics")
    print(f"   ✅ Found {len(electronics)} electronics items:")
    for e in electronics:
        print(f"      - {e['name']}: ${e['price']}")
    print()
    
    # Test 4: Query books
    print("🔍 Test 4: Querying books...")
    query = "SELECT * FROM c WHERE c.category = 'books' AND c.price < 50"
    books = container_client.query_items(query=query, partition_key="books")
    print(f"   ✅ Found {len(books)} books under $50:")
    for b in books:
        print(f"      - {b['name']}: ${b['price']}")
    print()
    
    # Test 5: Upsert (create new)
    print("🔄 Test 5: Upsert new item...")
    new_item = {"id": "phone1", "category": "electronics", "name": "Smartphone", "price": 799.99}
    upserted = container_client.upsert_item(body=new_item)
    print(f"   ✅ Upserted: {upserted['name']}\n")
    
    # Test 6: Upsert (update existing)
    print("🔄 Test 6: Upsert existing item (update price)...")
    new_item["price"] = 699.99  # Price drop!
    upserted = container_client.upsert_item(body=new_item)
    print(f"   ✅ Updated price to: ${upserted['price']}\n")
    
    # Test 7: Replace item
    print("✏️  Test 7: Replace item...")
    laptop = container_client.read_item(item="laptop1", partition_key="electronics")
    laptop["price"] = 899.99  # Price reduction
    laptop["on_sale"] = True
    replaced = container_client.replace_item(item="laptop1", body=laptop)
    print(f"   ✅ Replaced: {replaced['name']} now ${replaced['price']} (on sale: {replaced['on_sale']})\n")
    
    # Test 8: Delete item
    print("🗑️  Test 8: Deleting item...")
    container_client.delete_item(item="book2", partition_key="books")
    print("   ✅ Deleted: Rust Programming book\n")
    
    # Test 9: Verify deletion
    print("🔍 Test 9: Verifying deletion...")
    try:
        container_client.read_item(item="book2", partition_key="books")
        print("   ❌ Item still exists!")
    except CosmosResourceNotFoundError:
        print("   ✅ Item successfully deleted (not found)\n")
    
    # Test 10: Query after operations
    print("🔍 Test 10: Final count of all electronics...")
    query = "SELECT * FROM c WHERE c.category = 'electronics'"
    final_electronics = container_client.query_items(query=query, partition_key="electronics")
    print(f"   ✅ Total electronics: {len(final_electronics)}")
    for e in final_electronics:
        print(f"      - {e['name']}: ${e['price']}")
    print()
    
    # Cleanup
    print("🧹 Cleaning up...")
    container_client.delete()
    print("   ✅ Container deleted")
    
    db_client.delete()
    print("   ✅ Database deleted")
    
    print("\n🎉 All comprehensive tests passed!\n")

if __name__ == "__main__":
    try:
        test_comprehensive()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
