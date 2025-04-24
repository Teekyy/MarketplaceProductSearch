from sentence_transformers import SentenceTransformer
import torch
import os
from dotenv import load_dotenv
import numpy as np

class WeightedEmbeddingModel():
    """
    A class to create weighted embeddings for book data using a SentenceTransformer model.
    Weights are applied to different fields of the book data to create a combined embedding.
    """

    def __init__(self, batch_size=64, use_mps=True):
        """
        Initializes the WeightedEmbeddingModel with a SentenceTranformer model and warms it up. Sets the device to use mps if available.

        Args:
            batch_size (int): The batch size for encoding.
            use_mps (bool): Flag to use MPS device if available.
        """
        load_dotenv()
        model_name = os.getenv("HF_MODEL_NAME")

        # Initialize device
        if torch.backends.mps.is_available() and use_mps:
            device = torch.device("mps")
            print("Using MPS device")
        else:
            device = torch.device("cpu")
            print("MPS device not found, using CPU")
        self._device = device

        # Load model and warm it up
        self._model = SentenceTransformer(f'sentence-transformers/{model_name}').to(device)
        self._model.encode('warmup', device=device)
        self._batch_size = batch_size

        # Define weights and normalize them
        self._weights = {
            'title': 2,
            'author': 2,
            'description': 4,
            'category': 1,
            'format': 0.5,
            'length': 0.5,
            'published': 0.5
        }
        self._normalize_weights()


    def embed(self, books):
        """
        Creates weighted embeddings for a list of books.

        Args:
            books (list): A list of book dictionaries.

        Returns:
            list: A list of vectors representing the weighted embeddings of the books.
        """
        # Flattened array that contains texts from each field for all the books. 
        # Ex: ['title1', 'author1', 'description1', ..., 'title2', 'author2', 'description2', ...]
        # Dimensions: (books * num_fields,)
        texts = []
        # Contains the associated normalized weights for each text in the texts array.
        # Dimsensions: (books * num_fields,)
        text_weights = []

        # Populate the texts and text_weights arrays by iterating through each book its fields
        for book in books:
            for field, weight in self._weights.items():
                if field == 'published':
                    # Get the book's age category instead of the published year. When searching for a book, we want to search for the age category, not the year.
                    texts.append(self._get_book_age_category(book))
                else:
                    texts.append(book[field])
                text_weights.append(weight)

        # Encode the texts using the SentenceTransformer model
        # Dimensions: (books * num_fields, embedding_dim)
        embeddings = np.array(self._model.encode(
                texts,
                device=self._device,
                batch_size=self._batch_size
            ))

        # Create a new array to store the combined weighted embeddings
        # Dimensions: (books, embedding_dim)
        weighted_embeddings = np.zeros((len(books), embeddings.shape[1]))

        # Iterate through the embeddings and weights to create the weighted embeddings
        num_weights = len(self._weights)
        for i, (embedding, weight) in enumerate(zip(embeddings, text_weights)):
            book_index = i // num_weights
            weighted_embeddings[book_index] += embedding * weight
        
        return weighted_embeddings.tolist()
        

    def _normalize_weights(self):
        """
        Normalizes the weights so that they sum to 1.
        This is done to ensure that the weights are relative to each other and can be interpreted as probabilities.
        """
        total_weights = sum(self._weights.values())
        self._weights = {key: value / total_weights for key, value in self._weights.items()}
        

    def _get_book_age_category(self, book):
        """
        Determines the age category of a book based on its published year.

        Args:
            book (dict): A dictionary representing a book.

        Returns:
            str: The age category of the book ('old', 'recent', 'new').
        """
        age_to_year_mapping = {
            'old': (float('-inf'), 1999),
            'recent': (2000, 2020),
            'new': (2021, float('inf'))
        }

        # Get the published year from the book dictionary, defaulting to 2000 if not present
        published_year = book.get('published_year', 2000)

        # Check if the published year falls within any of the defined age categories
        for age, (start_year, end_year) in age_to_year_mapping.items():
            if start_year <= published_year <= end_year:
                return age

        # Return 'recent' as safety measure
        return 'recent'