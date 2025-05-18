import os
import asyncio
import aioboto3
import botocore.exceptions
from utils.logger import logger

class S3Service:
    """
    S3Service is a class that provides methods to interact with AWS S3.
    """

    def __init__(self):
        """
        Creates an instance of S3Service and an async session with AWS.
        """
        logger.info("Initializing S3Service")
        self._bucket_name = os.getenv('AWS_BUCKET_NAME')

        # Create session
        self.session = aioboto3.Session(
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )


    async def get_client(self):
        """
        Returns the S3 client.
        """
        return self.session.client('s3')


    async def fetch_presigned_urls(self, s3_keys):
        """
        Asynchronously fetches presigned URLs for a list of S3 keys.

        Args:
            s3_keys (list): A list of S3 keys.

        Returns:
            list: A list of presigned URLs.
        """
        logger.debug(f"Fetching presigned URLs for {len(s3_keys)} keys")
        async with await self.get_client as s3_client:
            tasks = []
            for s3_key in s3_keys:
                task = asyncio.create_task(self._generate_presigned_url(s3_client, s3_key))
                tasks.append(task)

            return await asyncio.gather(*tasks)
        
    
    async def fetch_presigned_url(self, s3_key):
        """
        Asynchronously fetches a single presigned URL for a given S3 keys.

        Args:
            s3_key (str): The S3 key.

        Returns:
            str: The presigned URL.
        """
        logger.debug(f"Fetching presigned URL for key: {s3_key}")
        async with await self.get_client as s3_client:
            return await self._generate_presigned_url(s3_client, s3_key)


    async def _generate_presigned_url(self, s3_client, s3_key, expiration=3600):
        """
        Generates a presigned URL for a given S3 key.

        Args:
            s3_client: The S3 client.
            s3_key (str): The S3 key.
            expiration (int): The expiration time in seconds.

        Returns:
            str: The presigned URL.
        """
        logger.debug(f"Generating presigned URL for key: {s3_key}")
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
            logger.error(f"An AWS service error occured while generating presigned URL for s3 key {s3_key}: {e}")
        except Exception as e:
            logger.error(f"An error occured while generating presigned URL for s3 key {s3_key}: {e}")

        return None