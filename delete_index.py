
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
Pinecone.delete_index(name=index_name)
