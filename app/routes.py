
from flask import jsonify, request, abort
from app import app, db
from bson import ObjectId

ALLOWED_PROPERTIES = set('title', 'author', 'description', 'category', 'format', 'length', 'published_date', 'thumbnail')

@app.route('/')
def get_app_health():
    return "Welcome to the Sci-Fi Book Marketplace!"

@app.route('/books', methods=['GET'])
def get_books():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))

    if page < 1 or limit < 1:
        abort(400, description="Invalid 'page' or 'limit'. Both must be greater than 0.") 

    skip = (page - 1) * limit
    books = db.books.find().skip(skip).limit(limit)
    return jsonify([book for book in books])

@app.route('/book/<id>', methods=['GET'])
def get_book(id):
    try:
        book = db.books.find_one(ObjectId(id))
        if book:
            return jsonify(book), 200
        else:
            return jsonify({'error': 'Book not found.'}), 404
    except Exception as e:
        return jsonify({'error': 'Invalid ID format.'}), 400
    
@app.route('/book', methods=['POST'])
def add_book():
    data = request.json

    

    book = {
        'title': data['title']
    }

@app.route('/book/<id>', methods=['PUT'])
def update_book():
    pass

@app.route('/book/<id>', methods=['DELETE'])
def delete_book():
    pass

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
