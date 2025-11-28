// Test file to understand the new azure_data_cosmos 0.22 API
// This will help us understand the correct patterns

use azure_data_cosmos::clients::CosmosClient;
use azure_identity::DefaultAzureCredential;

#[tokio::main]
async fn main() {
    // Test 1: Client creation with key
    let endpoint = "https://localhost:8081";
    let key = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==";
    
    // Try to understand the client API
    println!("Testing azure_data_cosmos 0.22 API...");
    
    // The new API likely uses builder pattern or different constructor
    // Let's see what methods are available
}
