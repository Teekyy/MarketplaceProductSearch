from dotenv import load_dotenv
import os
import time
import json
from tqdm import tqdm
from app.models.weighted_embedding_model import WeightedEmbeddingModel
import math

def create_chunks(data, chunk_size):
    num_chunks = math.ceil(len(data) / chunk_size)
    chunks = [data[i * chunk_size : (i+1) * chunk_size] for i in range(num_chunks)]

    return chunks

if __name__ == '__main__':
    load_dotenv()
    
    # Load book data
    with open('data/books.json', 'r') as file:
        books = json.load(file)

    chunk_size = 1800  # Size of each chunk
    batch_size = 80 # Size of batch for encoder model

    model_name = os.getenv('HF_MODEL_NAME')
    model = WeightedEmbeddingModel(model_name, batch_size=batch_size, use_mps=True)

    # Measure performance over multiple runs for more accuracy
    start = time.time()
    chunks = create_chunks(books, chunk_size=chunk_size)
    
    embeddings = []
    for chunk in tqdm(chunks, total=len(chunks), desc="Processing chunks", unit="chunk"):
        embeddings.extend(model.embed(chunk))

    end = time.time()
    total_time = end - start

    print(f"Elapsed time: {total_time} seconds")
    print(f"Embeddings generated: {len(embeddings)}")

