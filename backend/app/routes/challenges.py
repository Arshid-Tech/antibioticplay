import math
import random
import uuid
from datetime import datetime, timezone
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import (
    User,
    Quiz,
    Question,
    DailyChallenge,
    DuelSession,
)
from .quiz import score_question


def _today_utc():
    return datetime.now(timezone.utc).date()


def _get_or_create_daily_challenge():
    today = _today_utc()
    challenge = DailyChallenge.query.filter_by(challenge_date=today).first()
    if challenge and challenge.question_ids:
        return challenge

    all_questions = Question.query.all()
    if not all_questions:
        return None

    rng = random.Random(today.isoformat())
    chosen = rng.sample(all_questions, k=min(5, len(all_questions)))
    q_ids = [q.id for q in chosen]

    if not challenge:
        challenge = DailyChallenge(challenge_date=today, question_ids=q_ids)
        db.session.add(challenge)
    else:
        challenge.question_ids = q_ids
    db.session.commit()
    return challenge


class DailyChallengeView(Resource):
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        challenge = _get_or_create_daily_challenge()
        if not challenge:
            return {'message': 'سوالی برای چالش روزانه یافت نشد'}, 404

        questions = Question.query.filter(Question.id.in_(challenge.question_ids)).all()
        q_map = {q.id: q.to_dict() for q in questions}
        ordered_questions = [q_map[qid] for qid in challenge.question_ids if qid in q_map]

        return {
            'date': challenge.challenge_date.isoformat(),
            'bonus_xp': 50,
            'questions': ordered_questions,
        }, 200


class DailyChallengeAnswer(Resource):
    """Grade a single question inside the Daily Challenge and award bonus XP on completion."""
    @jwt_required()
    def post(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        data = request.get_json() or {}
        question_id = data.get('questionId')
        user_answer = data.get('answer')
        is_last = bool(data.get('isLastQuestion', False))

        if not question_id or user_answer is None:
            return {'message': 'اطلاعات ناقص است'}, 400

        q_obj = Question.query.filter_by(id=question_id).first()
        if not q_obj:
            return {'message': 'سوال یافت نشد'}, 404

        q_dict = q_obj.to_dict()
        base_score, is_correct, feedback = score_question(q_dict, user_answer)

        xp_awarded = 10 if is_correct else 0
        if is_last:
            xp_awarded += 20  # Daily completion bonus

        user.score = int(user.score or 0) + xp_awarded
        user.level = math.floor(user.score / 200) + 1
        db.session.commit()

        return {
            'isCorrect': is_correct,
            'feedback': feedback,
            'scoreEarned': base_score,
            'xpAwarded': xp_awarded,
            'newTotalScore': user.score,
            'newLevel': user.level,
            'explanation': q_dict.get('explanation', ''),
        }, 200


class DuelCreate(Resource):
    @jwt_required()
    def post(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        data = request.get_json() or {}
        quiz_id = data.get('quizId')
        challenger_score = int(data.get('score', 0))

        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return {'message': 'آزمون یافت نشد'}, 404

        duel_id = str(uuid.uuid4())[:8]
        duel = DuelSession(
            id=duel_id,
            quiz_id=quiz.id,
            challenger_id=user.id,
            challenger_score=challenger_score,
            status='pending',
        )
        db.session.add(duel)
        db.session.commit()

        return {
            'duel_id': duel.id,
            'quiz_id': quiz.id,
            'quiz_title': quiz.title,
            'challenger_score': challenger_score,
            'share_path': f'/duel/{duel.id}',
        }, 201


class DuelDetail(Resource):
    @jwt_required()
    def get(self, duel_id):
        duel = DuelSession.query.filter_by(id=duel_id).first()
        if not duel:
            return {'message': 'دوئل یافت نشد'}, 404

        challenger = User.query.get(duel.challenger_id)
        opponent = User.query.get(duel.opponent_id) if duel.opponent_id else None
        quiz = Quiz.query.filter_by(id=duel.quiz_id).first()

        winner = None
        if duel.status == 'completed' and duel.opponent_score is not None:
            if duel.opponent_score > duel.challenger_score:
                winner = 'opponent'
            elif duel.challenger_score > duel.opponent_score:
                winner = 'challenger'
            else:
                winner = 'tie'

        return {
            'id': duel.id,
            'status': duel.status,
            'quiz_id': duel.quiz_id,
            'quiz_title': quiz.title if quiz else duel.quiz_id,
            'challenger': {
                'username': challenger.username if challenger else '',
                'full_name': f"{challenger.first_name or ''} {challenger.last_name or ''}".strip() or (challenger.username if challenger else ''),
                'avatar_id': challenger.avatar_id if challenger else 'fleming',
                'score': duel.challenger_score,
            },
            'opponent': {
                'username': opponent.username,
                'full_name': f"{opponent.first_name or ''} {opponent.last_name or ''}".strip() or opponent.username,
                'avatar_id': opponent.avatar_id or 'fleming',
                'score': duel.opponent_score,
            } if opponent else None,
            'winner': winner,
        }, 200


class DuelSubmit(Resource):
    @jwt_required()
    def post(self, duel_id):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        duel = DuelSession.query.filter_by(id=duel_id).first()
        if not duel:
            return {'message': 'دوئل یافت نشد'}, 404

        if duel.challenger_id == user.id:
            return {'message': 'نمی‌توانید با خودتان دوئل کنید! لینک را برای هم‌کلاسی خود ارسال کنید.'}, 400

        if duel.status == 'completed':
            return {'message': 'این دوئل قبلاً تکمیل شده است.'}, 409

        data = request.get_json() or {}
        opponent_score = int(data.get('score', 0))

        duel.opponent_id = user.id
        duel.opponent_score = opponent_score
        duel.status = 'completed'

        bonus_xp = 0
        winner = 'tie'
        if opponent_score > duel.challenger_score:
            winner = 'opponent'
            bonus_xp = 30
            user.score = int(user.score or 0) + bonus_xp
            user.level = math.floor(user.score / 200) + 1
        elif duel.challenger_score > opponent_score:
            winner = 'challenger'
            challenger = User.query.get(duel.challenger_id)
            if challenger:
                challenger.score = int(challenger.score or 0) + 30
                challenger.level = math.floor(challenger.score / 200) + 1
        else:
            bonus_xp = 15
            user.score = int(user.score or 0) + bonus_xp
            user.level = math.floor(user.score / 200) + 1

        db.session.commit()

        return {
            'message': 'نتیجه دوئل ثبت شد',
            'winner': winner,
            'bonus_xp': bonus_xp,
            'challenger_score': duel.challenger_score,
            'opponent_score': duel.opponent_score,
        }, 200
