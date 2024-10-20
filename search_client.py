import grpc
import search_service_pb2
import search_service_pb2_grpc

def run():
    # Connect to the gRPC server
    with grpc.insecure_channel('20.246.133.101:50051') as channel:
        # Create a stub (client) for the SearchService
        stub = search_service_pb2_grpc.SearchServiceStub(channel)

        # Create a QueryRequest message
        query_request = search_service_pb2.QueryRequest(
            query="Red blouse kurtha",  # Example query
            top_k=5                      # Number of top results
        )

        # Call the PerformSearch method on the server
        response = stub.PerformSearch(query_request)

        # Print out the response from the server
        print(f"Received item IDs: {response.item_ids}")

if __name__ == '__main__':
    run()
