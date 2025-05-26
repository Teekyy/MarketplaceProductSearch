import asyncio
from upload_to_s3 import upload_data as upload_to_s3
from upload_to_mongo import upload_data as upload_to_mongo
from upload_to_pinecone import upload_data as upload_to_pinecone
import time
import argparse
from dotenv import load_dotenv


async def populate_data(file_path, s3=False, mongodb=False, pinecone=False):
    """
    Upload book data to S3, MongoDB, and Pinecone asynchronously.
    MongoDB is locally run, and Pinecone is a single API, so no point in using asynchronous functions,
    and better to use threading instead.

    Args:
        file_path (str): Path to the book data file.
        s3 (bool): Flag to upload data to S3.
        mongodb (bool): Flag to upload data to MongoDB.
        pinecone (bool): Flag to upload data to Pinecone.
    """
    load_dotenv()

    if not s3 and not mongodb and not pinecone:
        print("No services specified for populating book data.")
        return
    
    # Create async tasks
    tasks = []
    services = []

    if s3:
        tasks.append(asyncio.create_task(upload_to_s3(file_path)))
        services.append("S3")
    if mongodb:
        tasks.append(asyncio.to_thread(upload_to_mongo, file_path))
        services.append("MongoDB")
    if pinecone:
        tasks.append(asyncio.to_thread(upload_to_pinecone, file_path))
        services.append("Pinecone")

    # Execute tasks and gather results
    results = await asyncio.gather(*tasks, return_exceptions=True)
    failed_services, success_count = [], 0

    # Figure out which services failed
    for (result, service) in zip(results, services):
        if isinstance(result, Exception):
            failed_services.append(service)
            print(f"{service} upload failed: {result}")
        else:
            print(f"{service} upload succeeded!")
            success_count += 1
    
    # Display message based on successes
    if success_count == len(services):
        print("✅ Book data populated in specified services successfully!")
    elif success_count > 0:
        print(f"⚠️ The following services failed: {', '.join(failed_services)}")
    else:
        print(f"❌ Failed to upload in all services.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Populate book data in specified services.")
    parser.add_argument('--s3', action='store_true', help="Populate book data in S3")
    parser.add_argument('--mongodb', action='store_true', help="Populate book data in MongoDB")
    parser.add_argument('--pinecone', action='store_true', help="Populate book data in Pinecone")
    parser.add_argument('--all', action='store_true', help="Populate book data in all services")

    args = parser.parse_args()

    # If --all is specified, set all flags to True
    if args.all:
        args.s3 = args.mongodb = args.pinecone = True

    start = time.time()
    file_path = 'data/books.json'
    asyncio.run(populate_data(
        file_path,
        s3=args.s3,
        mongodb=args.mongodb,
        pinecone=args.pinecone
    ))
    end = time.time()
    time_elapsed = end - start
    print(f'Time elapsed: {time_elapsed} seconds')
