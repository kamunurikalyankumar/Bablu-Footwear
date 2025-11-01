from flask import Blueprint, request, jsonify
from app.models import Product, products_collection
from bson import ObjectId

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    category = request.args.get('category')
    if category:
        products = Product.find_by_category(category)
    else:
        products = Product.find_all()

    products_list = []
    for product in products:
        products_list.append({
            'id': str(product['_id']),
            'name': product['name'],
            'description': product['description'],
            'price': product['price'],
            'category': product['category'],
            'image_url': product['image_url'],
            'stock_quantity': product['stock_quantity']
        })

    return jsonify(products_list), 200

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.find_by_id(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    return jsonify({
        'id': str(product['_id']),
        'name': product['name'],
        'description': product['description'],
        'price': product['price'],
        'category': product['category'],
        'image_url': product['image_url'],
        'stock_quantity': product['stock_quantity']
    }), 200

@products_bp.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    if not query:
        return jsonify([]), 200

    # Simple search by name or description
    products = list(products_collection.find({
        '$or': [
            {'name': {'$regex': query, '$options': 'i'}},
            {'description': {'$regex': query, '$options': 'i'}}
        ]
    }))

    products_list = []
    for product in products:
        products_list.append({
            'id': str(product['_id']),
            'name': product['name'],
            'description': product['description'],
            'price': product['price'],
            'category': product['category'],
            'image_url': product['image_url'],
            'stock_quantity': product['stock_quantity']
        })

    return jsonify(products_list), 200

@products_bp.route('/by-name/<name>', methods=['GET'])
def get_product_by_name(name):
    product = products_collection.find_one({'name': name})
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    return jsonify({
        'id': str(product['_id']),
        'name': product['name'],
        'description': product['description'],
        'price': product['price'],
        'category': product['category'],
        'image_url': product['image_url'],
        'stock_quantity': product['stock_quantity']
    }), 200
