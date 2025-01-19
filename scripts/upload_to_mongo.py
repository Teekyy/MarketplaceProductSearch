from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv
import os
import json
import time
from utils.helpers import generate_s3_key

def upload_data(file_path):
    load_dotenv()

    # Load MongoDB info
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["marketplace"]
    collection = db['books']

    # Load book data from JSON file
    with open(file_path, 'r') as file:
        books = json.load(file)

    # Update the thumbnail field with the s3 key for all books
    for book in books:
        book['thumbnail'] = generate_s3_key(book)

    # Insert all the data into DB
    try:
        result = collection.insert_many(books)
        print(f"Inserted {len(result.inserted_ids)} documents.")
    except BulkWriteError as e:
        print("An error occurred while inserting documents:", e.details)
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

if __name__ == '__main__':
    start = time.time()
    upload_data('data/books.json')
    end = time.time()
    time_elapsed = end - start
    print(f'Time elapsed: {time_elapsed} seconds')
