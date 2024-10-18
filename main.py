import pymongo
import numpy as np
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec



# MongoDB connection setup using your connection string
MONGODB_URI = "mongodb+srv://nipuna21:giselle123@cluster0.a9vxy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGODB_URI)
db = client['ecommerce']
items_collection = db['items']

# Load the sentence transformer model (you can use a different pre-trained model)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # This generates 384-dimensional vectors

# Pinecone API Key and Environment
PINECONE_API_KEY = "b96a2456-baab-4784-882e-7162b0d9f3f0"  # Your Pinecone API key
PINECONE_ENVIRONMENT = "us-east-1"  # Change this to a supported region

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create or connect to an index in Pinecone (adjust dimensionality)
index_name = "ecommerce-items"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # Ensure dimension matches embedding size (384 for MiniLM)
        metric='cosine',  # Choose a metric (e.g., cosine, euclidean)
        spec=ServerlessSpec(
            cloud='aws',  # Cloud provider
            region='us-east-1'  # Change to a supported region
        )
    )

# Connect to the index
index = pc.Index(index_name)

# Function to generate vector embeddings using the sentence transformer model
def generate_vector_for_item(item):
    # You can choose to use productName, description, or both to generate the embedding
    text = item.get('productName', '') + ' ' + (item.get('description', '') or '')
    embedding = model.encode(text)
    return np.array(embedding).astype('float32')

# Function to upsert item vectors to Pinecone
def upsert_item_vectors_to_pinecone():
    # Retrieve all items from MongoDB
    items = list(items_collection.find({}, {"_id": 0, "itemId": 1, "productName": 1, "description": 1}))

    # Prepare Pinecone upsert data
    pinecone_vectors = []
    for item in items:
        vector = generate_vector_for_item(item)  # Generate vector using sentence transformer
        pinecone_vectors.append((item['itemId'], vector.tolist()))  # Pinecone expects (id, vector)

    # Upsert vectors into Pinecone index
    index.upsert(vectors=pinecone_vectors)
    print(f"Upserted {len(pinecone_vectors)} item vectors to Pinecone.")

# Step 1: Build the FAISS index and upsert vectors to Pinecone
def build_faiss_index_and_upsert_to_pinecone():
    # Retrieve all items
    items = list(items_collection.find({}, {"_id": 0, "itemId": 1, "productName": 1, "description": 1}))  # Fetching relevant fields

    item_id_map = {}  # Dictionary to store mapping of FAISS index to MongoDB itemId

    pinecone_vectors = []  # List to hold vectors for Pinecone upsert

    for i, item in enumerate(items):
        vector = generate_vector_for_item(item)  # Generate vector using sentence transformer
        item_id_map[i] = item['itemId']  # Store the mapping of index position to MongoDB itemId
        pinecone_vectors.append((item['itemId'], vector.tolist()))  # Prepare for Pinecone

    # Upsert vectors to Pinecone
    index.upsert(vectors=pinecone_vectors)

    print(f"Upserted {len(pinecone_vectors)} vectors to Pinecone.")

    return item_id_map

def perform_vector_search_in_pinecone(query_text, top_k=5):
    # Generate vector embeddings for the query
    query_vector = model.encode(query_text)
    
    # Ensure the vector is a list of floats
    query_vector = query_vector.astype(float).tolist()  # Ensure proper format for Pinecone
    
    # Perform the vector search in Pinecone
    query_results = index.query(queries=[query_vector], top_k=top_k)

    # Extract item IDs from the query results
    result_item_ids = [match.id for match in query_results.matches]

    return result_item_ids


# Example usage:
if __name__ == "__main__":
    # # Step 1: Upsert vectors to Pinecone
    # build_faiss_index_and_upsert_to_pinecone()

    # Step 2: Define a query (this is the text you want to search for)
    # Check if the index is ready
    if index_name in pc.list_indexes():
        print(f"Index '{index_name}' is ready.")
    else:
        print(f"Index '{index_name}' does not exist or is not ready.")

    query_text = "Blue denim "  # Replace with your actual query
    result_item_ids = perform_vector_search_in_pinecone(query_text, top_k=5)
    print("Search Results:", result_item_ids)

    # Step 4: Retrieve corresponding items from MongoDB
    matching_items = list(items_collection.find({"itemId": {"$in": result_item_ids}}))

    # Display search results
    for i, item in enumerate(matching_items):
        print(f"Rank {i+1}: ItemId: {item['itemId']}, ProductName: {item['productName']}")
