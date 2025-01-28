
from flask import Blueprint, jsonify, request
from bson import ObjectId
from .schemas import BookSchema, BookUpdateSchema
from marshmallow import ValidationError
import asyncio
from dotenv import load_dotenv
import os
from app.models.weighted_embedding_model import WeightedEmbeddingModel
from pinecone import Pinecone
from pinecone.exceptions import PineconeException
from ..services.s3_service import S3Service
from ..extensions import mongo
from ..services.book_service import BookService

books_api = Blueprint('books_api', __name__, url_prefix='/api/v1')
db = mongo.cx['marketplace']
book_service = BookService(db)

# PING
@books_api.route('/')
def get_app_health():
    return "Welcome to the Sci-Fi Book Marketplace!"


# DEFAULT SHOW ALL BOOKS
@books_api.route('/books', methods=['GET'])
def get_all_books():
    # Parse input
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))

    if page < 1 or limit < 1:
        return jsonify({"error": "Invalid 'page' or 'limit'. Both must be greater than 0."}), 400

    # Retrieve book metadata
    skip = (page - 1) * limit
    cursor = db.books.find().skip(skip).limit(limit)
    books = list(cursor)
    if not books:
        return jsonify({"message": "No books found."}), 404

    # Fetch presigned URLs for book covers
    s3_service = S3Service()
    s3_keys = [book["thumbnail"] for book in books]
    presigned_urls = asyncio.run(s3_service.fetch_presigned_urls(s3_keys))
    for book, url in zip(books, presigned_urls):
        book["thumbnail"] = url

    return jsonify(books), 200


# CRUD ROUTES
@books_api.route('/book/<id>', methods=['GET'])
def get_book(id):
    try:
        book = db.books.find_one({'isbn_13': id})
        if book:
            s3_service = S3Service()
            presigned_url = asyncio.run(s3_service.get_presigned_url([book["thumbnail"]]))
            book["thumbnail"] = presigned_url
            return jsonify(book), 200
        else:
            return jsonify({'error': 'Book not found.'}), 404
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


@books_api.route('/book/<id>', methods=['PUT'])
def add_book(id):
    schema = BookSchema()

    try:
        # Validate and deserialize input
        request_data = request.json
        request_data['isbn_13'] = id
        book_data = schema.load(request_data)

        # Check to see if the book already exists
        existing_book = db.books.find_one({'isbn_13': id})
        if existing_book:
            return jsonify({'error': 'Book already exists.'}), 400
        
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
    schema = BookUpdateSchema()

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
    try:
        result = db.books.delete_one({'isbn_13': id})

        if result.deleted_count > 0:
            return jsonify({'success': 'Book deleted successfully!'}), 204
        else:
            return jsonify({'error': 'Book not found.'}), 404
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500