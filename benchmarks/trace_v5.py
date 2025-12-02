"""Trace V5 SDK create_item to understand what it does"""
import time
import ssl
import sys
sys.path.insert(0, r'C:\cosmos\rust-sdk\python-v5\cosmos-python-sdk-v5\python')
from azure.cosmos import CosmosClient

endpoint = 'https://127.0.0.1:8081'
key = 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=='
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

print("Creating V5 client...")
start = time.time()
client = CosmosClient(endpoint, credential=key, connection_verify=ssl_context)
print(f"Client creation took: {time.time() - start:.4f}s")

print("\nCreating database...")
start = time.time()
try:
    database = client.create_database(id="trace_db")
except:
    database = client.get_database_client("trace_db")
print(f"Database creation/get took: {time.time() - start:.4f}s")

print("\nCreating container...")
start = time.time()
try:
    container = database.create_container(
        id="trace_container",
        partition_key={"paths": ["/pk"]}
    )
except:
    container = database.get_container_client("trace_container")
print(f"Container creation/get took: {time.time() - start:.4f}s")

# Time a single create_item operation
print("\n" + "="*60)
print("Timing single create_item operation:")
print("="*60)

item = {
    "id": "test_1",
    "pk": "partition_1",
    "name": "Test Item",
    "value": 123
}

for i in range(5):
    start = time.time()
    try:
        result = container.create_item(body=item)
    except Exception as e:
        # Item exists, try different ID
        item["id"] = f"test_{i}_unique"
        result = container.create_item(body=item)
    elapsed = time.time() - start
    print(f"Create attempt {i+1}: {elapsed:.4f}s")

print("\n" + "="*60)
print("Timing 10 sequential creates:")
print("="*60)

start_total = time.time()
for i in range(10):
    item = {
        "id": f"batch_test_{i}",
        "pk": "partition_batch",
        "name": f"Batch Item {i}",
        "value": i
    }
    try:
        container.create_item(body=item)
    except:
        pass
total_elapsed = time.time() - start_total
print(f"Total time for 10 creates: {total_elapsed:.4f}s")
print(f"Average per operation: {total_elapsed/10:.4f}s")
print(f"Operations per second: {10/total_elapsed:.2f}")

# Cleanup
try:
    client.delete_database("trace_db")
except:
    pass

print("\nDone!")
