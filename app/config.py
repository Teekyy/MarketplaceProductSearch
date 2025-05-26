import os

class Config:
    """
    Base configuration class.
    """
    MONGO_URI =os.getenv('MONGO_URI')
    MONGO_DB = os.getenv('MONGO_DB')

    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    HF_MODEL_NAME = os.getenv('HF_MODEL_NAME')

    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_INDEX_HOST = os.getenv('PINECONE_INDEX_HOST')

