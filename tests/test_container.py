"""Tests for Container item operations."""

import pytest
from azure.cosmos.exceptions import (
    CosmosResourceNotFoundError,
    CosmosResourceExistsError,
)


class TestContainerItemOperations:
    """Test suite for container item CRUD operations."""

    def test_create_item(self, container):
        """Test creating an item."""
        item = {
            "id": "test_item_1",
            "name": "Test Item",
            "category": "Test Category"
        }
        
        result = container.create_item(body=item)
        assert result is not None
        assert result.get("id") == item["id"]

    def test_create_item_with_partition_key(self, container):
        """Test creating an item with explicit partition key."""
        item = {
            "id": "test_item_2",
            "name": "Test Item 2",
            "category": "Category2"
        }
        
        result = container.create_item(body=item, partition_key="test_item_2")
        assert result is not None
        assert result.get("id") == item["id"]

    def test_create_duplicate_item_raises_error(self, container):
        """Test that creating a duplicate item raises an error."""
        item = {
            "id": "test_item_dup",
            "name": "Duplicate Item"
        }
        
        container.create_item(body=item)
        
        with pytest.raises(CosmosResourceExistsError):
            container.create_item(body=item)

    def test_read_item(self, container):
        """Test reading an item."""
        item = {
            "id": "test_item_read",
            "name": "Read Test",
            "value": 42
        }
        
        container.create_item(body=item)
        
        result = container.read_item(item="test_item_read", partition_key="test_item_read")
        assert result is not None
        assert result.get("id") == item["id"]
        assert result.get("name") == item["name"]
        assert result.get("value") == item["value"]

    def test_read_nonexistent_item_raises_error(self, container):
        """Test that reading a nonexistent item raises an error."""
        with pytest.raises(CosmosResourceNotFoundError):
            container.read_item(item="nonexistent_item", partition_key="nonexistent")

    def test_upsert_item_create(self, container):
        """Test upserting a new item (create)."""
        item = {
            "id": "test_item_upsert_new",
            "name": "Upsert New",
            "value": 100
        }
        
        result = container.upsert_item(body=item)
        assert result is not None
        assert result.get("id") == item["id"]

    def test_upsert_item_update(self, container):
        """Test upserting an existing item (update)."""
        item = {
            "id": "test_item_upsert_update",
            "name": "Original",
            "value": 1
        }
        
        container.create_item(body=item)
        
        # Update the item
        item["name"] = "Updated"
        item["value"] = 2
        
        result = container.upsert_item(body=item)
        assert result is not None
        assert result.get("name") == "Updated"
        assert result.get("value") == 2

    def test_replace_item(self, container):
        """Test replacing an item."""
        item = {
            "id": "test_item_replace",
            "name": "Original",
            "value": 1
        }
        
        container.create_item(body=item)
        
        # Replace the item
        new_item = {
            "id": "test_item_replace",
            "name": "Replaced",
            "value": 99
        }
        
        result = container.replace_item(item="test_item_replace", body=new_item)
        assert result is not None
        assert result.get("name") == "Replaced"
        assert result.get("value") == 99

    def test_replace_nonexistent_item_raises_error(self, container):
        """Test that replacing a nonexistent item raises an error."""
        item = {
            "id": "nonexistent",
            "name": "Does Not Exist"
        }
        
        with pytest.raises(CosmosResourceNotFoundError):
            container.replace_item(item="nonexistent", body=item)

    def test_delete_item(self, container):
        """Test deleting an item."""
        item = {
            "id": "test_item_delete",
            "name": "To Be Deleted"
        }
        
        container.create_item(body=item)
        
        container.delete_item(item="test_item_delete", partition_key="test_item_delete")
        
        # Verify deletion
        with pytest.raises(CosmosResourceNotFoundError):
            container.read_item(item="test_item_delete", partition_key="test_item_delete")

    def test_delete_nonexistent_item_raises_error(self, container):
        """Test that deleting a nonexistent item raises an error."""
        with pytest.raises(CosmosResourceNotFoundError):
            container.delete_item(item="nonexistent", partition_key="nonexistent")

    def test_query_items(self, container):
        """Test querying items."""
        # Create multiple items
        items = [
            {"id": f"query_test_{i}", "name": f"Item {i}", "value": i}
            for i in range(5)
        ]
        
        for item in items:
            container.create_item(body=item)
        
        # Query for all items
        results = container.query_items(query="SELECT * FROM c")
        assert isinstance(results, list)
        assert len(results) >= 5

    def test_query_items_with_filter(self, container):
        """Test querying items with a filter."""
        # Create items with different values
        for i in range(10):
            item = {
                "id": f"filter_test_{i}",
                "name": f"Item {i}",
                "value": i
            }
            container.create_item(body=item)
        
        # Query for items where value > 5
        results = container.query_items(query="SELECT * FROM c WHERE c.value > 5")
        assert isinstance(results, list)
        
        # Verify results
        for result in results:
            if "value" in result:
                assert result["value"] > 5

    def test_query_items_with_projection(self, container):
        """Test querying items with field projection."""
        item = {
            "id": "projection_test",
            "name": "Projection Test",
            "value": 42,
            "extra_field": "extra"
        }
        
        container.create_item(body=item)
        
        # Query with projection
        results = container.query_items(
            query="SELECT c.id, c.name FROM c WHERE c.id = 'projection_test'"
        )
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_multiple_items_operations(self, container):
        """Test creating, reading, updating, and deleting multiple items."""
        # Create multiple items
        for i in range(5):
            item = {
                "id": f"multi_{i}",
                "name": f"Multi Item {i}",
                "value": i * 10
            }
            container.create_item(body=item)
        
        # Read each item
        for i in range(5):
            result = container.read_item(item=f"multi_{i}", partition_key=f"multi_{i}")
            assert result.get("value") == i * 10
        
        # Update items
        for i in range(5):
            item = {
                "id": f"multi_{i}",
                "name": f"Updated Multi Item {i}",
                "value": i * 20
            }
            container.upsert_item(body=item)
        
        # Verify updates
        for i in range(5):
            result = container.read_item(item=f"multi_{i}", partition_key=f"multi_{i}")
            assert result.get("value") == i * 20
        
        # Delete items
        for i in range(5):
            container.delete_item(item=f"multi_{i}", partition_key=f"multi_{i}")


class TestContainerProxy:
    """Test suite for ContainerProxy."""

    def test_container_id_property(self, container):
        """Test container ID property."""
        assert container.id is not None
        assert isinstance(container.id, str)

    def test_read_container(self, container):
        """Test reading container properties."""
        result = container.read()
        assert result is not None
        assert result.get("id") == container.id

    def test_delete_container(self, database, test_container_id):
        """Test deleting a container through the container proxy."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        database.create_container(test_container_id, partition_key)
        
        container = database.get_container_client(test_container_id)
        container.delete()
        
        # Verify deletion
        with pytest.raises(CosmosResourceNotFoundError):
            container.read()
