
from flask import jsonify, request, abort
from app import app, db
from bson import ObjectId
from .schemas import BookSchema, BookUpdateSchema
from marshmallow import ValidationError
import asyncio
from .services.s3_utils import fetch_presigned_urls

# PING
@app.route('/')
def get_app_health():
    return "Welcome to the Sci-Fi Book Marketplace!"

# DEFAULT SHOW ALL BOOKS
@app.route('/books', methods=['GET'])
def get_all_books():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))

    if page < 1 or limit < 1:
        abort(400, description="Invalid 'page' or 'limit'. Both must be greater than 0.") 

    skip = (page - 1) * limit
    cursor = db.books.find().skip(skip).limit(limit)
    books = list(cursor)

    s3_keys = [book["thumbnail"] for book in books]
    presigned_urls = asyncio.run(fetch_presigned_urls(s3_keys))
    for book, url in zip(books, presigned_urls):
        book["thumbnail"] = url

    return jsonify(books)

# CRUD ROUTES
@app.route('/book/<id>', methods=['GET'])
def get_book(id):
    try:
        book = db.books.find_one({'_id': ObjectId(id)})
        if book:
            return jsonify(book), 200
        else:
            return jsonify({'error': 'Book not found.'}), 404
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
    
@app.route('/book', methods=['POST'])
def add_book():
    schema = BookSchema()

    try:
        data = schema.load(request.json)
        book = db.books.insert_one(data)

        return jsonify(book)
    except ValidationError as e:
        return jsonify({'error': 'Validation Error', 'messages': e.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
    

@app.route('/book/<id>', methods=['PUT'])
def update_book(id):
    schema = BookUpdateSchema()

    try:
        data = schema.load(request.json)
        book = db.books.update_one(
            {'_id': ObjectId(id)},
            {'$set': data}
        )

        return jsonify(book)
    except ValidationError as e:
        return jsonify({'error': 'Validation Error', 'messages': e.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
     

@app.route('/book/<id>', methods=['DELETE'])
def delete_book(id):
    try:
        result = db.books.delete_one({'_id': ObjectId(id)})

        if result.deleted_count > 0:
            return jsonify({'success': 'Book deleted successfully!'})
        else:
            return jsonify({'error': 'Book not found.'}), 404
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


# INSTANCE DEMONSTRATION ROUTES
@app.route('/instance', methods=['POST'])
def create_instance():
    pass

@app.route('/instance', methods=['DELETE'])
def delete_instance():
    pass

@app.route('/instance/<id>/start', methods=['POST'])
def start_traffic():
    pass

@app.route('/instance/<id>/stop', methods=['POST'])
def stop_traffic():
    pass
