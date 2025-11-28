"""
Async example usage of Azure Cosmos DB Python SDK v5

This example demonstrates async CRUD operations with the SDK.
"""

import os
import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError


async def main():
    # Initialize the async client
    endpoint = os.environ.get("COSMOS_ENDPOINT", "https://your-account.documents.azure.com:443/")
    key = os.environ.get("COSMOS_KEY", "your-key-here")
    
    async with CosmosClient(url=endpoint, credential=key) as client:
        # Create a database
        database_name = "async_example_database"
        print(f"Creating database: {database_name}")
        
        try:
            database_props = await client.create_database(database_name)
            print(f"Database created: {database_props}")
        except Exception as e:
            print(f"Database may already exist: {e}")
        
        # Get database client
        database = client.get_database_client(database_name)
        
        # Create a container
        container_name = "async_example_container"
        partition_key = {"paths": ["/userId"], "kind": "Hash"}
        
        print(f"\nCreating container: {container_name}")
        try:
            container_props = await database.create_container(container_name, partition_key)
            print(f"Container created: {container_props}")
        except Exception as e:
            print(f"Container may already exist: {e}")
        
        # Get container client
        container = database.get_container_client(container_name)
        
        # Create multiple items concurrently
        print("\n=== Creating Items Concurrently ===")
        items = [
            {"id": f"user{i}", "userId": f"user{i}", "name": f"User {i}", "score": i * 10}
            for i in range(1, 11)
        ]
        
        # Create all items concurrently
        create_tasks = [
            container.create_item(body=item, partition_key=item["userId"])
            for item in items
        ]
        
        try:
            results = await asyncio.gather(*create_tasks, return_exceptions=True)
            successful = sum(1 for r in results if not isinstance(r, Exception))
            print(f"Successfully created {successful}/{len(items)} items")
        except Exception as e:
            print(f"Error creating items: {e}")
        
        # Read items concurrently
        print("\n=== Reading Items Concurrently ===")
        read_tasks = [
            container.read_item(item=f"user{i}", partition_key=f"user{i}")
            for i in range(1, 6)
        ]
        
        read_results = await asyncio.gather(*read_tasks, return_exceptions=True)
        for result in read_results:
            if not isinstance(result, Exception):
                print(f"  {result.get('name')}: Score {result.get('score')}")
        
        # Query items asynchronously
        print("\n=== Querying Items ===")
        query = "SELECT * FROM c WHERE c.score > 50"
        items = await container.query_items(query=query)
        print(f"Found {len(items)} items with score > 50")
        
        # Update items concurrently
        print("\n=== Updating Items ===")
        update_tasks = []
        for i in range(1, 6):
            item = {
                "id": f"user{i}",
                "userId": f"user{i}",
                "name": f"Updated User {i}",
                "score": i * 20
            }
            update_tasks.append(container.upsert_item(body=item))
        
        await asyncio.gather(*update_tasks)
        print("Updated 5 items")
        
        # Delete items concurrently
        print("\n=== Deleting Items ===")
        delete_tasks = [
            container.delete_item(item=f"user{i}", partition_key=f"user{i}")
            for i in range(6, 11)
        ]
        
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print("Deleted 5 items")
        
        # Cleanup
        print("\n=== Cleanup ===")
        try:
            await container.delete()
            print(f"Deleted container: {container_name}")
        except Exception as e:
            print(f"Error deleting container: {e}")
        
        try:
            await database.delete()
            print(f"Deleted database: {database_name}")
        except Exception as e:
            print(f"Error deleting database: {e}")


if __name__ == "__main__":
    asyncio.run(main())
