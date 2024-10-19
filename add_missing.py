import grpc
from concurrent import futures
import search_service_pb2
import search_service_pb2_grpc
import pymongo
import numpy as np
from sentence_transformers import SentenceTransformer
import time
from pinecone import Pinecone

# MongoDB connection setup
MONGODB_URI = "mongodb+srv://nipuna21:giselle123@cluster0.a9vxy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGODB_URI)
db = client['ecommerce']
items_collection = db['items']

# Load the sentence transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Generates 384-dimensional vectors

# Pinecone API Key and Environment
PINECONE_API_KEY = "b96a2456-baab-4784-882e-7162b0d9f3f0"
PINECONE_ENVIRONMENT = "us-east-1"

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define the index name
index_name = "ecommerce-items"
while True:
    # Check if the index exists and is ready
    status = pc.describe_index(index_name).status
    if status['ready'] and index_name in pc.list_indexes().names():
        print(f"Index '{index_name}' is ready.")
        index = pc.Index(index_name)
        break  # Exit the loop when index is ready
    else:
        print(f"Index '{index_name}' is not ready yet. Waiting for 1 second...")
        time.sleep(1)
def generate_vector_for_item(item):
    # You can use productName, description, or both to generate the embedding
    text = item.get('productName', '') + ' ' + (item.get('description', '') or '')
    embedding = model.encode(text)
    return np.array(embedding).astype('float32')


def add_missing_items_to_pinecone():
    # Retrieve all items from MongoDB
    items = list(items_collection.find({}, {"_id": 0, "itemId": 1, "productName": 1, "description": 1}))

    # Extract all itemIds from MongoDB
    mongo_item_ids = {item['itemId'] for item in items}

    # Retrieve all itemIds from Pinecone using the list method (this is faster and cheaper than fetching all data)
    pinecone_item_ids = set()
    for ids in index.list(namespace=''):  # Iterate over the returned IDs
        pinecone_item_ids.update(ids) 

    # Find the items that are in MongoDB but not in Pinecone
    missing_item_ids = mongo_item_ids - pinecone_item_ids

    if missing_item_ids:
        # Prepare the vectors for missing items
        pinecone_vectors = []
        for item in items:
            if item['itemId'] in missing_item_ids:
                vector = generate_vector_for_item(item)  # Generate vector using sentence transformer
                pinecone_vectors.append((item['itemId'], vector.tolist()))  # Prepare for Pinecone

        # Upsert only the missing vectors to Pinecone
        index.upsert(vectors=pinecone_vectors)
        print(f"Upserted {len(pinecone_vectors)} missing item vectors to Pinecone.")
    else:
        print("No missing items to upsert.")

# Example usage:
if __name__ == "__main__":
    add_missing_items_to_pinecone()

