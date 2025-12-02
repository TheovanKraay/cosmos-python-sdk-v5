"""
Benchmark Tests - High volume performance tests for Cosmos DB SDK
Runs on both V4 (pure Python) and V5 (Rust-based) SDKs
"""
import os
import sys
import time
import json
from datetime import datetime

def get_client():
    """Get Cosmos DB client - works with both V4 and V5"""
    import ssl
    from azure.cosmos import CosmosClient
    
    # Hard-code emulator endpoint and key
    # Use 127.0.0.1 instead of localhost to avoid DNS issues
    endpoint = 'https://127.0.0.1:8081'
    key = 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=='
    
    # For V4 SDK, we need to pass a custom SSL context via connection_verify
    # For V5 SDK, connection_verify=False works
    # Create an SSL context that doesn't verify certificates (for emulator)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    return CosmosClient(endpoint, credential=key, connection_verify=ssl_context)

def setup_database_and_container(client, db_name="benchmark_db", container_name="benchmark_container"):
    """Setup test database and container"""
    # Create database
    try:
        database = client.create_database(id=db_name)
    except Exception:
        database = client.get_database_client(db_name)
    
    # Create container
    try:
        container = database.create_container(
            id=container_name,
            partition_key={"paths": ["/pk"]}
        )
    except Exception:
        container = database.get_container_client(container_name)
    
    return database, container

def cleanup_database(client, db_name="benchmark_db"):
    """Clean up test database"""
    try:
        client.delete_database(db_name)
    except Exception:
        pass

def benchmark_create_items(container, num_items=1000):
    """Benchmark: Create multiple items"""
    items = [
        {
            "id": f"item_{i}",
            "pk": f"partition_{i % 10}",  # 10 partitions
            "name": f"Product {i}",
            "category": "electronics",
            "price": 99.99 + i,
            "description": f"Description for item {i}" * 5,  # Make it more realistic
            "tags": ["tag1", "tag2", "tag3"],
            "timestamp": datetime.utcnow().isoformat()
        }
        for i in range(num_items)
    ]
    
    start = time.time()
    
    for item in items:
        try:
            container.create_item(body=item)
        except Exception as e:
            # Skip duplicates or other errors
            pass
    
    elapsed = time.time() - start
    
    return {
        "total_time": elapsed,
        "num_items": num_items,
        "ops_per_sec": num_items / elapsed if elapsed > 0 else 0
    }

def benchmark_read_items(container, num_reads=1000):
    """Benchmark: Read multiple items by ID"""
    start = time.time()
    
    for i in range(num_reads):
        try:
            container.read_item(
                item=f"item_{i}",
                partition_key=f"partition_{i % 10}"
            )
        except Exception:
            # Item might not exist
            pass
    
    elapsed = time.time() - start
    
    return {
        "total_time": elapsed,
        "num_reads": num_reads,
        "ops_per_sec": num_reads / elapsed if elapsed > 0 else 0
    }

def benchmark_query_items(container, num_queries=100):
    """Benchmark: Query items across partitions"""
    start = time.time()
    
    for i in range(10):  # Query each partition
        partition_key = f"partition_{i}"
        try:
            results = container.query_items(
                query=f"SELECT * FROM c WHERE c.pk = '{partition_key}'",
                partition_key=partition_key
            )
            # Consume results
            _ = list(results) if hasattr(results, '__iter__') else results
        except Exception:
            pass
    
    elapsed = time.time() - start
    
    return {
        "total_time": elapsed,
        "num_queries": 10,
        "ops_per_sec": 10 / elapsed if elapsed > 0 else 0
    }

