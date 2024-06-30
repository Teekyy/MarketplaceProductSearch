from dotenv import load_dotenv
import os
import time
import json
from tqdm import tqdm
from app.models.weighted_embedding_model import WeightedEmbeddingModel

load_dotenv()

model_name = os.getenv('HF_MODEL_NAME')
model = WeightedEmbeddingModel(model_name)

# Load book data
with open('data/books.json', 'r') as file:
    books = json.load(file)

# Measure performance over multiple runs for more accuracy
start = time.time()

embeddings = []
for book in books:
    embeddings.append(model.embed(book))
end = time.time()
total_time = end - start

print(f"Elapsed time: {total_time} seconds")

