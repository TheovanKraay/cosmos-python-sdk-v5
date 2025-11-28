"""Type stubs for Azure Cosmos DB Python SDK."""

from typing import Any, Dict, List, Optional, Union, TypeVar, overload
from typing_extensions import Self

_T = TypeVar("_T")

class CosmosClient:
    """A client for interacting with Azure Cosmos DB."""
    
    def __init__(
        self,
        url: str,
        credential: Optional[Union[str, Any]] = None,
        **kwargs: Any
    ) -> None: ...
    
    def __enter__(self) -> Self: ...
    
    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any]
    ) -> bool: ...
    
    def get_database_client(self, database: str) -> DatabaseProxy:
        """Get a database client.
        
        :param str database: The database ID
        :return: A database client
        :rtype: DatabaseProxy
        """
        ...
    
    def create_database(self, id: str, **kwargs: Any) -> Dict[str, Any]:
        """Create a new database.
        
        :param str id: The database ID
        :return: Database properties
        :rtype: Dict[str, Any]
        """
        ...
    
    def delete_database(self, database: str, **kwargs: Any) -> None:
        """Delete a database.
        
        :param str database: The database ID
        """
        ...
    
    def list_databases(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List all databases.
        
        :return: List of database properties
        :rtype: List[Dict[str, Any]]
        """
        ...


class DatabaseProxy:
    """A proxy to interact with a specific database."""
    
    @property
    def id(self) -> str:
        """Get the database ID."""
        ...
    
    def get_container_client(self, container: str) -> ContainerProxy:
        """Get a container client.
        
        :param str container: The container ID
        :return: A container client
        :rtype: ContainerProxy
        """
        ...
    
    def create_container(
        self,
        id: str,
        partition_key: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Create a new container.
        
        :param str id: The container ID
        :param Dict partition_key: Partition key configuration
        :return: Container properties
        :rtype: Dict[str, Any]
        """
        ...
    
    def delete_container(self, container: str, **kwargs: Any) -> None:
        """Delete a container.
        
        :param str container: The container ID
        """
        ...
    
    def list_containers(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List all containers.
        
        :return: List of container properties
        :rtype: List[Dict[str, Any]]
        """
        ...
    
    def read(self, **kwargs: Any) -> Dict[str, Any]:
        """Read database properties.
        
        :return: Database properties
        :rtype: Dict[str, Any]
        """
        ...
    
    def delete(self, **kwargs: Any) -> None:
        """Delete this database."""
        ...


class ContainerProxy:
    """A proxy to interact with a specific container."""
    
    @property
    def id(self) -> str:
        """Get the container ID."""
        ...
    
    def create_item(self, body: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Create a new item.
        
        :param Dict body: The item to create
        :return: The created item
        :rtype: Dict[str, Any]
        """
        ...
    
    def read_item(
        self,
        item: str,
        partition_key: Union[str, int, float],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Read an item by ID and partition key.
        
        :param str item: The item ID
        :param partition_key: The partition key value
        :return: The item
        :rtype: Dict[str, Any]
        """
        ...
    
    def upsert_item(self, body: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Create or replace an item.
        
        :param Dict body: The item to upsert
        :return: The upserted item
        :rtype: Dict[str, Any]
        """
        ...
    
    def replace_item(
        self,
        item: str,
        body: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replace an existing item.
        
        :param str item: The item ID
        :param Dict body: The new item data
        :return: The replaced item
        :rtype: Dict[str, Any]
        """
        ...
    
    def delete_item(
        self,
        item: str,
        partition_key: Union[str, int, float],
        **kwargs: Any
    ) -> None:
        """Delete an item.
        
        :param str item: The item ID
        :param partition_key: The partition key value
        """
        ...
    
    def query_items(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """Query items with SQL.
        
        :param str query: SQL query string
        :return: List of matching items
        :rtype: List[Dict[str, Any]]
        """
        ...
    
    def patch_item(
        self,
        item: str,
        partition_key: Union[str, int, float],
        patch_operations: List[Dict[str, Any]],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Patch an item.
        
        :param str item: The item ID
        :param partition_key: The partition key value
        :param List patch_operations: List of patch operations
        :return: The patched item
        :rtype: Dict[str, Any]
        """
        ...
    
    def read(self, **kwargs: Any) -> Dict[str, Any]:
        """Read container properties.
        
        :return: Container properties
        :rtype: Dict[str, Any]
        """
        ...
    
    def delete(self, **kwargs: Any) -> None:
        """Delete this container."""
        ...
