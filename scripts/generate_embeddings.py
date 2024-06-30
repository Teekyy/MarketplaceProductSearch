from dotenv import load_dotenv
import os
import time
import json
from tqdm import tqdm
from app.models.weighted_embedding_model import WeightedEmbeddingModel

load_dotenv()

model_name = os.getenv('HF_MODEL_NAME')
model = WeightedEmbeddingModel(model_name, use_mps=True)

# Load book data
with open('data/books.json', 'r') as file:
    books = json.load(file)

def create_chunks(data, num_chunks):
    avg_chunk_size = data // num_chunks
    chunks = [data[i * avg_chunk_size : (i+1) * avg_chunk_size] for i in range(num_chunks)]

    if len(data) % num_chunks != 0:
        chunks.append(data[num_chunks * avg_chunk_size : ])

    return chunks

# Measure performance over multiple runs for more accuracy
start = time.time()

embeddings = model.embed(books)

end = time.time()
total_time = end - start

print(f"Elapsed time: {total_time} seconds")

