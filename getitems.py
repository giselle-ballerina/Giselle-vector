import pymongo
import numpy as np
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import time
# MongoDB connection setup
MONGODB_URI = "mongodb+srv://nipuna21:giselle123@cluster0.a9vxy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGODB_URI)
db = client['ecommerce']
items_collection = db['items']

# Load the sentence transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Generates 384-dimensional vectors

# Pinecone API Key and Environment
PINECONE_API_KEY = "b96a2456-baab-4784-882e-7162b0d9f3f0"  # Your Pinecone API key
PINECONE_ENVIRONMENT = "us-east-1"  # Your Pinecone environment

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define the index name
index_name = "ecommerce-items"
while True:
  # Check if index exists and is ready
  status = pc.describe_index(index_name).status
  if status['ready'] and index_name in pc.list_indexes().names():
    print(f"Index '{index_name}' is ready.")
    index = pc.Index(index_name)
    print(f"Connecting to existing Pinecone index: '{index}'")
    break  # Exit the loop when index is ready and found
  else:
    print(f"Index '{index_name}' is not ready yet. Waiting for 1 second...")
    time.sleep(1)
# if index_name in existing_indexes:
#     print(f"Connecting to existing Pinecone index: '{index_name}'")
#     # Connect to the existing index
#     index = pc.Index(index_name)
# else:
#     print(f"Index '{index_name}' does not exist.")
#     exit()

# Function to generate vector embeddings using the sentence transformer model
def generate_vector_for_item(item):
    # You can use productName, description, or both to generate the embedding
    text = item.get('productName', '') + ' ' + (item.get('description', '') or '')
    embedding = model.encode(text)
    return np.array(embedding).astype('float32')
def generate_vector_for_query(item):
    # You can use productName, description, or both to generate the embedding
    
    embedding = model.encode(item)
    return np.array(embedding).astype('float32')
# Function to perform vector search in Pinecone
def perform_vector_search_in_pinecone(query_text, top_k=5):
    # Generate vector embeddings for the query
    embedding = model.encode(query_text) # Ensure proper format for Pinecone
    print(f"Encoded Text Shape: {embedding.shape}")
    query_vector = embedding.astype(float).tolist() # Convert to list for Pinecone
    # Perform the vector search in Pinecone
    query_results = index.query(vector=query_vector, top_k=top_k)

    # Extract item IDs from the query results
    result_item_ids = [match.id for match in query_results.matches]

    return result_item_ids

# Example usage:
if __name__ == "__main__":
    # Step 2: Define a query
        query_text = "Red blouse kurtha"  # Replace with your actual query
    
    # Ensure the index exists and is ready
   
        print(f"Index '{index_name}' is ready.")
        result_item_ids = perform_vector_search_in_pinecone(query_text, top_k=5)
        print("Search Results:", result_item_ids)
        
        # Step 4: Retrieve corresponding items from MongoDB
        matching_items = list(items_collection.find({"itemId": {"$in": result_item_ids}}))

        # Display search results
        for i, item in enumerate(matching_items):
            print(f"Rank {i+1}: ItemId: {item['itemId']}, ProductName: {item['productName']}")
 
