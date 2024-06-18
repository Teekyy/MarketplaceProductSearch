import asyncio
import aioboto3
import botocore.exceptions
import aiohttp
import os
import json
from dotenv import load_dotenv
import requests
from io import BytesIO
from tqdm.asyncio import tqdm as atqdm

load_dotenv()
         

async def upload_data():
    # Retrieve AWS credentials for client
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    region = os.getenv('AWS_REGION')
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Access book data from file
    with open('data/books.json', 'r') as file:
        books = json.load(file)

    # Create asynchronous clients for HTTP req and S3 client
    async with aiohttp.ClientSession() as session, aioboto3.Session().client(
        's3',
        region_name=region,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    ) as s3_client:
        num_books = len(books)

        # tasks will hold the coroutines to be executed
        tasks = []

        # progress bar
        pbar = atqdm(total=num_books, desc="Uploading Book Thumbnails to S3")

        # setup and start executing coroutines
        for book in books:
            title = camel_case(book['title'])
            author = camel_case(book['author'])
            year = book['published_year']
            thumbnail_url = book['thumbnail']
            s3_key = f'{title}_{author}_{year}'

            task = asyncio.create_task(download_and_upload(
                session=session,
                s3_client=s3_client,
                thumbnail_url=thumbnail_url,
                bucket_name=bucket_name,
                s3_key=s3_key,
                pbar=pbar
            ))
            tasks.append(task)

        # wait for coroutines to finish and count successes
        results = await asyncio.gather(*tasks)
        pbar.close()
        num_thumbnails_uploaded = sum(results)

    print(f'Uploaded {num_thumbnails_uploaded}/{num_books} thumbails.')


async def download_and_upload(session, s3_client, thumbnail_url, bucket_name, s3_key, pbar):
    try:
        async with session.get(thumbnail_url) as response:
            if response.status == 200:
                image_data = BytesIO(await response.read())
                await s3_client.upload_fileobj(image_data, bucket_name, s3_key)
                pbar.update(1)
                return True
            else:
                print(f'Failed to download image from {thumbnail_url}. Status: {response.status}')
                pbar.update(1)
                return False
            
    except aiohttp.ClientError as e:
        print(f'HTTP client error occured: {e}')
        pbar.update(1)
        return False
    except botocore.exceptions.ClientError as e:
        print(f"An AWS service error occurred: {e}")
        pbar.update(1)
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        pbar.update(1)
        return False

def camel_case(text):
    words = text.split()
    return ''.join([word.capitalize() for word in words])


if __name__ == '__main__':
    asyncio.run(upload_data())