from dotenv import load_dotenv
import os
import time
import json
from tqdm import tqdm
from itertools import product
from app.models.weighted_embedding_model import WeightedEmbeddingModel
from tabulate import tabulate

def create_chunks(data, num_chunks):
    avg_chunk_size = len(data) // num_chunks
    chunks = [data[i * avg_chunk_size : (i+1) * avg_chunk_size] for i in range(num_chunks)]

    if len(data) % num_chunks != 0:
        chunks.append(data[num_chunks * avg_chunk_size : ])

    return chunks

def generate_chunks(books, n, chunk_size):
    total_books = len(books) * n

    for start in range(0, total_books, chunk_size):
        batch = []
        for i in range(start, min(start + chunk_size, total_books)):
            batch.append(books[i % len(books)])
        yield batch

def run_experiment(books, model_name, n, chunk_size, batch_size, use_mps):
    model = WeightedEmbeddingModel(model_name, use_mps=use_mps, batch_size=batch_size)

    start = time.time()
    
    batches = generate_chunks(books, n=n, chunk_size=chunk_size)
    total_books = len(books) * n
    total_batches = (total_books + chunk_size - 1) // chunk_size  # Ceiling division
    
    embeddings = []
    for batch in tqdm(batches, total=total_batches, desc=f"Chunks: {chunk_size}, Batch: {batch_size}", unit="chunk"):
        embeddings.extend(model.embed(batch))
    
    end = time.time()
    return end - start

if __name__ == '__main__':
    load_dotenv()

    model_name = os.getenv('HF_MODEL_NAME')
    
    # Load book data
    with open('data/books.json', 'r') as file:
        books = json.load(file)

    # Experiment parameters
    chunk_sizes = [100, 500, 1000, 1500, 2000]
    batch_sizes = [32, 64, 128, 256]
    n = 100  # Number of times to repeat the book list
    use_mps = True  # Use MPS (GPU) on the M2 chip

    results = []

    # Run experiments
    for chunk_size, batch_size in product(chunk_sizes, batch_sizes):
        try:
            elapsed_time = run_experiment(books, model_name, n, chunk_size, batch_size, use_mps)
            results.append((chunk_size, batch_size, elapsed_time))
            print(f"Chunk size: {chunk_size}, Batch size: {batch_size}, Elapsed time: {elapsed_time} seconds")
        except Exception as e:
            print(f"Error with Chunk size: {chunk_size}, Batch size: {batch_size} - {e}")

    # Print the results in a tabular format
    headers = ["Chunk Size", "Batch Size", "Elapsed Time (s)"]
    table = tabulate(results, headers, tablefmt="grid")
    print(table)

    # Find the best configuration
    best_config = min(results, key=lambda x: x[2])
    print(f"\nBest configuration - Chunk size: {best_config[0]}, Batch size: {best_config[1]}, Elapsed time: {best_config[2]} seconds")
