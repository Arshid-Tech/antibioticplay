from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
import os

mongo = PyMongo()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # CORS configuration
    # In production (Render), origins like https://antibioticplay-xyz.onrender.com will be set
    # For local development, CORS is allowed from port 5173 (Vite) and 3000 (port used by dev frontend)
    cors_origins = os.environ.get('FRONTEND_URL', 'http://localhost:5173,http://localhost:3000')
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins.split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    mongo.init_app(app)
    jwt.init_app(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'The token has expired.',
            'error': 'token_expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'Signature verification failed.',
            'error': 'invalid_token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'Request does not contain an access token.',
            'error': 'authorization_required'
        }), 401

    from .routes import auth_bp, quiz_bp, leaderboard_bp, badge_bp, bookmarks_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(quiz_bp, url_prefix='/api/quizzes')
    app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')
    app.register_blueprint(badge_bp, url_prefix='/api/badges')
    app.register_blueprint(bookmarks_bp, url_prefix='/api/bookmarks')

    # Health check endpoint for deployment monitoring
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok'})

    return app