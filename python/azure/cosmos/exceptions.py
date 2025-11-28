"""Exception classes for Azure Cosmos DB."""

from azure.cosmos._rust import (
    CosmosHttpResponseError,
    CosmosResourceNotFoundError,
    CosmosResourceExistsError,
    CosmosAccessConditionFailedError,
)

__all__ = [
    "CosmosHttpResponseError",
    "CosmosResourceNotFoundError",
    "CosmosResourceExistsError",
    "CosmosAccessConditionFailedError",
]
