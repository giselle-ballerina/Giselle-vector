# Giselle-vector
# gRPC Search Service

This project is a Python-based gRPC server that provides search services. The server is designed to run using Python 3.10 and includes all necessary dependencies in the `requirements.txt` file.

## Prerequisites

Make sure you have Docker installed on your machine to build and run the container.

## Setup Instructions

1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```
2. Build the Docker image

```bash 
docker build -t grpc-search-service .
```
3. Run the Docker container
```bash 
docker run -d -p 50051:50051 grpc-search-service
```