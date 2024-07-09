from sentence_transformers import SentenceTransformer
import torch
from dotenv import load_dotenv
import os
import numpy as np
import json
import time

class WeightedEmbeddingModel():
    def __init__(self, model, batch_size=64, use_mps=True):

        # Initialize device
        if torch.backends.mps.is_available() and use_mps:
            device = torch.device("mps")
            print("Using MPS device")
        else:
            device = torch.device("cpu")
            print("MPS device not found, using CPU")
        self._device = device

        # Load model and warm it up
        self._model = SentenceTransformer(f'sentence-transformers/{model}').to(device)
        self._model.encode('warmup', device=device)
        self._batch_size = batch_size

        # Define weights and normalize them
        self._weights = {
            'title': 2,
            'author': 2,
            'description': 4,
            'category': 1,
            'format': 0.5,
            'length': 0.5
        }
        self._normalize_weights()

    def embed(self, books):
        texts = []
        text_weights = []
        for book in books:
            for field, weight in self._weights.items():
                texts.append(book[field])
                text_weights.append(weight)

        embeddings = np.array(self._model.encode(
                texts,
                device=self._device,
                batch_size=self._batch_size
            ))

        weighted_embeddings = np.zeros((len(books), embeddings.shape[1]))

        num_weights = len(self._weights)
        for i, (embedding, weight) in enumerate(zip(embeddings, text_weights)):
            book_index = i // num_weights
            weighted_embeddings[book_index] += embedding * weight
        
        return weighted_embeddings.tolist()
        

    def _normalize_weights(self):
        total_weights = sum(self._weights.values())
        self._weights = {key: value / total_weights for key, value in self._weights.items()}
        




        