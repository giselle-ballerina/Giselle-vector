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

# Function to generate vector embeddings using the sentence transformer model
def generate_vector_for_query(query_text):
    embedding = model.encode(query_text)
    return np.array(embedding).astype('float32')

# Function to perform vector search in Pinecone
def perform_vector_search_in_pinecone(query_text, top_k=5):
    embedding = generate_vector_for_query(query_text)
    query_vector = embedding.astype(float).tolist()
    
    # Perform the vector search in Pinecone
    query_results = index.query(vector=query_vector, top_k=top_k)
    result_item_ids = [match.id for match in query_results.matches]
    
    return result_item_ids

# gRPC Search Service definition
class SearchService(search_service_pb2_grpc.SearchServiceServicer):
    def PerformSearch(self, request, context):
        query_text = request.query
        top_k = request.top_k
        print(f"Received query: {query_text}, top_k: {top_k}")
        
        # Perform the vector search in Pinecone
        result_item_ids = perform_vector_search_in_pinecone(query_text, top_k)
        
        # Fetch items from MongoDB
        matching_items = list(items_collection.find({"itemId": {"$in": result_item_ids}}))
        
        # Extract item IDs
        item_ids = [item['itemId'] for item in matching_items]
        
        return search_service_pb2.SearchResponse(item_ids=item_ids)

# gRPC server setup
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    search_service_pb2_grpc.add_SearchServiceServicer_to_server(SearchService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Python gRPC server running on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
