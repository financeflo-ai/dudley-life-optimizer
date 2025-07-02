import os
import sys
from datetime import datetime, timedelta
import jwt
from functools import wraps
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from src.routes.user import user_bp
from src.routes.journal import journal_bp
from src.routes.business import business_bp
from src.routes.health import health_bp
from src.routes.productivity import productivity_bp
from src.routes.financial import financial_bp
from src.routes.goals import goals_bp
from src.routes.ai_insights import ai_insights_bp
from src.routes.analytics import analytics_bp
from src.routes.voice import voice_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dudley-life-optimizer-secret-key-2025')

# Enable CORS for all routes
CORS(app, origins="*")

# Register all blueprints
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(journal_bp, url_prefix='/api/journal')
app.register_blueprint(business_bp, url_prefix='/api/business')
app.register_blueprint(health_bp, url_prefix='/api/health')
app.register_blueprint(productivity_bp, url_prefix='/api/productivity')
app.register_blueprint(financial_bp, url_prefix='/api/financial')
app.register_blueprint(goals_bp, url_prefix='/api/goals')
app.register_blueprint(ai_insights_bp, url_prefix='/api/ai')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(voice_bp, url_prefix='/api/voice')

# JWT token verification decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Dudley Life Optimizer API',
        'version': '1.0.0'
    })

# Authentication endpoint
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # For demo purposes, using hardcoded credentials
    # In production, this would verify against Supabase Auth
    if data.get('email') == 'dudley@cmosuccesssystems.com' and data.get('password') == 'DudleyLifeOptimizer2025!':
        token = jwt.encode({
            'user_id': 'dudley-peacock-uuid',
            'email': 'dudley@cmosuccesssystems.com',
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': 'dudley-peacock-uuid',
                'email': 'dudley@cmosuccesssystems.com',
                'name': 'Dudley Peacock',
                'wealth_target_gbp': 200000000,
                'current_age': 56
            }
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

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
    app.run(host='0.0.0.0', port=5000, debug=True)
