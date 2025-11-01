import os
from app import create_app
from config.config import config

# Set default environment
environment = os.environ.get('FLASK_ENV', 'production')

# Create the Flask application
app = create_app(config[environment])

# Configure the app
app.config['SERVER_NAME'] = None  # Allow all host headers

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    debug = environment == 'development'
    app.run(host=host, port=port, debug=debug)
