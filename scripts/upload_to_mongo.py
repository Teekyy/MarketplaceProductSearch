from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv
import os
import json

load_dotenv()

def upload_data():
    mongo_uri = os.getenv("MONGO_URI")

    client = MongoClient(mongo_uri)
    db = client["marketplace"]
    collection = db['books']

    with open('data/books.json', 'r') as file:
        books = json.load(file)
    try:
        result = collection.insert_many(books)
        print(f"Inserted {len(result.inserted_ids)} documents.")
    except BulkWriteError as e:
        print("An error occurred while inserting documents:", e.details)

if __name__ == '__main__':
    upload_data()
