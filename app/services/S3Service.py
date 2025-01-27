import os
import asyncio
import aioboto3
import botocore.exceptions

async def fetch_presigned_urls(s3_keys):
    # Retrieve AWS credentials for client
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    region = os.getenv('AWS_REGION')
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    async with aioboto3.Session().client(
        's3',
        region_name=region,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    ) as s3_client:

        tasks = []

        for s3_key in s3_keys:
            task = asyncio.create_task(create_presigned_url(
                s3_client,
                bucket_name,
                s3_key
            ))

            tasks.append(task)

        presigned_urls = await asyncio.gather(*tasks)
        return presigned_urls

async def create_presigned_url(s3_client, bucket_name, s3_key, expiration=3600):
    try:
        response = await s3_client.generate_presigned_url(
            ClientMethod = 'get_object',
            Params = {
                'Bucket': bucket_name,
                'Key': s3_key
            },
            ExpiresIn = expiration
        )

        return response
    except botocore.exceptions.ClientError as e:
        print(f"An AWS service error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None