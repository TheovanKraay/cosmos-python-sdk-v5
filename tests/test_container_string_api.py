"""Tests for Container item operations using JSON string API (optimized path)."""

import pytest
import json
from azure.cosmos.exceptions import (
    CosmosResourceNotFoundError,
    CosmosResourceExistsError,
)


class TestContainerStringAPI:
    """Test suite for container item operations using JSON strings instead of dicts."""

    def test_create_item_with_string(self, container):
        """Test creating an item using JSON string."""
        item = {
            "id": "test_string_1",
            "name": "Test String Item",
            "category": "String Test"
        }
        item_json = json.dumps(item)
        
        # String input requires partition_key in kwargs
        result = container.create_item(body=item_json, partition_key="test_string_1")
        assert result is not None
        assert result.get("id") == item["id"]
        assert result.get("name") == item["name"]

    def test_create_item_string_without_partition_key_raises_error(self, container):
        """Test that creating with string body but no partition key fails."""
        item_json = json.dumps({"id": "test_no_pk", "name": "No PK"})
        
        with pytest.raises(ValueError, match="Partition key must be provided"):
            container.create_item(body=item_json)

    def test_upsert_item_with_string(self, container):
        """Test upserting an item using JSON string."""
        item = {
            "id": "test_upsert_string",
            "name": "Upsert String",
            "value": 42
        }
        item_json = json.dumps(item)
        
        # Create
        result = container.upsert_item(body=item_json, partition_key="test_upsert_string")
        assert result.get("id") == item["id"]
        
        # Update
        updated_item = {
            "id": "test_upsert_string",
            "name": "Upsert String Updated",
            "value": 100
        }
        updated_json = json.dumps(updated_item)
        result = container.upsert_item(body=updated_json, partition_key="test_upsert_string")
        assert result.get("value") == 100

    def test_replace_item_with_string(self, container):
        """Test replacing an item using JSON string."""
        item = {
            "id": "test_replace_string",
            "name": "Original",
            "category": "original"
        }
        container.create_item(body=item)
        
        # Replace with string
        updated_item = {
            "id": "test_replace_string",
            "name": "Replaced",
            "category": "updated"
        }
        updated_json = json.dumps(updated_item)
        
        result = container.replace_item(
            item="test_replace_string",
            body=updated_json,
            partition_key="test_replace_string"
        )
        assert result.get("name") == "Replaced"
        assert result.get("category") == "updated"

    def test_mixed_dict_and_string_operations(self, container):
        """Test that dict and string operations can be mixed."""
        # Create with dict
        dict_item = {
            "id": "mixed_test_1",
            "name": "Created with dict",
            "category": "mixed"
        }
        result1 = container.create_item(body=dict_item)
        assert result1.get("id") == "mixed_test_1"
        
        # Create with string
        string_item = {
            "id": "mixed_test_2",
            "name": "Created with string",
            "category": "mixed"
        }
        result2 = container.create_item(
            body=json.dumps(string_item),
            partition_key="mixed_test_2"
        )
        assert result2.get("id") == "mixed_test_2"
        
        # Read both
        read1 = container.read_item(item="mixed_test_1", partition_key="mixed_test_1")
        read2 = container.read_item(item="mixed_test_2", partition_key="mixed_test_2")
        assert read1.get("name") == "Created with dict"
        assert read2.get("name") == "Created with string"

    def test_string_with_complex_json(self, container):
        """Test string API with complex nested JSON."""
        complex_item = {
            "id": "complex_json",
            "name": "Complex Item",
            "metadata": {
                "tags": ["test", "complex", "nested"],
                "properties": {
                    "key1": "value1",
                    "key2": 123,
                    "key3": True
                }
            },
            "numbers": [1, 2, 3, 4, 5]
        }
        complex_json = json.dumps(complex_item)
        
        result = container.create_item(body=complex_json, partition_key="complex_json")
        assert result.get("id") == "complex_json"
        assert "metadata" in result
        assert result["metadata"]["tags"] == ["test", "complex", "nested"]
        assert result["metadata"]["properties"]["key2"] == 123

    def test_string_api_error_handling(self, container):
        """Test that invalid JSON strings are properly rejected."""
        invalid_json = "{'id': 'bad_json', 'name': 'Invalid'}"  # Single quotes, not valid JSON
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            container.create_item(body=invalid_json, partition_key="bad")
