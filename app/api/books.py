
from flask import Blueprint, jsonify, request
from .schemas import BookSchema, BookUpdateSchema
from marshmallow import ValidationError
import os
from ..services.s3_service import S3Service
from ..services.book_service import BookService
from utils.logger import logger


books_api = Blueprint('books_api', __name__, url_prefix='/api/v1')
s3_service = S3Service()
book_service = BookService(s3_service)

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
    logger.info(f"GET /books request received with params: page={request.args.get('page')}, limit={request.args.get('limit')}")
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))

    # Validate input
    if page < 1 or limit < 1:
        logger.warning(f"Invalid parameters: page={page}, limit={limit}")
        return jsonify({
            "error": "Invalid parameters",
            "message": "Page and limit must be greater than 0"
        }), 400

    # Get books
    try:
        books = await book_service.retrieve_books(page, limit)
    except Exception as e:
        logger.exception(f"Error retrieving books: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
    
    logger.info(f"Returning {len(books)} books")
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
    logger.info(f"GET /book/{id} request received")
    if not id.isdigit() or len(id) != 13:
        logger.warning(f"Invalid ISBN-13 format: {id}")
        return jsonify({
            'error': 'Invalid ISBN-13 format.',
            'message': 'ISBN-13 must be a 13-digit number.'
        }), 400

    # Get book
    try:
        book = await book_service.retrieve_book(id)
        if not book:
            logger.warning(f"Book not found: {id}")
            return jsonify({'error': 'Book not found.'}), 404
    except Exception as e:
        logger.exception(f"Error retrieving book: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
    
    logger.info(f"Book found: {book}")
    return jsonify(book), 200


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
    logger.info(f"PUT /book/{id} request received with data: {request.json}")
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
        model = WeightedEmbeddingModel(use_mps=True)
        embedding = model.embed([book_data])[0]
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(host=os.getenv("PINECONE_INDEX_HOST"))
        result = index.upsert(vectors=[(book_data['isbn_13'], embedding)])
        # Upload to thumbnail to S3



    except ValidationError as e:
        logger.warning(f"Validation error: {e.messages}")
        return jsonify({'error': 'Validation Error', 'message': e.messages}), 400
    except Exception as e:
        logger.exception(f"Error adding book: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
    
    logger.info(f"Book added successfully: {book}")
    return jsonify(book), 200

    

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
    logger.info(f"PATCH /book/{id} request received with data: {request.json}")
    schema = BookUpdateSchema()

    # TODO: USE BOOK_SERVICE TO UPDATE BOOK
    try:
        data = schema.load(request.json)
        book = db.books.update_one(
            {'_id': ObjectId(id)},
            {'$set': data}
        )

    except ValidationError as e:
        logger.warning(f"Validation error: {e.messages}")
        return jsonify({'error': 'Validation Error', 'messages': e.messages}), 400
    except Exception as e:
        logger.exception(f"Error updating book: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
    
    logger.info(f"Book updated successfully: {book}")
    return jsonify(book), 200

     

@books_api.route('/book/<id>', methods=['DELETE'])
def delete_book(id):
    """
    Delete a book from the database.

    Query Parameters:
        id (str): The ISBN-13 of the book to delete.

    Returns:
        JSON: Success message
    """
    logger.info(f"DELETE /book/{id} request received")
    # TODO: USE BOOK_SERVICE TO DELETE BOOK
    try:
        result = db.books.delete_one({'isbn_13': id})
    except Exception as e:
        logger.exception(f"Error deleting book: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
    
    if result.deleted_count > 0:
        logger.info(f"Book deleted successfully with id {id}")
        return jsonify({'success': 'Book deleted successfully!'}), 204
    else:
        logger.warning(f"Book not found with id {id}")
        return jsonify({'error': 'Book not found.'}), 404