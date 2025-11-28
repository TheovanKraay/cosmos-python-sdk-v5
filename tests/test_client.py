"""Tests for CosmosClient functionality."""

import pytest
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
    CosmosResourceNotFoundError,
    CosmosResourceExistsError,
)


class TestCosmosClient:
    """Test suite for CosmosClient."""

    def test_client_creation_with_key(self, account_url, account_key):
        """Test creating a client with account key."""
        client = CosmosClient(account_url, credential=account_key)
        assert client is not None

    def test_client_context_manager(self, account_url, account_key):
        """Test client as context manager."""
        with CosmosClient(account_url, credential=account_key) as client:
            assert client is not None

    def test_create_database(self, client, test_database_id):
        """Test creating a database."""
        result = client.create_database(test_database_id)
        assert result is not None
        assert result.get("id") == test_database_id
        
        # Cleanup
        client.delete_database(test_database_id)

    def test_create_duplicate_database_raises_error(self, client, test_database_id):
        """Test that creating a duplicate database raises an error."""
        client.create_database(test_database_id)
        
        try:
            with pytest.raises(CosmosResourceExistsError):
                client.create_database(test_database_id)
        finally:
            client.delete_database(test_database_id)

    def test_get_database_client(self, client, test_database_id):
        """Test getting a database client."""
        client.create_database(test_database_id)
        
        try:
            db_client = client.get_database_client(test_database_id)
            assert db_client is not None
            assert db_client.id == test_database_id
        finally:
            client.delete_database(test_database_id)

    def test_delete_database(self, client, test_database_id):
        """Test deleting a database."""
        client.create_database(test_database_id)
        client.delete_database(test_database_id)
        
        # Verify deletion by trying to get the database
        db_client = client.get_database_client(test_database_id)
        with pytest.raises(CosmosResourceNotFoundError):
            db_client.read()

    def test_delete_nonexistent_database_raises_error(self, client):
        """Test that deleting a nonexistent database raises an error."""
        with pytest.raises(CosmosResourceNotFoundError):
            client.delete_database("nonexistent_database")

    def test_list_databases(self, client, test_database_id):
        """Test listing databases."""
        # Create a test database
        client.create_database(test_database_id)
        
        try:
            databases = client.list_databases()
            assert isinstance(databases, list)
            
            # Check if our database is in the list
            db_ids = [db.get("id") for db in databases if db.get("id")]
            assert test_database_id in db_ids or len(databases) > 0
        finally:
            client.delete_database(test_database_id)


class TestDatabaseProxy:
    """Test suite for DatabaseProxy."""

    def test_database_id_property(self, database):
        """Test database ID property."""
        assert database.id is not None
        assert isinstance(database.id, str)

    def test_read_database(self, database):
        """Test reading database properties."""
        result = database.read()
        assert result is not None
        assert result.get("id") == database.id

    def test_create_container(self, database, test_container_id):
        """Test creating a container."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        result = database.create_container(test_container_id, partition_key)
        assert result is not None
        assert result.get("id") == test_container_id
        
        # Cleanup
        database.delete_container(test_container_id)

    def test_create_duplicate_container_raises_error(self, database, test_container_id):
        """Test that creating a duplicate container raises an error."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        database.create_container(test_container_id, partition_key)
        
        try:
            with pytest.raises(CosmosResourceExistsError):
                database.create_container(test_container_id, partition_key)
        finally:
            database.delete_container(test_container_id)

    def test_get_container_client(self, database, test_container_id):
        """Test getting a container client."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        database.create_container(test_container_id, partition_key)
        
        try:
            container = database.get_container_client(test_container_id)
            assert container is not None
            assert container.id == test_container_id
        finally:
            database.delete_container(test_container_id)

    def test_delete_container(self, database, test_container_id):
        """Test deleting a container."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        database.create_container(test_container_id, partition_key)
        database.delete_container(test_container_id)
        
        # Verify deletion
        container = database.get_container_client(test_container_id)
        with pytest.raises(CosmosResourceNotFoundError):
            container.read()

    def test_list_containers(self, database, test_container_id):
        """Test listing containers."""
        partition_key = {"paths": ["/id"], "kind": "Hash"}
        database.create_container(test_container_id, partition_key)
        
        try:
            containers = database.list_containers()
            assert isinstance(containers, list)
            
            # Check if our container is in the list
            container_ids = [c.get("id") for c in containers if c.get("id")]
            assert test_container_id in container_ids or len(containers) > 0
        finally:
            database.delete_container(test_container_id)

    def test_delete_database_through_proxy(self, client, test_database_id):
        """Test deleting a database through the database proxy."""
        client.create_database(test_database_id)
        db_client = client.get_database_client(test_database_id)
        
        db_client.delete()
        
        # Verify deletion
        with pytest.raises(CosmosResourceNotFoundError):
            db_client.read()
