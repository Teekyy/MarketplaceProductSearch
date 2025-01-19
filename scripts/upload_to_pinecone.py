from dotenv import load_dotenv
import json
import os
import time
from tqdm import tqdm
from app.models.weighted_embedding_model import WeightedEmbeddingModel
import math
from pinecone import Pinecone

def upload_data(file_path):
    load_dotenv()
    
    # Load book data from JSON file
    with open(file_path, 'r') as file:
        books = json.load(file)

    # Initialize Pinecone
    pc = Pinecone()
    index = pc.Index(host=os.getenv("INDEX_HOST"))

    chunk_size = 1000  # Size of each chunk
    batch_size = 64 # Size of batch for encoder model

    model_name = os.getenv('HF_MODEL_NAME')
    model = WeightedEmbeddingModel(model_name, batch_size=batch_size, use_mps=True)

    # Split data into chunks and embed each chunk
    chunks = create_chunks(books, chunk_size=chunk_size)
    
    embeddings = []
    for chunk in tqdm(chunks, total=len(chunks), desc="Processing chunks", unit="chunk"):
        embeddings.extend(model.embed(chunk))

    vectors = [
        (book["isbn_13"], embedding)
        for book, embedding in zip(books, embeddings)
    ]

    try:
        result = index.upsert(vectors=vectors)
        print(f"Upserted {result['upserted_count']} documents.")
    except pc.core.client.exceptions.ConnectionError as e:
        print("Connection error:", e)
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def create_chunks(data, chunk_size):
    num_chunks = math.ceil(len(data) / chunk_size)
    chunks = [data[i * chunk_size : (i+1) * chunk_size] for i in range(num_chunks)]

    return chunks


if __name__ == '__main__':
    start = time.time()
    upload_data('data/books.json')
    end = time.time()
    time_elapsed = end - start
    print(f'Time elapsed: {time_elapsed} seconds')