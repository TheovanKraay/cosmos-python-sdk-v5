"""
Test script to verify the Python v5 SDK works with Azure Cosmos DB Emulator
"""
import os
from azure.cosmos import CosmosClient

# Emulator configuration
ENDPOINT = os.getenv("COSMOS_ENDPOINT", "https://localhost:8081")
KEY = os.getenv("COSMOS_KEY", "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==")

def test_basic_operations():
    """Test basic CRUD operations with the emulator"""
    
    print("🔧 Connecting to Cosmos DB Emulator...")
    client = CosmosClient(ENDPOINT, credential=KEY)
    print("✅ Connected successfully!")
    
    # Create database
    print("\n📊 Creating database 'testdb'...")
    database = client.create_database(id="testdb")
    print(f"✅ Database created: {database}")
    
    # Get database client
    print("\n🔗 Getting database client...")
    db_client = client.get_database_client("testdb")
    print("✅ Database client obtained!")
    
    # Create container
    print("\n📦 Creating container 'testcontainer'...")
    container = db_client.create_container(
        id="testcontainer",
        partition_key={"paths": ["/category"]}
    )
    print(f"✅ Container created: {container}")
    
    # Get container client
    print("\n🔗 Getting container client...")
    container_client = db_client.get_container_client("testcontainer")
    print("✅ Container client obtained!")
    
    # Create an item
    print("\n📝 Creating item...")
    item = {
        "id": "item1",
        "category": "test",
        "name": "Test Item",
        "description": "This is a test item"
    }
    created_item = container_client.create_item(body=item)
    print(f"✅ Item created: {created_item}")
    
    # Read the item
    print("\n📖 Reading item...")
    read_item = container_client.read_item(item="item1", partition_key="test")
    print(f"✅ Item read: {read_item}")
    
    # Query items
    print("\n🔍 Querying items...")
    query = "SELECT * FROM c WHERE c.category = 'test'"
    items = container_client.query_items(query=query, partition_key="test")
    print(f"✅ Query returned {len(items)} items")
    for item in items:
        print(f"   - {item}")
    
    # Delete the item
    print("\n🗑️  Deleting item...")
    container_client.delete_item(item="item1", partition_key="test")
    print("✅ Item deleted!")
    
    # Delete container
    print("\n🗑️  Deleting container...")
    container_client.delete()
    print("✅ Container deleted!")
    
    # Delete database
    print("\n🗑️  Deleting database...")
    client.delete_database("testdb")
    print("✅ Database deleted!")
    
    print("\n🎉 All tests passed successfully!")

if __name__ == "__main__":
    try:
        test_basic_operations()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
