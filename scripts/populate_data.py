import asyncio
from upload_to_s3 import upload_data as upload_to_s3
from upload_to_mongo import upload_data as upload_to_mongo
from upload_to_pinecone import upload_data as upload_to_pinecone
import time
import argparse


async def populate_data(file_path, s3=False, mongodb=False, pinecone=False):
    """
    Upload book data to S3, MongoDB, and Pinecone asynchronously
    MongoDB is locally run, and Pinecone is a single API, so no point in using asynchronous functions,
    and better to use threading instead
    """

    if not s3 and not mongodb and not pinecone:
        print("No services specified for populating book data.")
        return
   
    try:
        tasks = []

        if s3:
            tasks.append(asyncio.create_task(upload_to_s3(file_path)))
        if mongodb:
            tasks.append(asyncio.to_thread(upload_to_mongo, file_path))
        if pinecone:
            tasks.append(asyncio.to_thread(upload_to_pinecone, file_path))

        await asyncio.gather(*tasks)
        print("Book data populated in specified services successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Populate book data in specified services.")
    parser.add_argument('--s3', action='store_true', help="Populate book data in S3")
    parser.add_argument('--mongodb', action='store_true', help="Populate book data in MongoDB")
    parser.add_argument('--pinecone', action='store_true', help="Populate book data in Pinecone")

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
