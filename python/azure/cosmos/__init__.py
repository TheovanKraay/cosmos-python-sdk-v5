"""Azure Cosmos DB Python SDK v5 - Rust-powered native extension."""

from azure.cosmos._rust import (
    CosmosClient as _RustCosmosClient,
    DatabaseClient as _RustDatabaseClient,
    ContainerClient as _RustContainerClient,
)
from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
    CosmosResourceNotFoundError,
    CosmosResourceExistsError,
    CosmosAccessConditionFailedError,
)

__all__ = [
    "CosmosClient",
    "DatabaseProxy",
    "ContainerProxy",
    "CosmosHttpResponseError",
    "CosmosResourceNotFoundError",
    "CosmosResourceExistsError",
    "CosmosAccessConditionFailedError",
]

__version__ = "5.0.0"


class CosmosClient:
    """A client for interacting with Azure Cosmos DB.
    
    :param str url: The URL of the Cosmos DB account
    :param credential: The credential for authentication (key string or credential object)
    :param kwargs: Additional keyword arguments
    """
    
    def __init__(self, url: str, credential=None, **kwargs):
        self._client = _RustCosmosClient(url, credential, **kwargs)
    
    def get_database_client(self, database: str) -> "DatabaseProxy":
        """Get a database client.
        
        :param str database: The database ID
        :return: A database client
        :rtype: DatabaseProxy
        """
        db_client = self._client.get_database_client(database)
        return DatabaseProxy(db_client)
    
    def create_database(self, id: str, **kwargs) -> dict:
        """Create a new database.
        
        :param str id: The database ID
        :return: Database properties
        :rtype: dict
        """
        return self._client.create_database(id, **kwargs)
    
    def delete_database(self, database: str, **kwargs) -> None:
        """Delete a database.
        
        :param str database: The database ID
        """
        return self._client.delete_database(database, **kwargs)
    
    def list_databases(self, **kwargs) -> list:
        """List all databases.
        
        :return: List of database properties
        :rtype: list[dict]
        """
        return self._client.list_databases(**kwargs)


class DatabaseProxy:
    """A proxy to interact with a specific database.
    
    :param _RustDatabaseClient client: The underlying Rust database client
    """
    
    def __init__(self, client: _RustDatabaseClient):
        self._client = client
    
    @property
    def id(self) -> str:
        """Get the database ID."""
        return self._client.id
    
    def get_container_client(self, container: str) -> "ContainerProxy":
        """Get a container client.
        
        :param str container: The container ID
        :return: A container client
        :rtype: ContainerProxy
        """
        container_client = self._client.get_container_client(container)
        return ContainerProxy(container_client)
    
    def create_container(self, id: str, partition_key: dict, **kwargs) -> dict:
        """Create a new container.
        
        :param str id: The container ID
        :param dict partition_key: Partition key configuration with 'paths' key
        :return: Container properties
        :rtype: dict
        """
        return self._client.create_container(id, partition_key, **kwargs)
    
    def delete_container(self, container: str, **kwargs) -> None:
        """Delete a container.
        
        :param str container: The container ID
        """
        return self._client.delete_container(container, **kwargs)
    
    def list_containers(self, **kwargs) -> list:
        """List all containers in this database.
        
        :return: List of container properties
        :rtype: list[dict]
        """
        return self._client.list_containers(**kwargs)
    
    def read(self, **kwargs) -> dict:
        """Read database properties.
        
        :return: Database properties
        :rtype: dict
        """
        return self._client.read(**kwargs)
    
    def delete(self, **kwargs) -> None:
        """Delete this database."""
        return self._client.delete(**kwargs)


class ContainerProxy:
    """A proxy to interact with a specific container.
    
    :param _RustContainerClient client: The underlying Rust container client
    """
    
    def __init__(self, client: _RustContainerClient):
        self._client = client
    
    @property
    def id(self) -> str:
        """Get the container ID."""
        return self._client.id
    
    def create_item(self, body: dict, **kwargs) -> dict:
        """Create a new item.
        
        :param dict body: The item to create
        :return: The created item
        :rtype: dict
        """
        return self._client.create_item(body, **kwargs)
    
    def read_item(self, item: str, partition_key, **kwargs) -> dict:
        """Read an item by ID and partition key.
        
        :param str item: The item ID
        :param partition_key: The partition key value
        :return: The item
        :rtype: dict
        """
        return self._client.read_item(item, partition_key, **kwargs)
    
    def upsert_item(self, body: dict, **kwargs) -> dict:
        """Create or replace an item.
        
        :param dict body: The item to upsert
        :return: The upserted item
        :rtype: dict
        """
        return self._client.upsert_item(body, **kwargs)
    
    def replace_item(self, item: str, body: dict, **kwargs) -> dict:
        """Replace an existing item.
        
        :param str item: The item ID
        :param dict body: The new item data
        :return: The replaced item
        :rtype: dict
        """
        return self._client.replace_item(item, body, **kwargs)
    
    def delete_item(self, item: str, partition_key, **kwargs) -> None:
        """Delete an item.
        
        :param str item: The item ID
        :param partition_key: The partition key value
        """
        return self._client.delete_item(item, partition_key, **kwargs)
    
    def query_items(self, query: str, **kwargs) -> list:
        """Query items with SQL.
        
        :param str query: SQL query string
        :return: List of matching items
        :rtype: list[dict]
        """
        return self._client.query_items(query, **kwargs)
    
    def patch_item(self, item: str, partition_key, patch_operations: list, **kwargs) -> dict:
        """Patch an item.
        
        :param str item: The item ID
        :param partition_key: The partition key value
        :param list patch_operations: List of patch operations
        :return: The patched item
        :rtype: dict
        """
        return self._client.patch_item(item, partition_key, patch_operations, **kwargs)
    
    def read(self, **kwargs) -> dict:
        """Read container properties.
        
        :return: Container properties
        :rtype: dict
        """
        return self._client.read(**kwargs)
    
    def delete(self, **kwargs) -> None:
        """Delete this container."""
        return self._client.delete(**kwargs)
