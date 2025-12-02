"""
Quick benchmark runner - runs a single quick test for sanity checking
"""
import os
import sys
import time
from pathlib import Path

# Add parent directory to path to import from benchmarks
sys.path.insert(0, str(Path(__file__).parent))

from benchmark_tests import (
    get_client,
    setup_database_and_container,
    cleanup_database,
    benchmark_create_items,
    benchmark_read_items,
    benchmark_query_items
)

def quick_benchmark():
    """Run a quick benchmark with smaller dataset"""
    print("\n" + "="*70)
    print("QUICK BENCHMARK - Fast sanity check")
    print("="*70 + "\n")
    
    try:
        from azure.cosmos import CosmosClient
        print("✅ Cosmos SDK imported successfully")
        
        # Try to detect SDK version
        sdk_version = "unknown"
        try:
            import azure_cosmos_rust
            sdk_version = "V5 (Rust-based)"
        except ImportError:
            sdk_version = "V4 (Pure Python)"
        
        print(f"📦 SDK Version: {sdk_version}\n")
        
    except ImportError as e:
        print(f"❌ Failed to import SDK: {e}")
        return
    
    client = get_client()
    database, container = setup_database_and_container(
        client, 
        db_name="quick_benchmark_db",
        container_name="quick_benchmark_container"
    )
    
    print("Running quick tests (100 operations each)...\n")
    
    # Create
    print("1️⃣  Creating 100 items...", end=" ", flush=True)
    result = benchmark_create_items(container, num_items=100)
    print(f"✅ {result['total_time']:.3f}s ({result['ops_per_sec']:.1f} ops/sec)")
    
    # Read
    print("2️⃣  Reading 100 items...", end=" ", flush=True)
    result = benchmark_read_items(container, num_reads=100)
    print(f"✅ {result['total_time']:.3f}s ({result['ops_per_sec']:.1f} ops/sec)")
    
    # Query
    print("3️⃣  Querying 10 partitions...", end=" ", flush=True)
    result = benchmark_query_items(container, num_queries=10)
    print(f"✅ {result['total_time']:.3f}s ({result['ops_per_sec']:.1f} ops/sec)")
    
    print("\n🧹 Cleaning up...")
    cleanup_database(client, "quick_benchmark_db")
    
    print("\n✅ Quick benchmark complete!\n")
    print("💡 Tip: Run 'python benchmarks/benchmark_runner.py' for full comparison")

if __name__ == "__main__":
    quick_benchmark()
