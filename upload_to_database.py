from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection details
mongo_uri = os.getenv("MONGODB_URI")
mongo_db_name = os.getenv("MONGODB_DB")
mongo_collection = os.getenv("MONOGDB_COLLECTION")

client = MongoClient(mongo_uri)
db = client[mongo_db_name]
collection = db[mongo_collection]

data_file_path = os.getenv("BOOKS_JSON_FILEPATH")
with open(data_file_path, 'r') as file:
    book_data = json.load(file)

collection.insert_many(book_data)

print("Data inserted successfully!")
client.close()