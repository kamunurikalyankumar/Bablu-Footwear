from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Order, orders_collection, Cart, Product, carts_collection, products_collection
import stripe
import os

orders_bp = Blueprint('orders', __name__)

# Set your Stripe secret key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_stripe_secret_key_here')

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    orders = Order.find_by_user_id(current_user_id)
    orders_list = []
    for order in orders:
        orders_list.append({
            'id': str(order['_id']),
            'items': order['items'],
            'total_amount': order['total_amount'],
            'shipping_address': order['shipping_address'],
            'payment_status': order['payment_status'],
            'order_status': order['order_status'],
            'created_at': order['created_at']
        })

    return jsonify(orders_list), 200

@orders_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    shipping_address = data.get('shipping_address')

    if not shipping_address:
        return jsonify({'message': 'Shipping address is required'}), 400

    cart_data = Cart.find_by_user_id(current_user_id)
    if not cart_data or not cart_data['items']:
        return jsonify({'message': 'Cart is empty'}), 400

    items = []
    total_amount = 0
    for item in cart_data['items']:
        product = Product.find_by_id(item['product_id'])
        if not product or product['stock_quantity'] < item['quantity']:
            return jsonify({'message': f'Insufficient stock for {product["name"] if product else "unknown product"}'}), 400

        item_total = product['price'] * item['quantity']
        total_amount += item_total
        items.append({
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'price': product['price']
        })

    # Create Stripe payment intent
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Amount in cents
            currency='usd',
            metadata={'user_id': current_user_id}
        )
    except Exception as e:
        return jsonify({'message': 'Payment processing error', 'error': str(e)}), 500

    # Create order
    order = Order(current_user_id, items, total_amount, shipping_address, 'pending')
    order_id = orders_collection.insert_one(order.to_dict()).inserted_id

    # Clear cart
    carts_collection.delete_one({'user_id': current_user_id})

    return jsonify({
        'order_id': str(order_id),
        'client_secret': intent.client_secret,
        'total_amount': total_amount
    }), 200

@orders_bp.route('/confirm-payment', methods=['POST'])
@jwt_required()
def confirm_payment():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    order_id = data.get('order_id')
    payment_intent_id = data.get('payment_intent_id')

    if not order_id or not payment_intent_id:
        return jsonify({'message': 'Order ID and Payment Intent ID are required'}), 400

    # Verify payment with Stripe
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status == 'succeeded':
            # Update order status
            from bson import ObjectId
            orders_collection.update_one(
                {'_id': ObjectId(order_id), 'user_id': current_user_id},
                {'$set': {'payment_status': 'paid', 'order_status': 'processing'}}
            )

            # Update product stock
            order = orders_collection.find_one({'_id': ObjectId(order_id)})
            for item in order['items']:
                products_collection.update_one(
                    {'_id': ObjectId(item['product_id'])},
                    {'$inc': {'stock_quantity': -item['quantity']}}
                )

            return jsonify({'message': 'Payment confirmed and order processed'}), 200
        else:
            return jsonify({'message': 'Payment not successful'}), 400
    except Exception as e:
        return jsonify({'message': 'Payment confirmation error', 'error': str(e)}), 500
