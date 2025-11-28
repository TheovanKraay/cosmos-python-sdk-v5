import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError

endpoint = os.getenv('COSMOS_ENDPOINT')
key = os.getenv('COSMOS_KEY')

client = CosmosClient(endpoint, credential=key)

try:
    client.delete_database('testdb')
    print('Deleted testdb database')
except CosmosResourceNotFoundError:
    print('Database not found')
