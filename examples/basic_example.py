"""
Example usage of Azure Cosmos DB Python SDK v5

This example demonstrates basic CRUD operations with the SDK.
"""

import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError


def main():
    # Initialize the client
    endpoint = os.environ.get("COSMOS_ENDPOINT", "https://your-account.documents.azure.com:443/")
    key = os.environ.get("COSMOS_KEY", "your-key-here")
    
    client = CosmosClient(url=endpoint, credential=key)
    
    # Create a database
    database_name = "example_database"
    print(f"Creating database: {database_name}")
    
    try:
        database_props = client.create_database(database_name)
        print(f"Database created: {database_props}")
    except Exception as e:
        print(f"Database may already exist: {e}")
    
    # Get database client
    database = client.get_database_client(database_name)
    
    # Create a container
    container_name = "example_container"
    partition_key = {"paths": ["/category"], "kind": "Hash"}
    
    print(f"\nCreating container: {container_name}")
    try:
        container_props = database.create_container(container_name, partition_key)
        print(f"Container created: {container_props}")
    except Exception as e:
        print(f"Container may already exist: {e}")
    
    # Get container client
    container = database.get_container_client(container_name)
    
    # Create items
    print("\n=== Creating Items ===")
    items_to_create = [
        {
            "id": "item1",
            "category": "electronics",
            "name": "Laptop",
            "price": 999.99
        },
        {
            "id": "item2",
            "category": "electronics",
            "name": "Mouse",
            "price": 29.99
        },
        {
            "id": "item3",
            "category": "books",
            "name": "Python Programming",
            "price": 49.99
        }
    ]
    
    for item in items_to_create:
        try:
            created = container.create_item(body=item, partition_key=item["category"])
            print(f"Created item: {created['id']} - {created['name']}")
        except Exception as e:
            print(f"Item may already exist: {e}")
    
    # Read an item
    print("\n=== Reading Item ===")
    try:
        item = container.read_item(item="item1", partition_key="electronics")
        print(f"Read item: {item['id']} - {item['name']} - ${item['price']}")
    except CosmosResourceNotFoundError:
        print("Item not found")
    
    # Query items
    print("\n=== Querying Items ===")
    query = "SELECT * FROM c WHERE c.category = 'electronics'"
    items = container.query_items(query=query)
    print(f"Found {len(items)} electronics items:")
    for item in items:
        print(f"  - {item.get('name', 'Unknown')}: ${item.get('price', 0)}")
    
    # Update an item (upsert)
    print("\n=== Updating Item ===")
    item_to_update = {
        "id": "item1",
        "category": "electronics",
        "name": "Laptop",
        "price": 899.99,  # Price reduced!
        "on_sale": True
    }
    
    updated = container.upsert_item(body=item_to_update)
    print(f"Updated item: {updated['id']} - New price: ${updated['price']}")
    
    # Replace an item
    print("\n=== Replacing Item ===")
    replacement_item = {
        "id": "item2",
        "category": "electronics",
        "name": "Wireless Mouse",
        "price": 39.99,
        "wireless": True
    }
    
    replaced = container.replace_item(item="item2", body=replacement_item)
    print(f"Replaced item: {replaced['id']} - {replaced['name']}")
    
    # Query all items
    print("\n=== All Items ===")
    all_items = container.query_items(query="SELECT * FROM c")
    for item in all_items:
        print(f"  {item.get('id')}: {item.get('name')} (${item.get('price')})")
    
    # Delete an item
    print("\n=== Deleting Item ===")
    try:
        container.delete_item(item="item3", partition_key="books")
        print("Deleted item: item3")
    except CosmosResourceNotFoundError:
        print("Item not found")
    
    # List containers
    print("\n=== Listing Containers ===")
    containers = database.list_containers()
    print(f"Found {len(containers)} containers")
    
    # Cleanup (optional)
    print("\n=== Cleanup ===")
    cleanup = input("Do you want to delete the container and database? (yes/no): ")
    
    if cleanup.lower() == "yes":
        try:
            container.delete()
            print(f"Deleted container: {container_name}")
        except Exception as e:
            print(f"Error deleting container: {e}")
        
        try:
            database.delete()
            print(f"Deleted database: {database_name}")
        except Exception as e:
            print(f"Error deleting database: {e}")
    else:
        print("Skipping cleanup")


if __name__ == "__main__":
    main()