def benchmark_upsert_items(container, num_upserts=500):
    """Benchmark: Upsert items (mix of create and update)"""
    items = [
        {
            "id": f"item_{i}",
            "pk": f"partition_{i % 10}",
            "name": f"Updated Product {i}",
            "category": "electronics",
            "price": 199.99 + i,
            "description": f"Updated description for item {i}" * 5,
            "updated": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        for i in range(num_upserts)
    ]
    
    start = time.time()
    
    for item in items:
        try:
            container.upsert_item(body=item)
        except Exception:
            pass
    
    elapsed = time.time() - start
    
    return {
        "total_time": elapsed,
        "num_upserts": num_upserts,
        "ops_per_sec": num_upserts / elapsed if elapsed > 0 else 0
    }

def benchmark_replace_items(container, num_replaces=300):
    """Benchmark: Replace existing items"""
    start = time.time()
    
    for i in range(num_replaces):
        try:
            # First read to get the item
            item = container.read_item(
                item=f"item_{i}",
                partition_key=f"partition_{i % 10}"
            )
            
            # Modify and replace
            item["price"] = item.get("price", 100) * 1.1
            item["modified"] = True
            
            container.replace_item(
                item=f"item_{i}",
                body=item
            )
        except Exception:
            pass
    
    elapsed = time.time() - start
    
    return {
        "total_time": elapsed,
        "num_replaces": num_replaces,
        "ops_per_sec": num_replaces / elapsed if elapsed > 0 else 0
    }

def benchmark_delete_items(container, num_deletes=200):
    """Benchmark: Delete items"""
    start = time.time()
    
    for i in range(num_deletes):
        try:
            container.delete_item(
                item=f"item_{i}",
                partition_key=f"partition_{i % 10}"
            )
        except Exception:
            pass
    
    elapsed = time.time() - start
    
    return {
        "total_time": elapsed,
        "num_deletes": num_deletes,
        "ops_per_sec": num_deletes / elapsed if elapsed > 0 else 0
    }

def benchmark_mixed_workload(container, num_operations=500):
    """Benchmark: Mixed workload (create, read, update, delete)"""
    start = time.time()
    
    for i in range(num_operations):
        pk = f"partition_{i % 10}"
        item_id = f"mixed_{i}"
        
        try:
            # 40% creates
            if i % 10 < 4:
                container.create_item(body={
                    "id": item_id,
                    "pk": pk,
                    "name": f"Mixed Item {i}",
                    "value": i
                })
            # 30% reads
            elif i % 10 < 7:
                container.read_item(item=item_id, partition_key=pk)
            # 20% updates
            elif i % 10 < 9:
                container.upsert_item(body={
                    "id": item_id,
                    "pk": pk,
                    "name": f"Updated Mixed Item {i}",
                    "value": i * 2
                })
            # 10% deletes
            else:
                container.delete_item(item=item_id, partition_key=pk)
        except Exception:
            pass
    
    elapsed = time.time() - start
    
    return {
        "total_time": elapsed,
        "num_operations": num_operations,
        "ops_per_sec": num_operations / elapsed if elapsed > 0 else 0
    }

def run_all_benchmarks():
    """Run all benchmark tests"""
    sdk_version = os.getenv('SDK_VERSION', 'unknown')
    
    print(f"Starting benchmarks with SDK {sdk_version}...", file=sys.stderr)
    
    client = get_client()
    database, container = setup_database_and_container(client)
    
    results = {
        "sdk_version": sdk_version,
        "timestamp": datetime.utcnow().isoformat(),
        "tests": {}
    }
    
    # Run benchmarks
    print(f"Running create items benchmark...", file=sys.stderr)
    results["tests"]["create_items_1000"] = benchmark_create_items(container, 1000)
    
    print(f"Running read items benchmark...", file=sys.stderr)
    results["tests"]["read_items_1000"] = benchmark_read_items(container, 1000)
    
    print(f"Running query items benchmark...", file=sys.stderr)
    results["tests"]["query_items_10_partitions"] = benchmark_query_items(container, 100)
    
    print(f"Running upsert items benchmark...", file=sys.stderr)
    results["tests"]["upsert_items_500"] = benchmark_upsert_items(container, 500)
    
    print(f"Running replace items benchmark...", file=sys.stderr)
    results["tests"]["replace_items_300"] = benchmark_replace_items(container, 300)
    
    print(f"Running delete items benchmark...", file=sys.stderr)
    results["tests"]["delete_items_200"] = benchmark_delete_items(container, 200)
    
    print(f"Running mixed workload benchmark...", file=sys.stderr)
    results["tests"]["mixed_workload_500"] = benchmark_mixed_workload(container, 500)
    
    # Cleanup
    print(f"Cleaning up...", file=sys.stderr)
    cleanup_database(client)
    
    # Output results as JSON to stdout (so benchmark_runner.py can parse it)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_all_benchmarks()
