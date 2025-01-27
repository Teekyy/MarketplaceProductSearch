import os
import asyncio
import aioboto3
import botocore.exceptions
from dotenv import load_dotenv

class S3Service:
    def __init__(self):
        load_dotenv()

        self._bucket_name = os.getenv('AWS_BUCKET_NAME')

        # Create session
        self.session = aioboto3.Session(
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )


    async def get_client(self):
        return self.session.client('s3')


    async def fetch_presigned_urls(self, s3_keys):
        async with await self.get_client as s3_client:
            tasks = []
            for s3_key in s3_keys:
                task = asyncio.create_task(self._generate_presigned_url(s3_client, s3_key))
                tasks.append(task)

            return await asyncio.gather(*tasks)
        
    
    async def get_presigned_url(self, s3_key):
        async with await self.get_client as s3_client:
            return await self._generate_presigned_url(s3_client, s3_key)


    async def _generate_presigned_url(self, s3_client, s3_key, expiration=3600):
        try:
            response = await s3_client.generate_presigned_url(
                ClientMethod = 'get_object',
                Params = {
                    'Bucket': self._bucket_name,
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