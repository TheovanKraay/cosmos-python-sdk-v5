"""Tests for async operations."""

import pytest
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import (
    CosmosResourceNotFoundError,
    CosmosResourceExistsError,
)


class TestAsyncCosmosClient:
    """Test suite for async CosmosClient."""

    @pytest.mark.asyncio
    async def test_async_client_creation(self, account_url, account_key):
        """Test creating an async client."""
        client = CosmosClient(account_url, credential=account_key)
        assert client is not None

    @pytest.mark.asyncio
    async def test_async_client_context_manager(self, account_url, account_key):
        """Test async client as context manager."""
        async with CosmosClient(account_url, credential=account_key) as client:
            assert client is not None

    @pytest.mark.asyncio
    async def test_async_create_database(self, async_client, test_database_id):
        """Test creating a database asynchronously."""
        result = await async_client.create_database(test_database_id)
        assert result is not None
        assert result.get("id") == test_database_id
        
        # Cleanup
        await async_client.delete_database(test_database_id)

    @pytest.mark.asyncio
    async def test_async_get_database_client(self, async_client, test_database_id):
        """Test getting a database client asynchronously."""
        await async_client.create_database(test_database_id)
        
        try:
            db_client = async_client.get_database_client(test_database_id)
            assert db_client is not None
            assert db_client.id == test_database_id
        finally:
            await async_client.delete_database(test_database_id)

    @pytest.mark.asyncio
    async def test_async_delete_database(self, async_client, test_database_id):
        """Test deleting a database asynchronously."""
        await async_client.create_database(test_database_id)
        await async_client.delete_database(test_database_id)
        
        # Verify deletion
        db_client = async_client.get_database_client(test_database_id)
        with pytest.raises(CosmosResourceNotFoundError):
            await db_client.read()

    @pytest.mark.asyncio
    async def test_async_list_databases(self, async_client, test_database_id):
        """Test listing databases asynchronously."""
        await async_client.create_database(test_database_id)
        
        try:
            databases = await async_client.list_databases()
            assert isinstance(databases, list)
            assert len(databases) > 0
        finally:
            await async_client.delete_database(test_database_id)


class TestAsyncDatabaseProxy:
    """Test suite for async DatabaseProxy."""

    @pytest.mark.asyncio
    async def test_async_database_read(self, async_database):
        """Test reading database properties asynchronously."""
        result = await async_database.read()
        assert result is not None

    @pytest.mark.asyncio
    async def test_async_create_container(self, async_database, test_container_id):
        """Test creating a container asynchronously."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        result = await async_database.create_container(test_container_id, partition_key)
        assert result is not None
        assert result.get("id") == test_container_id
        
        # Cleanup
        await async_database.delete_container(test_container_id)

    @pytest.mark.asyncio
    async def test_async_get_container_client(self, async_database, test_container_id):
        """Test getting a container client asynchronously."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        await async_database.create_container(test_container_id, partition_key)
        
        try:
            container = async_database.get_container_client(test_container_id)
            assert container is not None
            assert container.id == test_container_id
        finally:
            await async_database.delete_container(test_container_id)

    @pytest.mark.asyncio
    async def test_async_delete_container(self, async_database, test_container_id):
        """Test deleting a container asynchronously."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        await async_database.create_container(test_container_id, partition_key)
        await async_database.delete_container(test_container_id)
        
        # Verify deletion
        container = async_database.get_container_client(test_container_id)
        with pytest.raises(CosmosResourceNotFoundError):
            await container.read()

    @pytest.mark.asyncio
    async def test_async_list_containers(self, async_database, test_container_id):
        """Test listing containers asynchronously."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        await async_database.create_container(test_container_id, partition_key)
        
        try:
            containers = await async_database.list_containers()
            assert isinstance(containers, list)
        finally:
            await async_database.delete_container(test_container_id)


