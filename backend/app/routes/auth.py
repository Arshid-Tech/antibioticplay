from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app import db
from app.models import User


class UserRegistration(Resource):
    def post(self):
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password')
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()

        if not username or not email or not password:
            return {'message': 'فیلدهای الزامی خالی هستند'}, 400

        if User.find_by_username(username) or User.find_by_email(email):
            return {'message': 'کاربر با این نام کاربری یا ایمیل قبلاً ثبت‌نام کرده است'}, 409

        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            avatar_id='fleming',
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'کاربر با موفقیت ایجاد شد'}, 201


class UserLogin(Resource):
    def post(self):
        data = request.get_json() or {}
        identifier = (data.get('username') or '').strip()
        password = data.get('password') or ''

        user = User.find_by_username(identifier)
        if not user:
            user = User.find_by_email(identifier.lower())

        if user and user.verify_password(password):
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)
            display_name = user.first_name or user.username
            return {
                'message': f'ورود موفقیت آمیز بود. خوش آمدید {display_name}!',
                'access_token': access_token,
                'refresh_token': refresh_token,
            }, 200

        return {'message': 'نام کاربری/ایمیل یا رمز عبور نامعتبر است'}, 401


class UserProfile(Resource):
    @jwt_required()
    def get(self):
        current_user_username = get_jwt_identity()
        user = User.find_by_username(current_user_username)

        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        league_info = User.get_league_info(user.score)

        return {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'role': user.role,
            'score': user.score,
            'level': user.level,
            'correct_streak': user.correct_streak,
            'league': league_info,
            'avatar_id': user.avatar_id or 'fleming',
            'badges_earned': user.get_earned_badge_ids(),
            'quizzes_completed': user.quizzes_completed,
            'bookmarks': user.get_bookmarks_list(),
        }, 200


class UpdateAvatar(Resource):
    @jwt_required()
    def post(self):
        current_user_username = get_jwt_identity()
        data = request.get_json() or {}
        avatar_id = data.get('avatar_id')

        valid_avatars = ['fleming', 'waksman', 'domagk', 'florey', 'hodgkin', 'bugie', 'youyou']
        if avatar_id not in valid_avatars:
            return {'message': 'آواتار نامعتبر است'}, 400

        user = User.find_by_username(current_user_username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        user.avatar_id = avatar_id
        db.session.commit()

        return {'message': 'آواتار با موفقیت بروزرسانی شد'}, 200


class ChangePassword(Resource):
    @jwt_required()
    def post(self):
        current_user_username = get_jwt_identity()
        data = request.get_json() or {}
        current_password = data.get('current_password') or ''
        new_password = data.get('new_password') or ''

        if not current_password or not new_password:
            return {'message': 'وارد کردن رمز عبور فعلی و رمز عبور جدید الزامی است.'}, 400

        if len(new_password) < 6:
            return {'message': 'رمز عبور جدید باید حداقل ۶ کاراکتر باشد.'}, 400

        user = User.find_by_username(current_user_username)
        if not user:
            return {'message': 'کاربر یافت نشد.'}, 404

        if not user.verify_password(current_password):
            return {'message': 'رمز عبور فعلی اشتباه است.'}, 400

        user.set_password(new_password)
        db.session.commit()

        return {'message': 'رمز عبور شما با موفقیت تغییر یافت.'}, 200
