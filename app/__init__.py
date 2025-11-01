from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .routes.auth import auth_bp
from .routes.products import products_bp
from .routes.cart import cart_bp
from .routes.orders import orders_bp
from .routes.admin import admin_bp
import os

def create_app(config_object=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Load configuration
    if config_object is None:
        # Load the default configuration
        app.config.from_object('config.config.Config')
    else:
        app.config.from_object(config_object)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    CORS(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Serve static files
    @app.route('/assets/<path:path>')
    def serve_assets(path):
        return send_from_directory('static/assets', path)

    # Serve HTML pages
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/<path:path>')
    def serve_page(path):
        if path.endswith('.html'):
            return render_template(path)
        return render_template('index.html')

    return app
