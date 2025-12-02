# Cosmos DB SDK Benchmarks

This directory contains performance benchmarks comparing the V4 (pure Python) SDK with the V5 (Rust-based) SDK.

## Overview

The benchmark suite:
- Creates separate virtual environments for V4 and V5 SDKs
- Runs identical high-volume tests on both
- Compares performance metrics
- Generates detailed comparison reports

## Prerequisites

- Python 3.8+
- Rust 1.70+ (for building V5 SDK)
- Azure Cosmos DB Emulator or an Azure Cosmos DB account
- Environment variables set:
  ```bash
  $env:COSMOS_ENDPOINT = "https://localhost:8081"
  $env:COSMOS_KEY = "your-key-here"
  ```

## Running Benchmarks

### Quick Start

```bash
# From the repository root
python benchmarks/benchmark_runner.py
```

This will:
1. Create `benchmarks/venv_v4` and install V4 SDK from PyPI
2. Create `benchmarks/venv_v5` and build/install V5 SDK locally
3. Run all benchmark tests in both environments
4. Display comparison results
5. Save detailed results to `benchmarks/benchmark_results.json`

### Manual Run

If you want to run benchmarks manually:

```bash
# Setup V4 environment
python -m venv benchmarks/venv_v4
benchmarks/venv_v4/Scripts/activate  # Windows
pip install azure-cosmos==4.7.0

# Run V4 benchmark
$env:SDK_VERSION="v4"
python benchmarks/benchmark_tests.py

# Setup V5 environment
python -m venv benchmarks/venv_v5
benchmarks/venv_v5/Scripts/activate  # Windows
pip install maturin
maturin develop --release

# Run V5 benchmark
$env:SDK_VERSION="v5"
python benchmarks/benchmark_tests.py
```

## Benchmark Tests

### 1. Create Items (1000 items)
Creates 1000 documents across 10 partitions with realistic data.

### 2. Read Items (1000 reads)
Point reads by ID and partition key.

### 3. Query Items (10 partition queries)
Queries across 10 different partitions.

### 4. Upsert Items (500 items)
Mix of creates and updates using upsert.

### 5. Replace Items (300 items)
Read and replace existing items.

### 6. Delete Items (200 items)
Delete items by ID and partition key.

### 7. Mixed Workload (500 operations)
Realistic workload with 40% creates, 30% reads, 20% updates, 10% deletes.

## Sample Output

```
======================================================================
BENCHMARK RESULTS COMPARISON
======================================================================

Operation                      V4 (Python)          V5 (Rust)            Speedup        
-------------------------------------------------------------------------------------
create_items_1000                      12.3450s            8.1234s      🚀 1.52x
read_items_1000                         8.9012s            5.2341s      🚀 1.70x
query_items_10_partitions               2.1234s            1.3456s      🚀 1.58x
upsert_items_500                        6.7890s            4.2345s      🚀 1.60x
replace_items_300                       5.4321s            3.1234s      🚀 1.74x
delete_items_200                        3.2109s            1.9876s      🚀 1.62x
mixed_workload_500                      7.6543s            4.8765s      🚀 1.57x
-------------------------------------------------------------------------------------
TOTAL                                  46.4559s           28.9251s           1.61x

🎉 V5 (Rust) is 1.61x faster overall!
```

## Results File

Detailed results are saved to `benchmark_results.json` with structure:

```json
{
  "v4_results": { ... },
  "v5_results": { ... },
  "comparison": {
    "create_items_1000": {
      "v4_time": 12.345,
      "v5_time": 8.1234,
      "speedup": 1.52,
      "v4_ops_per_sec": 81.0,
      "v5_ops_per_sec": 123.1
    },
    ...
  },
  "summary": {
    "total_v4_time": 46.4559,
    "total_v5_time": 28.9251,
    "overall_speedup": 1.61
  },
  "timestamp": "2025-12-02 10:30:45"
}
```

## Customizing Benchmarks

Edit `benchmark_tests.py` to:
- Adjust number of operations (e.g., change `num_items=1000` to `num_items=5000`)
- Add new benchmark functions
- Modify data patterns
- Change partition distribution

## Performance Tips

### For V5 SDK
- Use `maturin develop --release` for optimized builds
- The first run may include JIT compilation overhead

### For Both SDKs
- Use the emulator for consistent testing
- Close other applications to reduce noise
- Run multiple times and average results
- Test with different data sizes and patterns

## Troubleshooting

**Virtual environment creation fails:**
- Ensure Python 3.8+ is installed
- Check you have write permissions to the benchmarks directory

**V5 build fails:**
- Verify Rust 1.70+ is installed (`rustc --version`)
- Ensure you're in the repository root
- Check that Cargo.toml and src/ are present

**Benchmark fails with connection error:**
- Verify Cosmos DB Emulator is running
- Check environment variables are set correctly
- Test connection with a simple script first

**Results seem inconsistent:**
- Run benchmarks multiple times
- Close unnecessary applications
- Check system resource usage
- Use release build for V5 (`--release` flag)

## Contributing

To add new benchmarks:
1. Add a new function to `benchmark_tests.py`
2. Follow the naming convention `benchmark_<operation>_<details>`
3. Return a dict with `total_time`, count, and `ops_per_sec`
4. Add the benchmark call to `run_all_benchmarks()`

## Notes

- Benchmarks use the same database/container setup for both SDKs
- Each test cleans up after itself
- Results may vary based on:
  - Network latency (emulator vs cloud)
  - System resources
  - Data size and complexity
  - Number of partitions
