import math
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, SurveyResponse

MIN_QUIZZES_FOR_SURVEY = 2
SURVEY_XP_REWARD = 50
TOTAL_MEEGA_ITEMS = 27


class SurveyStatus(Resource):
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        existing = SurveyResponse.query.filter_by(user_id=user.id).first()
        completed_count = len(user.get_completed_quiz_ids())

        return {
            'submitted': existing is not None,
            'submitted_at': existing.submitted_at.isoformat() if existing and existing.submitted_at else None,
            'quizzes_completed': completed_count,
            'min_quizzes_required': MIN_QUIZZES_FOR_SURVEY,
            'eligible': completed_count >= MIN_QUIZZES_FOR_SURVEY,
            'xp_reward': SURVEY_XP_REWARD,
        }, 200


class SurveySubmit(Resource):
    @jwt_required()
    def post(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        if SurveyResponse.query.filter_by(user_id=user.id).first():
            return {'message': 'شما قبلاً این پرسشنامه را تکمیل کرده‌اید.'}, 409

        data = request.get_json() or {}
        age = data.get('age')
        gender = (data.get('gender') or '').strip()
        digital_game_freq = (data.get('digital_game_freq') or '').strip()
        traditional_game_freq = (data.get('traditional_game_freq') or '').strip()
        answers = data.get('answers') or {}
        qualitative_feedback = (data.get('qualitative_feedback') or '').strip()

        try:
            age_int = int(age)
            if age_int < 15 or age_int > 90:
                return {'message': 'سن وارد شده معتبر نیست.'}, 400
        except (TypeError, ValueError):
            return {'message': 'لطفاً سن خود را به صورت عدد معتبر وارد کنید.'}, 400

        if gender not in ('زن', 'مرد'):
            return {'message': 'لطفاً جنسیت را انتخاب کنید.'}, 400

        if not digital_game_freq or not traditional_game_freq:
            return {'message': 'لطفاً سوالات سابقه بازی را تکمیل کنید.'}, 400

        if not isinstance(answers, dict):
            return {'message': 'فرمت پاسخ‌های پرسشنامه نامعتبر است.'}, 400

        cleaned_answers = {}
        for i in range(1, TOTAL_MEEGA_ITEMS + 1):
            key = f'q{i}'
            val = answers.get(key)
            try:
                val_int = int(val)
            except (TypeError, ValueError):
                return {'message': f'لطفاً به سوال شماره {i} پاسخ دهید.'}, 400
            if val_int < 1 or val_int > 5:
                return {'message': f'مقدار سوال شماره {i} باید بین ۱ تا ۵ باشد.'}, 400
            cleaned_answers[key] = val_int

        response = SurveyResponse(
            user_id=user.id,
            age=age_int,
            gender=gender,
            digital_game_freq=digital_game_freq,
            traditional_game_freq=traditional_game_freq,
            answers=cleaned_answers,
            qualitative_feedback=qualitative_feedback,
        )
        db.session.add(response)

        # Award XP incentive
        user.score = int(user.score or 0) + SURVEY_XP_REWARD
        user.level = math.floor(user.score / 200) + 1
        db.session.commit()

        return {
            'message': 'پرسشنامه با موفقیت ثبت شد. از مشارکت ارزشمند شما سپاسگزاریم!',
            'xp_awarded': SURVEY_XP_REWARD,
            'new_total_score': user.score,
            'new_level': user.level,
        }, 201
