import os
import sys
# DON\"T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.product import product_bp
from prometheus_flask_exporter import PrometheusMetrics
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

metrics = PrometheusMetrics(app)

# Enable CORS for all routes
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Basic Auth setup
auth = HTTPBasicAuth()

users = {
    "user1": {"password": generate_password_hash("pass1"), "role": "user"},
    "admin1": {"password": generate_password_hash("adminpass"), "role": "admin"}
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username]["password"], password):
        return username

@auth.get_user_roles
def get_user_roles(username):
    return users[username]["role"]

# Function to skip rate limiting for health checks
def skip_health_check():
    return request.path == '/healthz'

# Rate Limiting setup
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://", # Can use redis:// for production
    skip_if=skip_health_check # Skip rate limiting if health check
)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(product_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Import models to ensure they are registered
from src.models.product import Product

with app.app_context():
    db.create_all()

@app.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        'message': 'Microservices Backend API',
        'version': '1.0.0',
        'endpoints': {
            'users': '/api/users',
            'products': '/api/products',
            'health': '/api/health'
        }
    })

@app.after_request
def log_request_info(response):
    logger.info(f'Request: Path={request.path}, Method={request.method}, ResponseCode={response.status_code}')
    return response

# Secure endpoint example
@app.route('/api/secure-data', methods=['GET'])
@auth.login_required
def secure_data():
    return jsonify({'message': 'This is secure data!'})

# Authorization examples
@app.route('/api/admin-only', methods=['POST', 'DELETE'])
@auth.login_required(role='admin')
def admin_only_post_delete():
    return jsonify({'message': 'Admin can perform POST/DELETE here.'}), 200

@app.route('/api/user-get', methods=['GET'])
@auth.login_required(role='user')
def user_get():
    return jsonify({'message': 'User can perform GET here.'}), 200

@app.route('/api/user-post-delete', methods=['POST', 'DELETE'])
@auth.login_required(role='user')
def user_post_delete():
    # If user role tries to POST/DELETE, return 403
    return jsonify({'message': 'Forbidden for user role on POST/DELETE.'}), 403

# Rate limited endpoint example
@app.route('/api/products', methods=['GET'])
@limiter.limit("10 per minute") # Limit 10 requests per minute
def get_products():
    return jsonify([{'id': 1, 'name': 'Product A'}]), 200

# Handle rate limit exceeded error
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'message': 'Too many requests.', 'status_code': 409}), 409

@app.route('/healthz', methods=['GET'])
def healthz():
    return 'OK', 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


