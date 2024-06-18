import boto3
from botocore.exceptions import ClientError
import os
import json
from dotenv import load_dotenv
import requests
from io import BytesIO
from tqdm import tqdm

load_dotenv()

def upload_data():
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    region = os.getenv('AWS_REGION')
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    s3_client = boto3.client(
        's3',
        region_name=region,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    with open('data/books.json', 'r') as file:
        books = json.load(file)
        num_thumbnails_uploaded = 0
        num_books = len(books)

        for book in tqdm(books, total=num_books, desc="Uploading Book Thumnails to S3"):
            title = camel_case(book['title'])
            author = camel_case(book['author'])
            year = book['published_year']
            thumbnail = book['thumbnail']
            s3_key = f'{title}_{author}_{year}'

            response = requests.get(thumbnail)
            if response.status_code == 200:
                image_data = BytesIO(response.content)

                try:
                    s3_client.upload_fileobj(image_data, bucket_name, s3_key)
                    num_thumbnails_uploaded += 1
                except ClientError as e:
                    print(f"An AWS service error occurred: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")
            else:
                print(f'Failed to download image from {thumbnail}')
    
    print(f'Uploaded {num_thumbnails_uploaded}/{num_books} thumbails.')


def camel_case(text):
    words = text.split()
    return ''.join([word.capitalize() for word in words])


if __name__ == '__main__':
    upload_data()