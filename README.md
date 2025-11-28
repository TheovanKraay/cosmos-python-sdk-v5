# Azure Cosmos DB Python SDK v5

Native Python module for Azure Cosmos DB, built in Rust using the Azure Cosmos DB Rust SDK.

## Features

- Full API compatibility with existing Python SDK
- Native Rust implementation for better performance
- Async/await support
- Type hints and comprehensive documentation
- Same exception model as existing SDK

## Installation

### Prerequisites

- Python 3.8 or later
- Rust 1.70 or later (install from https://rustup.rs/)
- Maturin build tool

### Local Installation

This package is currently in development and not published to PyPI. Install it locally:

```bash
# Clone the repository
git clone <repository-url>
cd cosmos-python-sdk-v5

# Create and activate a virtual environment (recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install maturin
pip install maturin

# Build and install the package in development mode
maturin develop

# Or for release build:
maturin develop --release
```

## Quick Start

```python
from azure.cosmos import CosmosClient

# Initialize client
client = CosmosClient(url="https://your-account.documents.azure.com:443/", credential="your-key")

# Get database and container clients
database = client.get_database_client("your-database")
container = database.get_container_client("your-container")

# Create an item
item = {"id": "1", "name": "Product 1", "category": "Electronics"}
container.create_item(body=item)

# Read an item
result = container.read_item(item="1", partition_key="Electronics")
print(result)
```

## Current Limitations

- **Authentication**: Only key-based authentication is currently supported. Azure AD authentication (DefaultAzureCredential) is not yet available.
- **Async Support**: Async operations are not yet implemented. All operations are synchronous.
- **Cross-Partition Queries**: Queries require an explicit `partition_key` parameter. Cross-partition queries will be supported in a future update.
- **Batch Operations**: Batch/transactional operations are not yet implemented.

## Testing with Emulator

The SDK works with the Azure Cosmos DB Emulator:

```bash
# Set environment variables
$env:COSMOS_ENDPOINT = "https://localhost:8081"
$env:COSMOS_KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

# Run tests
python test_emulator.py
python test_comprehensive.py
```

## Running Tests

```bash
# Basic emulator test
python test_emulator.py

# Comprehensive test suite
python test_comprehensive.py

# API compatibility test
python test_v4_compatibility.py
```

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed test results.

## License

MIT
