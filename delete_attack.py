import pymongo

# Connect to MongoDB
MONGODB_URI = "mongodb+srv://nipuna21:giselle123@cluster0.a9vxy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGODB_URI)
db = client['ecommerce']
collection = db['users']

# Delete documents that match certain criteria
result = collection.delete_many({ "bin": { "$exists": True } })  # Adjust the query as needed

# Check the result
print(f"Documents deleted: {result.deleted_count}")
