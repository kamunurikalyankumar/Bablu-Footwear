from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Product, products_collection, Order, users_collection, orders_collection
from bson import ObjectId

admin_bp = Blueprint('admin', __name__)

def admin_required():
    current_user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': current_user_id})
    if not user or not user.get('is_admin', False):
        return False
    return True

@admin_bp.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    category = data.get('category')
    image_url = data.get('image_url')
    stock_quantity = data.get('stock_quantity')

    if not all([name, description, price, category, image_url, stock_quantity]):
        return jsonify({'message': 'All fields are required'}), 400

    product = Product(name, description, price, category, image_url, stock_quantity)
    product_id = products_collection.insert_one(product.to_dict()).inserted_id

    return jsonify({'message': 'Product added successfully', 'product_id': str(product_id)}), 201

@admin_bp.route('/products/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    data = request.get_json()
    update_data = {}
    for field in ['name', 'description', 'price', 'category', 'image_url', 'stock_quantity']:
        if field in data:
            update_data[field] = data[field]

    if not update_data:
        return jsonify({'message': 'No fields to update'}), 400

    result = products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': update_data})
    if result.matched_count == 0:
        return jsonify({'message': 'Product not found'}), 404

    return jsonify({'message': 'Product updated successfully'}), 200

@admin_bp.route('/products/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    result = products_collection.delete_one({'_id': ObjectId(product_id)})
    if result.deleted_count == 0:
        return jsonify({'message': 'Product not found'}), 404

    return jsonify({'message': 'Product deleted successfully'}), 200

@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    orders = Order.find_all()
    orders_list = []
    for order in orders:
        user = users_collection.find_one({'_id': order['user_id']})
        orders_list.append({
            'id': str(order['_id']),
            'user': user['username'] if user else 'Unknown',
            'items': order['items'],
            'total_amount': order['total_amount'],
            'shipping_address': order['shipping_address'],
            'payment_status': order['payment_status'],
            'order_status': order['order_status'],
            'created_at': order['created_at']
        })

    return jsonify(orders_list), 200

@admin_bp.route('/orders/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    data = request.get_json()
    new_status = data.get('order_status')

    if not new_status:
        return jsonify({'message': 'Order status is required'}), 400

    result = orders_collection.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {'order_status': new_status}}
    )
    if result.matched_count == 0:
        return jsonify({'message': 'Order not found'}), 404

    return jsonify({'message': 'Order status updated successfully'}), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    users = list(users_collection.find())
    users_list = []
    for user in users:
        users_list.append({
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'is_admin': user.get('is_admin', False),
            'created_at': user['created_at']
        })

    return jsonify(users_list), 200
