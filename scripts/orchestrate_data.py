import asyncio
from generate_book_data import generate_book_data
from upload_to_s3 import upload_data as upload_to_s3
from upload_to_mongo import upload_data as upload_to_mongo

async def main(file_path):
    try:
        generate_book_data(file_path)

        upload_to_s3_task = asyncio.create_task(upload_to_s3(file_path))
        upload_to_mongo_task = asyncio.to_thread(upload_to_mongo, file_path)

        await asyncio.gather(upload_to_s3_task, upload_to_mongo_task)
    except Exception as e:
        print(f"An error occurred: {e}")

    print("Book generated and populated.")

if __name__ == '__main__':
    file_path = 'data/books.json'
    asyncio.run(main(file_path))