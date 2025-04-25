
from flask import Blueprint, jsonify, request
from .schemas import BookSchema, BookUpdateSchema
from marshmallow import ValidationError
from dotenv import load_dotenv
import os
from ..services.s3_service import S3Service
from ..extensions import mongo
from ..services.book_service import BookService

# Configure api, database, and services
books_api = Blueprint('books_api', __name__, url_prefix='/api/v1')
db = mongo.cx['marketplace']
s3_service = S3Service()
book_service = BookService(db, s3_service)

# PING
@books_api.route('/')
def get_app_health():
    return "Welcome to the Sci-Fi Book Catalog!"


# DEFAULT SHOW ALL BOOKS
@books_api.route('/books', methods=['GET'])
async def get_books():
    """
    Retrieves a list of books with pagination.
    
    Query Parameters:
        page (int): The page number to retrieve (default: 1).
        limit (int): The number of books to retrieve per page (default: 20).
    
    Returns:
        JSON: List of book objects with presigned URLs for thumbnails
    """
    # Parse input
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))

    # Validate input
    if page < 1 or limit < 1:
        return jsonify({
            "error": "Invalid parameters",
            "message": "Page and limit must be greater than 0"
        }), 400

    # Get books
    books = await book_service.retrieve_books(page, limit)

    return jsonify(books), 200


# CRUD ROUTES
@books_api.route('/book/<id>', methods=['GET'])
async def get_book(id):
    """
    Retrieve a single book.

    Query Parameters:
        id (str): The ISBN-13 of the book to retrieve.

    Returns:
        JSON: Book object with presigned URL for thumbnail
    """
    # Validate input
    if not id.isdigit() or len(id) != 13:
        return jsonify({
            'error': 'Invalid ISBN-13 format.',
            'message': 'ISBN-13 must be a 13-digit number.'
        }), 400

    # Get book
    try:
        book = await book_service.retrieve_book(id)
        if not book:
            return jsonify({'error': 'Book not found.'}), 404
        return jsonify(book), 200
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


@books_api.route('/book/<id>', methods=['PUT'])
async def add_book(id):
    """
    Add a new book to the database.

    Query Parameters:
        id (str): The ISBN-13 of the book to add.

    Request Body:
        JSON: Book metadata (title, author, genre, etc.)

    Returns:
        JSON: Book object with presigned URL for thumbnail
    """
    schema = BookSchema()

    try:
        # Validate and deserialize input
        request_data = request.json
        request_data['isbn_13'] = id
        book_data = schema.load(request_data)
        
        # TODO: USE BOOK_SERVICE TO STORE BOOK

        # Insert book metadata
        book = db.books.insert_one(book_data)
        # Embed book metadata
        load_dotenv()
        model = WeightedEmbeddingModel(use_mps=True)
        embedding = model.embed([book_data])[0]
        pc = Pinecone()
        index = pc.Index(host=os.getenv("PINECONE_INDEX_HOST"))
        result = index.upsert(vectors=[(book_data['isbn_13'], embedding)])
        # Upload to thumbnail to S3



        return jsonify(book), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation Error', 'message': e.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
    

@books_api.route('/book/<id>', methods=['PATCH'])
def update_book(id):
    """
    Update an existing book in the database.

    Query Parameters:
        id (str): The ISBN-13 of the book to update.

    Request Body:
        JSON: Partial book metadata (title, author, genre, etc.)

    Returns:
        JSON: Updated book object
    """
    schema = BookUpdateSchema()

    # TODO: USE BOOK_SERVICE TO UPDATE BOOK
    try:
        data = schema.load(request.json)
        book = db.books.update_one(
            {'_id': ObjectId(id)},
            {'$set': data}
        )

        return jsonify(book), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation Error', 'messages': e.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
     

@books_api.route('/book/<id>', methods=['DELETE'])
def delete_book(id):
    """
    Delete a book from the database.

    Query Parameters:
        id (str): The ISBN-13 of the book to delete.

    Returns:
        JSON: Success message
    """

    # TODO: USE BOOK_SERVICE TO DELETE BOOK
    try:
        result = db.books.delete_one({'isbn_13': id})

        if result.deleted_count > 0:
            return jsonify({'success': 'Book deleted successfully!'}), 204
        else:
            return jsonify({'error': 'Book not found.'}), 404
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500