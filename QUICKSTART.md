# Quick Start Guide

## Installation

### Prerequisites

- **Python**: 3.8 or later
- **Rust**: 1.70 or later (install from https://rustup.rs/)
- **Git**: For cloning the repository

### Local Installation Steps

This package is currently in development and not yet published to PyPI.

```bash
# 1. Clone the repository
git clone <repository-url>
cd cosmos-python-sdk-v5

# 2. Create a virtual environment (recommended)
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 4. Install maturin (the Rust-Python build tool)
pip install maturin

# 5. Build and install the package
# For development (faster builds, includes debug symbols):
maturin develop

# OR for release (optimized builds, better performance):
maturin develop --release
```

### Verify Installation

```bash
python -c "from azure.cosmos import CosmosClient; print('Installation successful!')"
```

## Basic Usage

### 1. Initialize Client

```python
from azure.cosmos import CosmosClient

# Using account key (currently the only supported authentication method)
client = CosmosClient(
    url="https://your-account.documents.azure.com:443/",
    credential="your-account-key"
)

# For Azure Cosmos DB Emulator (local development)
client = CosmosClient(
    url="https://localhost:8081",
    credential="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
)
```

### 2. Work with Databases

```python
# Create database
database_props = client.create_database("my_database")

# Get database client
database = client.get_database_client("my_database")

# List databases
databases = client.list_databases()

# Delete database
client.delete_database("my_database")
```

### 3. Work with Containers

```python
# Create container
partition_key = {"paths": ["/category"], "kind": "Hash"}
container_props = database.create_container("my_container", partition_key)

# Get container client
container = database.get_container_client("my_container")

# List containers
containers = database.list_containers()

# Delete container
database.delete_container("my_container")
```

### 4. Work with Items

```python
# Create item
item = {
    "id": "1",
    "category": "electronics",
    "name": "Laptop",
    "price": 999.99
}
created_item = container.create_item(body=item)

# Read item
read_item = container.read_item(
    item="1",
    partition_key="electronics"
)

# Update item (upsert)
item["price"] = 899.99
updated_item = container.upsert_item(body=item)

# Replace item
new_item = {
    "id": "1",
    "category": "electronics",
    "name": "Gaming Laptop",
    "price": 1299.99
}
replaced_item = container.replace_item(item="1", body=new_item)

# Delete item
container.delete_item(item="1", partition_key="electronics")
```

### 5. Query Items

```python
# Query items (requires partition_key)
items = container.query_items(
    query="SELECT * FROM c WHERE c.price > 100",
    partition_key="electronics"  # Required for now
)

for item in items:
    print(f"{item['name']}: ${item['price']}")

# Query with WHERE clause
query = "SELECT * FROM c WHERE c.category = 'electronics' AND c.price < 1000"
items = container.query_items(
    query=query,
    partition_key="electronics"
)

# Note: Cross-partition queries (without specifying partition_key) 
# will be supported in a future update
```

## Current Limitations

### Authentication
- ✅ Key-based authentication (account key)
- ❌ Azure AD authentication (DefaultAzureCredential) - not yet implemented

### Async Support
- ❌ Async operations are not yet implemented
- All current operations are synchronous

### Query Limitations
- ✅ Partition-scoped queries (with `partition_key` parameter)
- ❌ Cross-partition queries - coming in future update
- ❌ Parameterized queries - coming in future update

### Other Features
- ❌ Batch/transactional operations - not yet implemented
- ❌ Patch operations - not yet implemented
- ❌ Change feed - not yet implemented

## Error Handling

```python
from azure.cosmos.exceptions import (
    CosmosResourceNotFoundError,
    CosmosResourceExistsError,
    CosmosHttpResponseError
)

try:
    item = container.read_item(item="999", partition_key="missing")
except CosmosResourceNotFoundError:
    print("Item not found")
except CosmosHttpResponseError as e:
    print(f"HTTP error: {e}")
```

## Context Manager

```python
# Sync
with CosmosClient(url, credential) as client:
    database = client.get_database_client("mydb")
    # ... operations ...

# Async
async with CosmosClient(url, credential) as client:
    database = client.get_database_client("mydb")
    # ... await operations ...
```

## Best Practices

### 1. Reuse Clients

```python
# Good: Reuse client across operations
client = CosmosClient(url, credential)
database = client.get_database_client("mydb")
container = database.get_container_client("mycontainer")

# Perform many operations with the same container
for item in items:
    container.create_item(body=item)
```

### 2. Provide Partition Keys Explicitly

```python
# Always provide partition_key for queries
items = container.query_items(
    query="SELECT * FROM c WHERE c.status = 'active'",
    partition_key="user_123"
)

# Partition key auto-detection works for common fields
# (category, partitionKey, pk, type, tenantId)
item = {"id": "1", "category": "electronics", "name": "Laptop"}
container.create_item(body=item)  # Auto-detects 'category' as partition key
```

### 3. Handle Exceptions Appropriately

```python
def safe_create_item(container, item):
    try:
        return container.create_item(body=item)
    except CosmosResourceExistsError:
        # Item already exists, update instead
        return container.upsert_item(body=item)
    except CosmosHttpResponseError as e:
        # Log error and handle appropriately
        logger.error(f"Failed to create item: {e}")
        raise
```

### 4. Use Proper Partition Keys

```python
# Good: Provide partition key explicitly
container.read_item(item="123", partition_key="user_123")

# Also works: Include in body for create/upsert
item = {
    "id": "123",
    "userId": "user_123",  # This is the partition key
    "data": "..."
}
container.create_item(body=item, partition_key="user_123")
```

## Common Patterns

### Bulk Insert

```python
from azure.cosmos.exceptions import CosmosResourceExistsError

def bulk_insert(container, items):
    """Insert multiple items, skipping duplicates"""
    successful = 0
    for item in items:
        try:
            container.create_item(body=item)
            successful += 1
        except CosmosResourceExistsError:
            pass  # Skip duplicates
    
    print(f"Inserted {successful}/{len(items)} items")

# Note: Async bulk operations will be much faster when async support is added
```

### Query Results

```python
# Current implementation returns all results as a list
# Note: Pagination with continuation tokens will be added in a future update

results = container.query_items(
    query="SELECT * FROM c WHERE c.type = 'important'",
    partition_key="your-partition-key"
)

print(f"Found {len(results)} items")

# Process results
for item in results:
    process(item)
```

### Batch Operations by Partition

```python
from collections import defaultdict

# Group items by partition key
items_by_partition = defaultdict(list)
for item in all_items:
    pk = item["partitionKey"]
    items_by_partition[pk].append(item)

# Process each partition
for pk, items in items_by_partition.items():
    for item in items:
        container.create_item(body=item, partition_key=pk)
```

## Environment Variables

For testing and development:

```bash
# Required for running tests
export COSMOS_ENDPOINT="https://your-account.documents.azure.com:443/"
export COSMOS_KEY="your-account-key"

# Optional: For Azure AD authentication
export AZURE_TENANT_ID="..."
export AZURE_CLIENT_ID="..."
export AZURE_CLIENT_SECRET="..."
```

## Next Steps

- See [examples/](examples/) for complete working examples
- Read [ARCHITECTURE.md](ARCHITECTURE.md) for implementation details
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Review [tests/](tests/) for comprehensive usage examples

## Getting Help

- Check existing issues on GitHub
- Review the examples in [examples/](examples/)
- Read the Azure Cosmos DB documentation
- Open a new issue for bugs or feature requests
