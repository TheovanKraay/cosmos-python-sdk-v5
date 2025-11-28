"""Type stubs for exceptions."""

class CosmosHttpResponseError(Exception):
    """Base exception for Cosmos DB HTTP response errors."""
    ...

class CosmosResourceNotFoundError(CosmosHttpResponseError):
    """Exception raised when a resource is not found (404)."""
    ...

class CosmosResourceExistsError(CosmosHttpResponseError):
    """Exception raised when a resource already exists (409)."""
    ...

class CosmosAccessConditionFailedError(CosmosHttpResponseError):
    """Exception raised when an access condition fails (412)."""
    ...
