# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your gRPC server is running on
EXPOSE 50051

# Command to run the gRPC server
CMD ["python", "search_server_new.py"]
