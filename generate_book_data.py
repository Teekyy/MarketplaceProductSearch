import requests
import json
import os
import random
from itertools import product
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# API settings
api_url = os.getenv("GOOGLE_BOOKS_API_URL")

# Data definitions
categories = ["Romance", "Thriller", "Comics", "Mystery", "Action Adventure"]
lengths = ["Short Read", "Standard Length", "Long Read"]
formats = ["Ebook", "Audiobook", "Paperback"]
published_date_bins = {
    'old': {
        'years': (1970, 1999),
        'weight': 1
    },
    'recent': {
        'years': (2000, 2020),
        'weight': 10
    },
    'new': {
        'years': (2021, 2024),
        'weight': 5
    }
}

# Function to query Google Books API
def query_google_books(query):
    params = {
        'q': query,
        'maxResults': 5  # Limit results to top 5
    }
    response = requests.get(url=api_url, params=params)
    response.raise_for_status()  # Raise an exception for bad requests
    return response.json()

# Function to process books
def process_books(books_data, other_metadata):
    if not other_metadata:
        print('You forgot to pass in metadata for the books.')
        return

    books = []
    for item in books_data.get('items', []):
        if len(books) >= 2:
            break

        volume_info = item.get('volumeInfo', {})
        description = volume_info.get('description')
        thumbnail = volume_info.get('imageLinks', {}).get('thumbnail')

        bins = [info["years"] for info in other_metadata["published_date_bins"].values()]
        bin_weights =[info["weight"] for info in other_metadata["published_date_bins"].values()]
        chosen_bin = random.choices(bins, weights=bin_weights, k=1)[0]
        published_date = random.randint(*chosen_bin)

        if description and thumbnail:  # Ensure both description and thumbnail exist
            books.append({
                'title': volume_info.get('title'),
                'author': volume_info.get('authors')[0],
                'description': description,
                'category': other_metadata.get('category'),
                'format': other_metadata.get('format'),
                'length': other_metadata.get('length'),
                'published_date': published_date,
                'thumbnail': thumbnail
            })
    return books

# Main execution loop
all_books = []
MAX_NUM_BOOKS = 10

for category, length, book_format in tqdm(product(categories, lengths, formats), total=len(categories)*len(lengths)*len(formats), desc="Querying Google Books"):
    if len(all_books) >= MAX_NUM_BOOKS:
        break

    query = f'Sci-Fi {category} {length} {book_format}'
    result = query_google_books(query)
    metadata = {
        'category': category,
        'length': length,
        'format': book_format,
        'published_date_bins': published_date_bins
    }

    books = process_books(result, metadata)
    all_books.extend(books)

# Print the number of books fetched and details of the first few
print(f"Total books fetched: {len(all_books)}")
books_json = json.dumps(all_books, indent=4)

# Save JSON string to file
with open('books.json', 'w') as f:
    json.dump(all_books, f, indent=4)


