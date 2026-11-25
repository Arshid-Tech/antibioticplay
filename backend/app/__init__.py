import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    cors_origins = os.environ.get(
        'FRONTEND_URL',
        'http://localhost:5173,http://localhost:3000'
    )
    CORS(app, resources={
        r"/api/*": {
            "origins": [o.strip() for o in cors_origins.split(',') if o.strip()],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    })

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'نشست شما منقضی شده است. لطفاً دوباره وارد شوید.',
            'error': 'token_expired',
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'توکن نامعتبر است.',
            'error': 'invalid_token',
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'برای دسترسی به این بخش باید وارد شوید.',
            'error': 'authorization_required',
        }), 401

    from . import models  # noqa: F401
    from .routes import (
        auth_bp,
        quiz_bp,
        leaderboard_bp,
        badge_bp,
        bookmarks_bp,
        flashcards_bp,
        challenges_bp,
        survey_bp,
        admin_bp,
    )

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(quiz_bp, url_prefix='/api/quizzes')
    app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')
    app.register_blueprint(badge_bp, url_prefix='/api/badges')
    app.register_blueprint(bookmarks_bp, url_prefix='/api/bookmarks')
    app.register_blueprint(flashcards_bp, url_prefix='/api/flashcards')
    app.register_blueprint(challenges_bp, url_prefix='/api/challenges')
    app.register_blueprint(survey_bp, url_prefix='/api/survey')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    @app.route('/health')
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            return jsonify({'status': 'ok', 'database': 'connected'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'database': str(e)}), 500

    return app
