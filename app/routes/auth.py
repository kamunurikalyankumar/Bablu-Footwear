from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, users_collection
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Username, email, and password are required'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long'}), 400

    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return jsonify({'message': 'Invalid email format'}), 400

    if User.find_by_email(email):
        return jsonify({'message': 'Email already exists'}), 400

    if User.find_by_username(username):
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    user = User(username, email, hashed_password)
    users_collection.insert_one(user.to_dict())

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user_data = User.find_by_email(email)
    if not user_data or not check_password_hash(user_data['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user_data['_id']))
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': str(user_data['_id']),
            'username': user_data['username'],
            'email': user_data['email'],
            'is_admin': user_data.get('is_admin', False)
        }
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user_data = users_collection.find_one({'_id': current_user_id})
    if not user_data:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': str(user_data['_id']),
        'username': user_data['username'],
        'email': user_data['email'],
        'is_admin': user_data.get('is_admin', False)
    }), 200
