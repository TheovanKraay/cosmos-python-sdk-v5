"""Type stubs for async Azure Cosmos DB operations."""

from typing import Any, Dict, List, Optional, Union, TypeVar
from typing_extensions import Self

_T = TypeVar("_T")

class CosmosClient:
    """Async client for interacting with Azure Cosmos DB."""
    
    def __init__(
        self,
        url: str,
        credential: Optional[Union[str, Any]] = None,
        **kwargs: Any
    ) -> None: ...
    
    async def __aenter__(self) -> Self: ...
    
    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any]
    ) -> bool: ...
    
    def get_database_client(self, database: str) -> DatabaseProxy:
        """Get a database client."""
        ...
    
    async def create_database(self, id: str, **kwargs: Any) -> Dict[str, Any]:
        """Create a new database asynchronously."""
        ...
    
    async def delete_database(self, database: str, **kwargs: Any) -> None:
        """Delete a database asynchronously."""
        ...
    
    async def list_databases(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List all databases asynchronously."""
        ...


class DatabaseProxy:
    """Async proxy to interact with a specific database."""
    
    @property
    def id(self) -> str:
        """Get the database ID."""
        ...
    
    def get_container_client(self, container: str) -> ContainerProxy:
        """Get a container client."""
        ...
    
    async def create_container(
        self,
        id: str,
        partition_key: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Create a new container asynchronously."""
        ...
    
    async def delete_container(self, container: str, **kwargs: Any) -> None:
        """Delete a container asynchronously."""
        ...
    
    async def list_containers(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List all containers asynchronously."""
        ...
    
    async def read(self, **kwargs: Any) -> Dict[str, Any]:
        """Read database properties asynchronously."""
        ...
    
    async def delete(self, **kwargs: Any) -> None:
        """Delete this database asynchronously."""
        ...


class ContainerProxy:
    """Async proxy to interact with a specific container."""
    
    @property
    def id(self) -> str:
        """Get the container ID."""
        ...
    
    async def create_item(self, body: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Create a new item asynchronously."""
        ...
    
    async def read_item(
        self,
        item: str,
        partition_key: Union[str, int, float],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Read an item asynchronously."""
        ...
    
    async def upsert_item(self, body: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Upsert an item asynchronously."""
        ...
    
    async def replace_item(
        self,
        item: str,
        body: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replace an item asynchronously."""
        ...
    
    async def delete_item(
        self,
        item: str,
        partition_key: Union[str, int, float],
        **kwargs: Any
    ) -> None:
        """Delete an item asynchronously."""
        ...
    
    async def query_items(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """Query items asynchronously."""
        ...
    
    async def patch_item(
        self,
        item: str,
        partition_key: Union[str, int, float],
        patch_operations: List[Dict[str, Any]],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Patch an item asynchronously."""
        ...
    
    async def read(self, **kwargs: Any) -> Dict[str, Any]:
        """Read container properties asynchronously."""
        ...
    
    async def delete(self, **kwargs: Any) -> None:
        """Delete this container asynchronously."""
        ...
