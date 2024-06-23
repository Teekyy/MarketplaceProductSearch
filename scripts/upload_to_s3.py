import asyncio
import aioboto3
import botocore.exceptions
import aiohttp
import os
import json
from dotenv import load_dotenv
from io import BytesIO
from tqdm.asyncio import tqdm as atqdm
import time         

async def upload_data(file_path):
    """
    Uploads book thumbnails from book JSON file to an AWS S3 bucket asynchronously.

    Args:
        file_path (str): The path to the JSON file containing book data.
    """

    load_dotenv()

    # Retrieve AWS credentials for client
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    region = os.getenv('AWS_REGION')
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    start = time.time()

    # Access book data from file
    with open(file_path, 'r') as file:
        books = json.load(file)

    # Create asynchronous clients for HTTP req and S3 client
    async with aiohttp.ClientSession() as session, aioboto3.Session().client(
        's3',
        region_name=region,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    ) as s3_client:
        num_books = len(books)

        # Tasks will hold the coroutines to be executed
        tasks = []

        # Progress bar
        pbar = atqdm(total=num_books, desc="Uploading Book Thumbnails to S3")

        # Setup and execute coroutines
        for book in books:

            # Extract data from JSON file and generate unique S3 key
            title = camel_case(book['title'])
            author = camel_case(book['author'])
            year = book['published_year']
            thumbnail_url = book['thumbnail']
            s3_key = f'{title}_{author}_{year}'

            # Create coroutine task and schedule it for execution
            task = asyncio.create_task(download_and_upload_thumbnail(
                session=session,
                s3_client=s3_client,
                thumbnail_url=thumbnail_url,
                bucket_name=bucket_name,
                s3_key=s3_key,
                pbar=pbar
            ))
            tasks.append(task)

        # Wait for coroutines to finish and count successes
        results = await asyncio.gather(*tasks)
        pbar.close()
        num_thumbnails_uploaded = sum(results)

    # Calculate elapsed time
    end = time.time()
    time_elapsed = end - start
    print(f'Time elapsed: {time_elapsed} seconds')

    print(f'Uploaded {num_thumbnails_uploaded}/{num_books} thumbails.')


async def download_and_upload_thumbnail(session, s3_client, thumbnail_url, bucket_name, s3_key, pbar):
    """
    Downloads a thumbnail image from a URL and uploads it to an S3 bucket.

    Args:
        session (aiohttp.ClientSession): The asynchronous HTTP session.
        s3_client (aioboto3.S3.Client): The asynchronous S3 client.
        thumbnail_url (str): The URL of the thumbnail image.
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The S3 key for the uploaded image.
        pbar (tqdm): The progress bar to update.

    Returns:
        bool: True if the thumbnail was successfully uploaded, False otherwise.
    """
    try:
        # Asynchronously download data in memory, and then upload to S3
        async with session.get(thumbnail_url) as response:
            if response.status == 200:
                image_data = BytesIO(await response.read())
                await s3_client.upload_fileobj(image_data, bucket_name, s3_key)
                pbar.update(1) # Update progress bar
                return True
            else:
                print(f'Failed to download image from {thumbnail_url}. Status: {response.status}')
                pbar.update(1) # Update progress bar
                return False
    except aiohttp.ClientError as e:
        print(f'HTTP client error occured: {e}')
        pbar.update(1) # Update progress bar
        return False
    except botocore.exceptions.ClientError as e:
        print(f"An AWS service error occurred: {e}")
        pbar.update(1) # Update progress bar
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        pbar.update(1) # Update progress bar
        return False

def camel_case(text):
    """
    Converts a given string to camel case.

    Args:
        text (str): The input string to be converted.

    Returns:
        str: The camel case version of the input string.
    """
    words = text.split()
    return ''.join([word.capitalize() for word in words])


if __name__ == '__main__':
    asyncio.run(upload_data('data/books.json'))