from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Cart, carts_collection, Product
from bson import ObjectId

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    current_user_id = get_jwt_identity()
    cart_data = Cart.find_by_user_id(current_user_id)
    if not cart_data:
        return jsonify({'items': [], 'total': 0}), 200

    items = []
    total = 0
    for item in cart_data['items']:
        product = Product.find_by_id(item['product_id'])
        if product:
            item_total = product['price'] * item['quantity']
            total += item_total
            items.append({
                'product_id': item['product_id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'image_url': product['image_url'],
                'item_total': item_total
            })

    return jsonify({'items': items, 'total': total}), 200

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'message': 'Product ID is required'}), 400

    try:
        # Handle both ObjectId string and normal string formats
        try:
            if not ObjectId.is_valid(product_id):
                return jsonify({'message': 'Invalid product ID format'}), 400
            product = Product.find_by_id(product_id)
        except Exception as e:
            return jsonify({'message': f'Invalid product ID: {str(e)}'}), 400

        if not product:
            return jsonify({'message': 'Product not found'}), 404

        if product['stock_quantity'] < quantity:
            return jsonify({'message': 'Insufficient stock'}), 400
    except Exception as e:
        return jsonify({'message': 'Invalid product ID format'}), 400

    cart_data = Cart.find_by_user_id(current_user_id)
    if not cart_data:
        cart = Cart(current_user_id)
        cart.add_item(product_id, quantity)
        carts_collection.insert_one(cart.to_dict())
    else:
        cart = Cart(cart_data['user_id'], cart_data['items'])
        cart.add_item(product_id, quantity)
        carts_collection.update_one({'user_id': current_user_id}, {'$set': cart.to_dict()})

    return jsonify({'message': 'Item added to cart'}), 200

@cart_bp.route('/remove/<product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    current_user_id = get_jwt_identity()
    cart_data = Cart.find_by_user_id(current_user_id)
    if not cart_data:
        return jsonify({'message': 'Cart not found'}), 404

    cart = Cart(cart_data['user_id'], cart_data['items'])
    cart.remove_item(product_id)
    carts_collection.update_one({'user_id': current_user_id}, {'$set': cart.to_dict()})

    return jsonify({'message': 'Item removed from cart'}), 200

@cart_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_cart():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or quantity is None:
        return jsonify({'message': 'Product ID and quantity are required'}), 400

    cart_data = Cart.find_by_user_id(current_user_id)
    if not cart_data:
        return jsonify({'message': 'Cart not found'}), 404

    if quantity <= 0:
        cart = Cart(cart_data['user_id'], cart_data['items'])
        cart.remove_item(product_id)
    else:
        product = Product.find_by_id(product_id)
        if not product or product['stock_quantity'] < quantity:
            return jsonify({'message': 'Invalid quantity or insufficient stock'}), 400

        cart = Cart(cart_data['user_id'], cart_data['items'])
        cart.remove_item(product_id)
        cart.add_item(product_id, quantity)

    carts_collection.update_one({'user_id': current_user_id}, {'$set': cart.to_dict()})

    return jsonify({'message': 'Cart updated'}), 200
