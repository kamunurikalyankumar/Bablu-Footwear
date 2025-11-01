from flask import Flask, render_template, send_from_directory, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .routes.auth import auth_bp
from .routes.products import products_bp
from .routes.cart import cart_bp
from .routes.orders import orders_bp
from .routes.admin import admin_bp
import os

# Create the Flask application
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static',
           static_url_path='/static')

def create_app(config_object=None):
    global app
    
    # Load configuration
    if config_object is None:
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
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    # Main routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/shop')
    def shop():
        return render_template('shop.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/register')
    def register():
        return render_template('register.html')

    @app.route('/cart')
    def cart():
        return render_template('cart.html')

    @app.route('/admin')
    def admin():
        return render_template('admin.html')

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.error(f'Page not found: {request.url}')
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f'Server Error: {e}')
        return render_template('500.html'), 500

    # Serve static files
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)

    return app
