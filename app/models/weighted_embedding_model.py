from sentence_transformers import SentenceTransformer
import torch
from dotenv import load_dotenv
import os
import numpy as np
import json
import time

class WeightedEmbeddingModel():
    def __init__(self, model, use_mps=True):

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

    def embed(self, book):
        weighted_embedding = np.zeros(self._model.get_sentence_embedding_dimension())

        for field, weight in self._weights.items():
            field_text = str(book[field])
            field_embedding = np.array(self._model.encode(field_text, device=self._device))
            
            weighted_embedding += weight * field_embedding
        
        return weighted_embedding
        

    def _normalize_weights(self):
        total_weights = sum(self._weights.values())
        self._weights = {key: value / total_weights for key, value in self._weights.items()}
        




        