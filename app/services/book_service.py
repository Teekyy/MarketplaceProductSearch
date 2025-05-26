from ..exceptions import BookExistsError
from utils.logger import logger

class BookService:
    """
    BookService is a class that provides methods to retrieve and manipulate book data stored in a range of databases.
    """

    def __init__(self, db, s3_service):
        """
        Initializes the BookService with a database connection and an S3 service instance.
        """
        logger.info("Initializing BookService")
        self._db = db
        self._s3 = s3_service


    async def retrieve_books(self, page, limit):
        """
        Asynchronously retrieves a list of books from the database with pagination.

        Args:
            page (int): The page number to retrieve.
            limit (int): The number of books to retrieve per page.

        Returns:
            list: A list of books.
            None: If no books are found.
        """
        # Retrieve book metadata from db
        logger.debug(f"Retrieving books: page={page}, limit={limit}")
        skip = (page - 1) * limit
        cursor = self._db.books.find().skip(skip).limit(limit)
        books = list(cursor)
        logger.debug(f"Retrieved {len(books)} books from the database")
        
        # Fetch presigned URLs for book covers
        if books:
            logger.debug(f"Fetching presigned URLs for {len(books)} books")
            s3_keys = [book["thumbnail"] for book in books]
            presigned_urls = await self._s3.fetch_presigned_urls(s3_keys)
            for book, url in zip(books, presigned_urls):
                book["thumbnail"] = url
        
        return books
    

    async def retrieve_book(self, isbn_13):
        """
        Asynchronously retrieves a single book from the database.

        Args:
            isbn_13 (str): The ISBN-13 of the book to retrieve.
        
        Returns:
            dict: The book data.
            None: If the book is not found.
        """
        # Retrieve book metadata from db
        logger.debug(f"Retrieving book with ISBN-13: {isbn_13}")
        book = self._db.books.find_one({'isbn_13': isbn_13})

        # Fetch presigned URL for book cover
        if book:
            logger.debug(f"Book found: {book}. Fetching presigned URL for cover")
            presigned_url = await self._s3.fetch_presigned_url([book["thumbnail"]])
            book["thumbnail"] = presigned_url
        return book


    async def store_book(self, book):
        """
        Asynchronously stores a book in the database.

        Args:
            book (dict): The book data to store.

        Raises:
            BookExistsError: If the book already exists in the database.
        """
        # Check to see if the book already exists
        if self.book_exists(book['isbn_13']):
            raise BookExistsError(f"Book with ISBN-13 {book['isbn_13']} already exists")


    def book_exists(self, isbn_13):
        """
        Checks if a book exists in the database.

        Args:
            isbn_13 (str): The ISBN-13 of the book to check.
        
        Returns:
            bool: True if the book exists, False otherwise.
        """
        existing_book = self.db.books.find_one({'isbn_13': isbn_13})
        return True if existing_book else False