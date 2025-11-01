from app import create_app
from config.config import config
import os

environment = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[environment])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'  # Required for Render deployment
    debug = environment == 'development'
    app.run(host=host, port=port, debug=debug)
