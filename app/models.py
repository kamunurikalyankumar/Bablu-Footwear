from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB connection - MongoDB Atlas
client = MongoClient('mongodb+srv://admin:admin@mernapp.m9qyw.mongodb.net/?appName=MERNapp')
db = client['ecommerce_db']

# Collections
users_collection = db['users']
products_collection = db['products']
carts_collection = db['carts']
orders_collection = db['orders']

# User model
class User:
    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }

    @staticmethod
    def find_by_email(email):
        return users_collection.find_one({'email': email})

    @staticmethod
    def find_by_username(username):
        return users_collection.find_one({'username': username})

# Product model
class Product:
    def __init__(self, name, description, price, category, image_url, stock_quantity):
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.image_url = image_url
        self.stock_quantity = stock_quantity
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'stock_quantity': self.stock_quantity,
            'created_at': self.created_at
        }

    @staticmethod
    def find_all():
        return list(products_collection.find())

    @staticmethod
    def find_by_id(product_id):
        from bson import ObjectId
        return products_collection.find_one({'_id': ObjectId(product_id)})

    @staticmethod
    def find_by_category(category):
        return list(products_collection.find({'category': category}))

# Cart model
class Cart:
    def __init__(self, user_id, items=None):
        self.user_id = user_id
        self.items = items or []  # List of {'product_id': str, 'quantity': int}
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'items': self.items,
            'updated_at': self.updated_at
        }

    def add_item(self, product_id, quantity):
        product_id = str(product_id)  # Convert to string to ensure consistent comparison
        for item in self.items:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                return
        self.items.append({'product_id': product_id, 'quantity': quantity})

    def remove_item(self, product_id):
        product_id = str(product_id)  # Convert to string to ensure consistent comparison
        self.items = [item for item in self.items if item['product_id'] != product_id]

    @staticmethod
    def find_by_user_id(user_id):
        return carts_collection.find_one({'user_id': user_id})

# Order model
class Order:
    def __init__(self, user_id, items, total_amount, shipping_address, payment_status='pending'):
        self.user_id = user_id
        self.items = items  # List of {'product_id': str, 'quantity': int, 'price': float}
        self.total_amount = total_amount
        self.shipping_address = shipping_address
        self.payment_status = payment_status
        self.order_status = 'pending'
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'items': self.items,
            'total_amount': self.total_amount,
            'shipping_address': self.shipping_address,
            'payment_status': self.payment_status,
            'order_status': self.order_status,
            'created_at': self.created_at
        }

    @staticmethod
    def find_by_user_id(user_id):
        return list(orders_collection.find({'user_id': user_id}))

    @staticmethod
    def find_all():
        return list(orders_collection.find())
