import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json
import os
import random
from itertools import product
from dotenv import load_dotenv
from tqdm import tqdm
import time

def generate_book_data(file_path):
    """
    Generates book data by querying the Google Books API.
    Uses concurrent fetching to improve performance and saves the fetched data to a JSON file.

    Args:
        file_path (str): The path to the JSON file to write data to.
    """

    load_dotenv()

    # API settings
    api_url = os.getenv("GOOGLE_BOOKS_API_URL")

    # Configurations ----------------------
    MAX_NUM_BOOKS = 100 # Maximum number of books to generate data for
    # Data definitions
    categories = ["Cyberpunk", "Thriller", "Comics", "Mystery", "Action Adventure"]
    lengths = ["Short Read", "Standard Length", "Long Read"]
    formats = ["Ebook", "Audiobook", "Paperback"]
    # Distribution weights for how published years should be assigned for each book
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
    start = time.time()

    all_books = []
    combinations = product(categories, lengths, formats)

    # Used to keep track of previously processed books so there aren't duplicate title-author combos
    # Lock is used to ensure thread-safe access to shared resources
    processed_books = set()
    lock = threading.Lock()
    
    # Concurrent data fetching
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks to executor for fetching book data concurrently
        futures = [executor.submit(fetch_book_data, combo, api_url, published_year_bins, processed_books, lock) for combo in combinations]

        # Process completed futures are they complete
        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating Book Data"):
            if len(all_books) >= MAX_NUM_BOOKS:
                break
            
            books = future.result()
            if books:
                all_books.extend(books)

    # Calculate elapsed time
    end = time.time()
    time_elapsed = end - start
    print(f'Time elapsed: {time_elapsed} seconds')

    print(f"Total books fetched: {len(all_books)}")
    # Save book data to file as JSON
    with open(file_path, 'w') as file:
        json.dump(all_books, file, indent=4)

def fetch_book_data(combination, api_url, published_year_bins, processed_books, lock):
    """
    Fetches book data from the Google Books API for a given combination of category, length, and format.
    
    Args:
        combination (tuple): A combination of category, length, and format.
        api_url (str): The URL of the Google Books API.
        published_year_bins (dict): The distribution weights for published years.
        processed_books (set): A set to keep track of processed books to avoid duplicates.
        lock (threading.Lock): A lock to ensure thread-safe access to shared resources.
    
    Returns:
        list: A list of processed books.
    """

    category, length, book_format = combination

    # Construct search query to search Google Books API
    query = f'Sci-Fi {category} {length} {book_format}'

    # Fetch data
    results = query_google_books(query, api_url)

    # Additional metadata to be included with the fetched data
    metadata = {
        'category': category,
        'length': length,
        'format': book_format,
        'published_year_bins': published_year_bins
    }

    # Process fetched data if there is any
    if results:
        return process_books(results, metadata, processed_books, lock)
    else:
        return []


def query_google_books(query, api_url):
    """
    Queries the Google Books API with a given query string and API URL.
    
    Args:
        query (str): The query string for the Google Books API.
        api_url (str): The URL of the Google Books API.
    
    Returns:
        dict or None: The JSON response from the API if successful, otherwise None.
    """

    params = {
        'q': query,
        'maxResults': 10  # Limit results to top 10
    }
    
    # Make request to Google Books API
    try:
        response = requests.get(url=api_url, params=params)
        response.raise_for_status()  # Raise an exception for bad requests
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None
    except Exception as e:
        print(f"An error occurred: {err}")
        return None


def process_books(books_data, other_metadata, processed_books, lock):
    """
    Processes book data from the Google Books API response, adding metadata and ensuring no duplicates.
    
    Args:
        books_data (dict): The JSON response from the Google Books API.
        other_metadata (dict): Additional metadata to be included with each book.
        processed_books (set): A set to keep track of processed books to avoid duplicates.
        lock (threading.Lock): A lock to ensure thread-safe access to shared resources.
    
    Returns:
        list: A list of processed book entries.
    """

    books = []
    MAX_NUM_BOOK_PER_COMBO = 2 # Maximum number of books to add for each combination of category, length, and book format

    # Check if metadata was passed
    if not other_metadata:
        print('You forgot to pass in metadata for the books.')
        return books

    # Process each item in response from Google Books API
    for item in books_data.get('items', []):
        # Check if max number of books reached
        if len(books) >= MAX_NUM_BOOK_PER_COMBO:
            break

        # Generate published year for book
        bins = [info["years"] for info in other_metadata["published_year_bins"].values()]
        bin_weights =[info["weight"] for info in other_metadata["published_year_bins"].values()]
        chosen_bin = random.choices(bins, weights=bin_weights, k=1)[0]
        published_year = random.randint(*chosen_bin)

        # Extract data from response
        volume_info = item.get('volumeInfo', {})
        description = volume_info.get('description')
        thumbnail = volume_info.get('imageLinks', {}).get('thumbnail')
        title = volume_info.get('title')
        isbn_13 = next(
            (id["identifier"] for id in volume_info.get('industryIdentifiers', []) if id["type"] == "ISBN_13"),
            None
        )

        # Ensure data includes an author; skip if missing
        authors = volume_info.get('authors')
        if not authors:
            continue
        author = authors[0]

        # Ensure title-author combination has not been processed already; skip if it has
        title_author = f'{title.lower()}_{author.lower()}'
        with lock:
            if title_author in processed_books:
                continue
            processed_books.add(title_author)

        # Ensure description, thumbnail, and isbn_13 exist before adding book data
        if description and thumbnail and isbn_13:
            books.append({
                'isbn': isbn_13,
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
    generate_book_data('data/books.json')