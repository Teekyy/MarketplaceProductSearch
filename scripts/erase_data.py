import time
from dotenv import load_dotenv
import asyncio
import boto3
import botocore.exceptions
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from pinecone import Pinecone
from pinecone.exceptions import (
    PineconeException,
    NotFoundException
)
import os
import argparse

async def erase_data(s3=False, mongodb=False, pinecone=False):
    """
    Delete book data from S3, MongoDB, and Pinecone asynchronously.
    We are using threads instead of true asynchronous, because most of the operations are single API calls.

    Args:
        s3 (bool): Flag to erase data from S3.
        mongodb (bool): Flag to erase data from MongoDB.
        pinecone (bool): Flag to erase data from Pinecone.
    """
    load_dotenv()

    if not s3 and not mongodb and not pinecone:
        print("No services specified for erasing book data.")
        return

    # Create async tasks
    tasks = []
    services = []

    if s3:
        tasks.append(asyncio.to_thread(erase_s3_data))
        services.append("S3")
    if mongodb:
        tasks.append(asyncio.to_thread(erase_mongodb_data))
        services.append("MongoDB")
    if pinecone:
        tasks.append(asyncio.to_thread(erase_pinecone_data))
        services.append("Pinecone")

    # Execute tasks and gather results
    results = await asyncio.gather(*tasks, return_exceptions=True)
    failed_services, success_count = [], 0

    # Figure out which services failed
    for (result, service) in zip(results, services):
        if isinstance(result, Exception):
            failed_services.append(service)
            print(f"{service} failed to delete book data: {result}")
        else:
            success_count += 1
            print(f"{service} book data deletion succeded!")

    # Display message based on successes
    if success_count == len(services):
        print("✅ Book data deleted in specified services!")
    elif success_count > 0:
        print(f"⚠️ The following services failed: {', '.join(failed_services)}")
    else:
        print(f"❌ Failed to delete book data in all services.")


def erase_s3_data():
    """
    Completely empty s3 bucket by deleting all objects.
    """
    # Retrieve AWS credentials for client
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    region = os.getenv('AWS_REGION')
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
 
    # Create client for S3
    s3_resource = boto3.resource('s3', region_name=region, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
    # Retrieve bucket and delete all objects
    bucket = s3_resource.Bucket(bucket_name)
    bucket.objects.filter(Prefix='thumbnails/').delete()


def erase_mongodb_data():
    """
    Completely empty MongoDB by deleting all documents in the collection.
    """
    # Load MongoDB info
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client[os.getenv("MONGO_DB")]
    collection = db['books']

    # Delete all documents
    result = collection.delete_many({})
    print(f"Deleted {result.deleted_count} documents.")


def erase_pinecone_data():
    """
    Completely empty Pinecone vector index by deleting all vectors.
    """

    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(host=os.getenv("PINECONE_INDEX_HOST"))

    try:
        # Delete all vectors
        result = index.delete(delete_all=True)
    except NotFoundException as e:
        print("No vectors to delete in Pinecone index.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Erase book data from specified services.")
    parser.add_argument("--s3", action="store_true", help="Erase S3 data")
    parser.add_argument("--mongodb", action="store_true", help="Erase MongoDB data")
    parser.add_argument("--pinecone", action="store_true", help="Erase Pinecone data")
    parser.add_argument("--all", action="store_true", help="Erase data from all services")

    args = parser.parse_args()

    # If --all is specified, set all flags to True
    if args.all:
        args.s3 = args.mongodb = args.pinecone = True

    start = time.time()
    asyncio.run(erase_data(
        s3=args.s3,
        mongodb=args.mongodb,
        pinecone=args.pinecone
    ))
    end = time.time()
    time_elapsed = end - start
    print(f'Time elapsed: {time_elapsed} seconds')