import asyncio
from upload_to_s3 import upload_data as upload_to_s3
from upload_to_mongo import upload_data as upload_to_mongo
from upload_to_pinecone import upload_data as upload_to_pinecone
import time


async def populate_data(file_path):
    """
    Upload book data to S3, MongoDB, and Pinecone asynchronously
    MongoDB is locally run, and Pinecone is a single API, so no point in using asynchronous functions,
    and better to use threading instead
    """
   
    try:
        upload_to_s3_task = asyncio.create_task(upload_to_s3(file_path))
        upload_to_mongo_task = asyncio.to_thread(upload_to_mongo, file_path)
        upload_to_pinecone_task = asyncio.to_thread(upload_to_pinecone, file_path)

        await asyncio.gather(upload_to_s3_task, upload_to_mongo_task, upload_to_pinecone_task)
        print("Book data populated in S3 and MongoDB and Pinecone successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    start = time.time()
    file_path = 'data/books.json'
    asyncio.run(populate_data(file_path))
    end = time.time()
    time_elapsed = end - start
    print(f'Time elapsed: {time_elapsed} seconds')
