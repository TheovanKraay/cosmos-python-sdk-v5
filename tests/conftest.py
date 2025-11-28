"""Test configuration and fixtures for Azure Cosmos DB tests."""

import os
import pytest
from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient


@pytest.fixture(scope="session")
def account_url():
    """Get the Cosmos DB account URL from environment."""
    url = os.environ.get("COSMOS_ENDPOINT")
    if not url:
        pytest.skip("COSMOS_ENDPOINT environment variable not set")
    return url


@pytest.fixture(scope="session")
def account_key():
    """Get the Cosmos DB account key from environment."""
    key = os.environ.get("COSMOS_KEY")
    if not key:
        pytest.skip("COSMOS_KEY environment variable not set")
    return key


@pytest.fixture(scope="session")
def client(account_url, account_key):
    """Create a sync Cosmos DB client."""
    return CosmosClient(account_url, credential=account_key)


@pytest.fixture(scope="session")
def async_client(account_url, account_key):
    """Create an async Cosmos DB client."""
    return AsyncCosmosClient(account_url, credential=account_key)


@pytest.fixture(scope="function")
def test_database_id():
    """Generate a unique database ID for testing."""
    import uuid
    return f"test_db_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="function")
def test_container_id():
    """Generate a unique container ID for testing."""
    import uuid
    return f"test_container_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="function")
def database(client, test_database_id):
    """Create a test database and clean up after test."""
    db = client.create_database(test_database_id)
    db_client = client.get_database_client(test_database_id)
    
    yield db_client
    
    # Cleanup
    try:
        client.delete_database(test_database_id)
    except Exception:
        pass


@pytest.fixture(scope="function")
async def async_database(async_client, test_database_id):
    """Create an async test database and clean up after test."""
    await async_client.create_database(test_database_id)
    db_client = async_client.get_database_client(test_database_id)
    
    yield db_client
    
    # Cleanup
    try:
        await async_client.delete_database(test_database_id)
    except Exception:
        pass


@pytest.fixture(scope="function")
def container(database, test_container_id):
    """Create a test container and clean up after test."""
    partition_key = {"paths": ["/id"], "kind": "Hash"}
    container_props = database.create_container(
        test_container_id,
        partition_key
    )
    container_client = database.get_container_client(test_container_id)
    
    yield container_client
    
    # Cleanup
    try:
        database.delete_container(test_container_id)
    except Exception:
        pass


@pytest.fixture(scope="function")
async def async_container(async_database, test_container_id):
    """Create an async test container and clean up after test."""
    partition_key = {"paths": ["/id"], "kind": "Hash"}
    await async_database.create_container(test_container_id, partition_key)
    container_client = async_database.get_container_client(test_container_id)
    
    yield container_client
    
    # Cleanup
    try:
        await async_database.delete_container(test_container_id)
    except Exception:
        pass