class TestAsyncContainerOperations:
    """Test suite for async container item operations."""

    @pytest.mark.asyncio
    async def test_async_create_item(self, async_container):
        """Test creating an item asynchronously."""
        item = {
            "id": "async_item_1",
            "name": "Async Test Item",
            "value": 100
        }
        
        result = await async_container.create_item(body=item)
        assert result is not None
        assert result.get("id") == item["id"]

    @pytest.mark.asyncio
    async def test_async_read_item(self, async_container):
        """Test reading an item asynchronously."""
        item = {
            "id": "async_item_read",
            "name": "Async Read Test",
            "value": 200
        }
        
        await async_container.create_item(body=item)
        
        result = await async_container.read_item(
            item="async_item_read",
            partition_key="async_item_read"
        )
        assert result is not None
        assert result.get("id") == item["id"]
        assert result.get("value") == item["value"]

    @pytest.mark.asyncio
    async def test_async_upsert_item(self, async_container):
        """Test upserting an item asynchronously."""
        item = {
            "id": "async_item_upsert",
            "name": "Async Upsert",
            "value": 300
        }
        
        # First upsert (create)
        result1 = await async_container.upsert_item(body=item)
        assert result1 is not None
        
        # Second upsert (update)
        item["value"] = 400
        result2 = await async_container.upsert_item(body=item)
        assert result2 is not None

    @pytest.mark.asyncio
    async def test_async_replace_item(self, async_container):
        """Test replacing an item asynchronously."""
        item = {
            "id": "async_item_replace",
            "name": "Original",
            "value": 1
        }
        
        await async_container.create_item(body=item)
        
        new_item = {
            "id": "async_item_replace",
            "name": "Replaced",
            "value": 2
        }
        
        result = await async_container.replace_item(
            item="async_item_replace",
            body=new_item
        )
        assert result is not None
        assert result.get("name") == "Replaced"

    @pytest.mark.asyncio
    async def test_async_delete_item(self, async_container):
        """Test deleting an item asynchronously."""
        item = {
            "id": "async_item_delete",
            "name": "To Be Deleted"
        }
        
        await async_container.create_item(body=item)
        await async_container.delete_item(
            item="async_item_delete",
            partition_key="async_item_delete"
        )
        
        # Verify deletion
        with pytest.raises(CosmosResourceNotFoundError):
            await async_container.read_item(
                item="async_item_delete",
                partition_key="async_item_delete"
            )

    @pytest.mark.asyncio
    async def test_async_query_items(self, async_container):
        """Test querying items asynchronously."""
        # Create multiple items
        items = [
            {"id": f"async_query_{i}", "name": f"Item {i}", "value": i}
            for i in range(5)
        ]
        
        for item in items:
            await async_container.create_item(body=item)
        
        # Query for all items
        results = await async_container.query_items(query="SELECT * FROM c")
        assert isinstance(results, list)
        assert len(results) >= 5

    @pytest.mark.asyncio
    async def test_async_query_items_with_filter(self, async_container):
        """Test querying items with a filter asynchronously."""
        # Create items
        for i in range(10):
            item = {
                "id": f"async_filter_{i}",
                "name": f"Item {i}",
                "value": i
            }
            await async_container.create_item(body=item)
        
        # Query with filter
        results = await async_container.query_items(
            query="SELECT * FROM c WHERE c.value > 5"
        )
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_async_multiple_concurrent_operations(self, async_container):
        """Test performing multiple concurrent operations."""
        import asyncio
        
        # Create multiple items concurrently
        items = [
            {"id": f"concurrent_{i}", "name": f"Item {i}", "value": i}
            for i in range(10)
        ]
        
        create_tasks = [
            async_container.create_item(body=item)
            for item in items
        ]
        
        results = await asyncio.gather(*create_tasks)
        assert len(results) == 10
        
        # Read items concurrently
        read_tasks = [
            async_container.read_item(
                item=f"concurrent_{i}",
                partition_key=f"concurrent_{i}"
            )
            for i in range(10)
        ]
        
        read_results = await asyncio.gather(*read_tasks)
        assert len(read_results) == 10


class TestAsyncExceptionHandling:
    """Test suite for async exception handling."""

    @pytest.mark.asyncio
    async def test_async_resource_not_found(self, async_container):
        """Test ResourceNotFoundError in async operations."""
        with pytest.raises(CosmosResourceNotFoundError):
            await async_container.read_item(
                item="nonexistent",
                partition_key="nonexistent"
            )

    @pytest.mark.asyncio
    async def test_async_resource_exists(self, async_container):
        """Test ResourceExistsError in async operations."""
        item = {
            "id": "duplicate_async",
            "name": "Duplicate"
        }
        
        await async_container.create_item(body=item)
        
        with pytest.raises(CosmosResourceExistsError):
            await async_container.create_item(body=item)
