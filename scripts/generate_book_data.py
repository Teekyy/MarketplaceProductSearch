import requests
import json
import os
import random
from itertools import product
from dotenv import load_dotenv
from tqdm import tqdm

def main():
    load_dotenv()

    # API settings
    api_url = os.getenv("GOOGLE_BOOKS_API_URL")

    # Data definitions
    categories = ["Romance", "Thriller", "Comics", "Mystery", "Action Adventure"]
    lengths = ["Short Read", "Standard Length", "Long Read"]
    formats = ["Ebook", "Audiobook", "Paperback"]
    published_year_bins = {
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

    # Main execution loop
    all_books = []
    MAX_NUM_BOOKS = 100
    processed_books = set()

    combinations = product(categories, lengths, formats)
    for category, length, book_format in tqdm(combinations, total=len(list(combinations)), desc="Generating Book Data"):
        if len(all_books) >= MAX_NUM_BOOKS:
            break

        query = f'Sci-Fi {category} {length} {book_format}'
        result = query_google_books(query, api_url)
        metadata = {
            'category': category,
            'length': length,
            'format': book_format,
            'published_year_bins': published_year_bins
        }

        books = process_books(result, metadata, processed_books)
        all_books.extend(books)

    # Print the number of books fetched and details of the first few
    print(f"Total books fetched: {len(all_books)}")
    books_json = json.dumps(all_books, indent=4)

    # Save JSON string to file
    with open('data/books2.json', 'w') as file:
        json.dump(all_books, file, indent=4)

# Function to query Google Books API
def query_google_books(query, api_url):
    params = {
        'q': query,
        'maxResults': 10  # Limit results to top 10
    }
    response = requests.get(url=api_url, params=params)
    response.raise_for_status()  # Raise an exception for bad requests
    return response.json()

# Function to process books
def process_books(books_data, other_metadata, processed_books):
    books = []

    if not other_metadata:
        print('You forgot to pass in metadata for the books.')
        return books

    for item in books_data.get('items', []):
        if len(books) >= 2:
            break

        bins = [info["years"] for info in other_metadata["published_year_bins"].values()]
        bin_weights =[info["weight"] for info in other_metadata["published_year_bins"].values()]
        chosen_bin = random.choices(bins, weights=bin_weights, k=1)[0]
        published_year = random.randint(*chosen_bin)

        volume_info = item.get('volumeInfo', {})
        description = volume_info.get('description')
        thumbnail = volume_info.get('imageLinks', {}).get('thumbnail')
        title = volume_info.get('title')
        author = volume_info.get('authors')[0]

        title_author = f'{title.lower()}_{author.lower()}'
        if title_author in processed_books:
            continue
        processed_books.add(title_author)

        if description and thumbnail:  # Ensure both description and thumbnail exist
            books.append({
                'title': title,
                'author': author,
                'description': description,
                'category': other_metadata.get('category'),
                'format': other_metadata.get('format'),
                'length': other_metadata.get('length'),
                'published_year': published_year,
                'thumbnail': thumbnail
            })
    return books


if __name__ == '__main__':
    main()