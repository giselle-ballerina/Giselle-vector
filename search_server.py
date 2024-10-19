import grpc
from concurrent import futures
import search_service_pb2
import search_service_pb2_grpc
from sentence_transformers import SentenceTransformer
import pymongo
import numpy as np

class SearchService(search_service_pb2_grpc.SearchServiceServicer):
    def PerformSearch(self, request, context):
        query_text = request.query
        top_k = request.top_k
        print(f"Received query: {query_text}, top_k: {top_k}")
        # Perform the vector search (mocked result here)
        result_item_ids = ["item1", "item2", "item3"]
        return search_service_pb2.SearchResponse(item_ids=result_item_ids)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    search_service_pb2_grpc.add_SearchServiceServicer_to_server(SearchService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Python gRPC server running on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
