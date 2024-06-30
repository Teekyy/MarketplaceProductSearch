from sentence_transformers import SentenceTransformer
import torch
from dotenv import load_dotenv
import os
import time
import numpy as np
import json

load_dotenv()

use_mps = False

# Check if MPS is available
if torch.backends.mps.is_available() and use_mps:
    device = torch.device("mps")
    print("Using MPS device")
else:
    device = torch.device("cpu")
    print("MPS device not found, using CPU")

# Load model
model_name = os.getenv('HF_MODEL_NAME')
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').to(device)

# Load book data
with open('data/books.json', 'r') as file:
    books = json.load(file)

# warm up model
_ = model.encode(str(books[0]["description"]), device=device)

# Function to get embeddings
def generate_embedding(book):
    weights = {
        'title': 2,
        'author': 2,
        'description': 4,
        'category': 1,
        'format': 0.5,
        'length': 0.5
    }
    total_weights = sum(weights.values())

    weighted_embedding = np.zeros(model.get_sentence_embedding_dimension())

    for field, weight in weights.items():
        field_text = str(book[field])
        field_embedding = np.array(model.encode(field_text, device=device).tolist())

        weighted_embedding += (weight / total_weights) * field_embedding

    return weighted_embedding

def custom_weighted_model(books):
    pass


# Measure performance over multiple runs for more accuracy
start = time.time()

embeddings = []
for book in books:
    embeddings.append(generate_embedding(book))
end = time.time()
total_time = end - start

print(f"Elapsed time: {total_time} seconds")

