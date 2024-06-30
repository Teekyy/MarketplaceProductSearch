import asyncio
from upload_to_s3 import upload_data as upload_to_s3
from upload_to_mongo import upload_data as upload_to_mongo
import time

async def populate_data(file_path):
    # Generate new book data and upload to S3 and MongoDB asynchronously
    start = time.time()

    try:
        upload_to_s3_task = asyncio.create_task(upload_to_s3(file_path))
        upload_to_mongo_task = asyncio.to_thread(upload_to_mongo, file_path)

        await asyncio.gather(upload_to_s3_task, upload_to_mongo_task)
    except Exception as e:
        print(f"An error occurred: {e}")

    end = time.time()
    elapsed_time = end - start
    print(f'Total time elapsed: {elapsed_time}')
    print("Book data populated in S3 and MongoDB successfully!")

if __name__ == '__main__':
    file_path = 'data/books.json'
    asyncio.run(populate_data(file_path))