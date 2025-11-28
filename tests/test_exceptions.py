"""Tests for exception handling and error cases."""

import pytest
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
    CosmosResourceNotFoundError,
    CosmosResourceExistsError,
    CosmosAccessConditionFailedError,
)


class TestExceptions:
    """Test suite for exception handling."""

    def test_exception_hierarchy(self):
        """Test that exception hierarchy is correct."""
        # ResourceNotFoundError should be a subclass of CosmosHttpResponseError
        assert issubclass(CosmosResourceNotFoundError, CosmosHttpResponseError)
        assert issubclass(CosmosResourceExistsError, CosmosHttpResponseError)
        assert issubclass(CosmosAccessConditionFailedError, CosmosHttpResponseError)

    def test_invalid_credentials_raises_error(self, account_url):
        """Test that invalid credentials raise an error."""
        client = CosmosClient(account_url, credential="invalid_key")
        
        # Should raise an error when attempting an operation
        with pytest.raises(CosmosHttpResponseError):
            client.list_databases()

    def test_read_nonexistent_database_raises_error(self, client):
        """Test reading a nonexistent database raises ResourceNotFoundError."""
        db_client = client.get_database_client("nonexistent_database_xyz")
        
        with pytest.raises(CosmosResourceNotFoundError):
            db_client.read()

    def test_read_nonexistent_container_raises_error(self, database):
        """Test reading a nonexistent container raises ResourceNotFoundError."""
        container = database.get_container_client("nonexistent_container_xyz")
        
        with pytest.raises(CosmosResourceNotFoundError):
            container.read()

    def test_create_duplicate_database_raises_error(self, client, test_database_id):
        """Test creating a duplicate database raises ResourceExistsError."""
        client.create_database(test_database_id)
        
        try:
            with pytest.raises(CosmosResourceExistsError):
                client.create_database(test_database_id)
        finally:
            client.delete_database(test_database_id)

    def test_create_duplicate_container_raises_error(self, database, test_container_id):
        """Test creating a duplicate container raises ResourceExistsError."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        database.create_container(test_container_id, partition_key)
        
        try:
            with pytest.raises(CosmosResourceExistsError):
                database.create_container(test_container_id, partition_key)
        finally:
            database.delete_container(test_container_id)

    def test_create_duplicate_item_raises_error(self, container):
        """Test creating a duplicate item raises ResourceExistsError."""
        item = {
            "id": "duplicate_item",
            "name": "Duplicate"
        }
        
        container.create_item(body=item)
        
        with pytest.raises(CosmosResourceExistsError):
            container.create_item(body=item)

    def test_read_nonexistent_item_raises_error(self, container):
        """Test reading a nonexistent item raises ResourceNotFoundError."""
        with pytest.raises(CosmosResourceNotFoundError):
            container.read_item(item="nonexistent_item", partition_key="nonexistent")

    def test_delete_nonexistent_database_raises_error(self, client):
        """Test deleting a nonexistent database raises ResourceNotFoundError."""
        with pytest.raises(CosmosResourceNotFoundError):
            client.delete_database("nonexistent_database_xyz")

    def test_delete_nonexistent_container_raises_error(self, database):
        """Test deleting a nonexistent container raises ResourceNotFoundError."""
        with pytest.raises(CosmosResourceNotFoundError):
            database.delete_container("nonexistent_container_xyz")

    def test_delete_nonexistent_item_raises_error(self, container):
        """Test deleting a nonexistent item raises ResourceNotFoundError."""
        with pytest.raises(CosmosResourceNotFoundError):
            container.delete_item(item="nonexistent_item", partition_key="nonexistent")

    def test_replace_nonexistent_item_raises_error(self, container):
        """Test replacing a nonexistent item raises ResourceNotFoundError."""
        item = {
            "id": "nonexistent",
            "name": "Does Not Exist"
        }
        
        with pytest.raises(CosmosResourceNotFoundError):
            container.replace_item(item="nonexistent", body=item)

    def test_invalid_partition_key_format(self, container):
        """Test that invalid partition key format raises appropriate error."""
        item = {
            "id": "test_item",
            "name": "Test"
        }
        
        # This should raise an error due to invalid partition key type
        with pytest.raises((TypeError, ValueError, CosmosHttpResponseError)):
            container.read_item(item="test_item", partition_key={"invalid": "dict"})

    def test_missing_required_fields(self, container):
        """Test that missing required fields raises appropriate error."""
        # Item without 'id' field
        item = {
            "name": "No ID"
        }
        
        with pytest.raises((KeyError, ValueError, CosmosHttpResponseError)):
            container.create_item(body=item)


class TestErrorMessages:
    """Test suite for error message quality."""

    def test_resource_not_found_error_message(self, container):
        """Test that ResourceNotFoundError has informative message."""
        try:
            container.read_item(item="nonexistent", partition_key="nonexistent")
        except CosmosResourceNotFoundError as e:
            error_msg = str(e)
            assert len(error_msg) > 0
            # Error message should contain useful information
            assert "404" in error_msg or "NotFound" in error_msg or "not found" in error_msg.lower()

    def test_resource_exists_error_message(self, container):
        """Test that ResourceExistsError has informative message."""
        item = {"id": "exists_test", "name": "Test"}
        container.create_item(body=item)
        
        try:
            container.create_item(body=item)
        except CosmosResourceExistsError as e:
            error_msg = str(e)
            assert len(error_msg) > 0
            # Error message should contain useful information
            assert "409" in error_msg or "Conflict" in error_msg or "exists" in error_msg.lower()


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_empty_query(self, container):
        """Test executing an empty or minimal query."""
        # Create an item first
        item = {"id": "edge_case_1", "name": "Test"}
        container.create_item(body=item)
        
        # Query with minimal SQL
        results = container.query_items(query="SELECT * FROM c")
        assert isinstance(results, list)

    def test_item_with_special_characters(self, container):
        """Test creating items with special characters."""
        item = {
            "id": "special_chars",
            "name": "Test with émojis 🎉 and spëcial çhars",
            "description": "Line1\nLine2\tTabbed"
        }
        
        result = container.create_item(body=item)
        assert result is not None
        
        # Read it back
        read_result = container.read_item(item="special_chars", partition_key="special_chars")
        assert read_result.get("name") == item["name"]

    def test_large_item(self, container):
        """Test creating a large item (within limits)."""
        # Create an item with a large string field
        large_string = "x" * 10000  # 10KB string
        item = {
            "id": "large_item",
            "data": large_string
        }
        
        result = container.create_item(body=item)
        assert result is not None

    def test_deeply_nested_json(self, container):
        """Test creating items with deeply nested JSON."""
        item = {
            "id": "nested_item",
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep_value"
                        }
                    }
                }
            }
        }
        
        result = container.create_item(body=item)
        assert result is not None
        
        # Read and verify
        read_result = container.read_item(item="nested_item", partition_key="nested_item")
        assert read_result["level1"]["level2"]["level3"]["level4"]["value"] == "deep_value"

    def test_numeric_partition_keys(self, database, test_container_id):
        """Test using numeric partition keys."""
        # Create container with numeric partition key path
        partition_key = {"paths": ["/numericKey"], "kind": "Hash"}
        database.create_container(test_container_id, partition_key)
        
        try:
            container = database.get_container_client(test_container_id)
            
            item = {
                "id": "numeric_pk_test",
                "numericKey": 12345,
                "name": "Numeric PK Test"
            }
            
            result = container.create_item(body=item, partition_key=12345)
            assert result is not None
        finally:
            database.delete_container(test_container_id)
