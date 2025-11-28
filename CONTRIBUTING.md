# Contributing to Azure Cosmos DB Python SDK v5

Thank you for your interest in contributing!

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Rust 1.70 or higher
- Cargo
- Maturin

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd cosmos-python-sdk-v5
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install Maturin:
```bash
pip install maturin
```

4. Build the extension in development mode:
```bash
maturin develop
```

5. Install development dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov black mypy ruff
```

## Building

### Development Build

```bash
maturin develop
```

### Release Build

```bash
maturin build --release
```

## Testing

### Prerequisites

Set environment variables for testing:
```bash
export COSMOS_ENDPOINT="https://your-account.documents.azure.com:443/"
export COSMOS_KEY="your-account-key"
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_client.py

# Run with coverage
pytest --cov=azure.cosmos --cov-report=html
```

## Code Quality

### Formatting

```bash
black python/
```

### Linting

```bash
ruff check python/
```

### Type Checking

```bash
mypy python/
```

## Rust Development

The Rust code is located in `src/`. When modifying Rust code:

1. Make your changes
2. Run `cargo fmt` to format
3. Run `cargo clippy` to lint
4. Rebuild with `maturin develop`
5. Run tests to verify

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Code of Conduct

Please be respectful and constructive in all interactions.

## License

This project is licensed under the MIT License.
