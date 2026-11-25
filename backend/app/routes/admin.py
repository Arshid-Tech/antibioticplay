import csv
import io
import uuid
from functools import wraps
from datetime import datetime
from flask import request, Response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import (
    User,
    Unit,
    Quiz,
    Question,
    UserQuizProgress,
    Flashcard,
    UserFlashcardProgress,
    SurveyResponse,
    normalize_asset_path,
)

MEEGA_DOMAINS = {
    'visual_design': {
        'label': 'طراحی بصری و رابط کاربری',
        'items': ['q1', 'q2', 'q8', 'q9'],
    },
    'usability': {
        'label': 'قابلیت استفاده و سهولت یادگیری',
        'items': ['q3', 'q4', 'q5', 'q6', 'q7'],
    },
    'engagement': {
        'label': 'چالش، درگیری و غرقگی (Flow)',
        'items': ['q11', 'q12', 'q13', 'q14', 'q15', 'q18', 'q19', 'q20', 'q21', 'q22'],
    },
    'learning': {
        'label': 'ارزش آموزشی و یادگیری درک‌شده',
        'items': ['q10', 'q16', 'q17', 'q23', 'q24', 'q25', 'q26', 'q27'],
    },
}


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user or user.role != 'admin':
            return {'message': 'دسترسی غیرمجاز. این بخش مخصوص مدیران سیستم است.'}, 403
        return fn(*args, **kwargs)
    return wrapper


def _domain_mean(answers: dict, keys: list[str]) -> float | None:
    vals = [answers.get(k) for k in keys if isinstance(answers.get(k), (int, float))]
    if not vals:
        return None
    return round(sum(vals) / len(vals), 2)


class AdminAnalytics(Resource):
    @admin_required
    def get(self):
        users = User.query.all()
        total_users = len(users)
        quizzes = Quiz.query.order_by(Quiz.unit_id, Quiz.order_index).all()
        progresses = UserQuizProgress.query.all()
        surveys = SurveyResponse.query.all()
        total_flashcards = Flashcard.query.count()
        total_fc_reviews = UserFlashcardProgress.query.filter(
            UserFlashcardProgress.last_reviewed_at.isnot(None)
        ).count()

        # Users who started or completed at least one quiz
        active_user_ids = {p.user_id for p in progresses}
        completed_any_user_ids = {p.user_id for p in progresses if p.is_completed}

        # Per-quiz breakdown
        quiz_stats = []
        for quiz in quizzes:
            q_progs = [p for p in progresses if p.quiz_id == quiz.id]
            started_cnt = len(q_progs)
            completed_cnt = sum(1 for p in q_progs if p.is_completed)
            avg_score = (
                round(sum(p.best_score for p in q_progs) / started_cnt, 1)
                if started_cnt
                else 0
            )
            avg_attempts = (
                round(sum(p.attempts for p in q_progs) / started_cnt, 2)
                if started_cnt
                else 0
            )
            max_attempts = max((p.attempts for p in q_progs), default=0)
            quiz_stats.append({
                'id': quiz.id,
                'title': quiz.title,
                'questions_count': len(quiz.questions),
                'started_count': started_cnt,
                'completed_count': completed_cnt,
                'completion_rate': round((completed_cnt / started_cnt) * 100, 1) if started_cnt else 0,
                'avg_best_score': avg_score,
                'avg_attempts': avg_attempts,
                'max_attempts': max_attempts,
            })

        # MEEGA+ summary
        survey_count = len(surveys)
        domain_summary = []
        overall_scores = []
        ages = [s.age for s in surveys if s.age]
        gender_dist = {'زن': 0, 'مرد': 0}

        for s in surveys:
            if s.gender in gender_dist:
                gender_dist[s.gender] += 1
            ans = s.answers or {}
            vals = [v for v in ans.values() if isinstance(v, (int, float))]
            if vals:
                overall_scores.append(sum(vals))

        for dom_key, dom_info in MEEGA_DOMAINS.items():
            dom_vals = []
            for s in surveys:
                m = _domain_mean(s.answers or {}, dom_info['items'])
                if m is not None:
                    dom_vals.append(m)
            domain_summary.append({
                'key': dom_key,
                'label': dom_info['label'],
                'mean': round(sum(dom_vals) / len(dom_vals), 2) if dom_vals else 0,
            })

        qualitative_notes = [
            {
                'username': s.user.username if s.user else '',
                'submitted_at': s.submitted_at.isoformat() if s.submitted_at else '',
                'text': s.qualitative_feedback,
            }
            for s in surveys
            if s.qualitative_feedback
        ]

        return {
            'kpis': {
                'total_users': total_users,
                'active_users': len(active_user_ids),
                'completed_any_users': len(completed_any_user_ids),
                'survey_responses': survey_count,
                'total_flashcards': total_flashcards,
                'total_flashcard_reviews': total_fc_reviews,
                'meega_total_mean': round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else 0,
                'avg_age': round(sum(ages) / len(ages), 1) if ages else 0,
                'gender_distribution': gender_dist,
            },
            'quiz_stats': quiz_stats,
            'meega_domains': domain_summary,
            'qualitative_notes': qualitative_notes[:30],
        }, 200


class AdminExportCSV(Resource):
    @admin_required
    def get(self, export_type):
        export_type = (export_type or '').lower()
        if export_type not in ('users', 'survey', 'combined'):
            return {'message': 'نوع خروجی نامعتبر است'}, 400

        users = User.query.order_by(User.id.asc()).all()
        quizzes = Quiz.query.order_by(Quiz.unit_id, Quiz.order_index).all()
        quiz_ids = [q.id for q in quizzes]

        output = io.StringIO()
        # Add UTF-8 BOM for Persian support in Excel & SPSS
        output.write('\ufeff')

        if export_type == 'users':
            fieldnames = [
                'user_id', 'username', 'first_name', 'last_name', 'email', 'role',
                'total_score', 'level', 'quizzes_completed', 'correct_streak',
                'badges_count', 'flashcards_reviewed',
            ]
            for qid in quiz_ids:
                fieldnames.extend([f'{qid}_best_score', f'{qid}_attempts', f'{qid}_completed'])

            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for u in users:
                prog_map = {p.quiz_id: p for p in u.quiz_progresses.all()}
                fc_count = u.flashcard_progresses.filter(
                    UserFlashcardProgress.last_reviewed_at.isnot(None)
                ).count()
                row = {
                    'user_id': u.id,
                    'username': u.username,
                    'first_name': u.first_name or '',
                    'last_name': u.last_name or '',
                    'email': u.email,
                    'role': u.role,
                    'total_score': u.score,
                    'level': u.level,
                    'quizzes_completed': u.quizzes_completed,
                    'correct_streak': u.correct_streak,
                    'badges_count': u.earned_badges.count(),
                    'flashcards_reviewed': fc_count,
                }
                for qid in quiz_ids:
                    p = prog_map.get(qid)
                    row[f'{qid}_best_score'] = p.best_score if p else 0
                    row[f'{qid}_attempts'] = p.attempts if p else 0
                    row[f'{qid}_completed'] = 1 if (p and p.is_completed) else 0
                writer.writerow(row)

        elif export_type == 'survey':
            q_cols = [f'q{i}' for i in range(1, 28)]
            fieldnames = [
                'user_id', 'username', 'age', 'gender',
                'digital_game_freq', 'traditional_game_freq',
                *q_cols,
                'visual_design_mean', 'usability_mean', 'engagement_mean', 'learning_mean',
                'meega_total_score', 'qualitative_feedback', 'submitted_at',
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for s in SurveyResponse.query.order_by(SurveyResponse.submitted_at.asc()).all():
                ans = s.answers or {}
                row = {
                    'user_id': s.user_id,
                    'username': s.user.username if s.user else '',
                    'age': s.age,
                    'gender': s.gender,
                    'digital_game_freq': s.digital_game_freq,
                    'traditional_game_freq': s.traditional_game_freq,
                    'visual_design_mean': _domain_mean(ans, MEEGA_DOMAINS['visual_design']['items']) or '',
                    'usability_mean': _domain_mean(ans, MEEGA_DOMAINS['usability']['items']) or '',
                    'engagement_mean': _domain_mean(ans, MEEGA_DOMAINS['engagement']['items']) or '',
                    'learning_mean': _domain_mean(ans, MEEGA_DOMAINS['learning']['items']) or '',
                    'meega_total_score': sum(v for v in ans.values() if isinstance(v, (int, float))),
                    'qualitative_feedback': s.qualitative_feedback or '',
                    'submitted_at': s.submitted_at.isoformat() if s.submitted_at else '',
                }
                for col in q_cols:
                    row[col] = ans.get(col, '')
                writer.writerow(row)

        else:  # combined (SPSS-ready joined table)
            q_cols = [f'q{i}' for i in range(1, 28)]
            fieldnames = [
                'user_id', 'username', 'first_name', 'last_name',
                'total_score', 'level', 'quizzes_completed', 'badges_count',
                'total_attempts', 'flashcards_reviewed',
                'survey_submitted', 'age', 'gender',
                'digital_game_freq', 'traditional_game_freq',
                *q_cols,
                'visual_design_mean', 'usability_mean', 'engagement_mean', 'learning_mean',
                'meega_total_score', 'qualitative_feedback',
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for u in users:
                progs = u.quiz_progresses.all()
                s = u.survey_response
                ans = s.answers if s and s.answers else {}
                fc_count = u.flashcard_progresses.filter(
                    UserFlashcardProgress.last_reviewed_at.isnot(None)
                ).count()
                row = {
                    'user_id': u.id,
                    'username': u.username,
                    'first_name': u.first_name or '',
                    'last_name': u.last_name or '',
                    'total_score': u.score,
                    'level': u.level,
                    'quizzes_completed': u.quizzes_completed,
                    'badges_count': u.earned_badges.count(),
                    'total_attempts': sum(p.attempts for p in progs),
                    'flashcards_reviewed': fc_count,
                    'survey_submitted': 1 if s else 0,
                    'age': s.age if s else '',
                    'gender': s.gender if s else '',
                    'digital_game_freq': s.digital_game_freq if s else '',
                    'traditional_game_freq': s.traditional_game_freq if s else '',
                    'visual_design_mean': _domain_mean(ans, MEEGA_DOMAINS['visual_design']['items']) or '',
                    'usability_mean': _domain_mean(ans, MEEGA_DOMAINS['usability']['items']) or '',
                    'engagement_mean': _domain_mean(ans, MEEGA_DOMAINS['engagement']['items']) or '',
                    'learning_mean': _domain_mean(ans, MEEGA_DOMAINS['learning']['items']) or '',
                    'meega_total_score': sum(v for v in ans.values() if isinstance(v, (int, float))) if s else '',
                    'qualitative_feedback': s.qualitative_feedback if s else '',
                }
                for col in q_cols:
                    row[col] = ans.get(col, '') if s else ''
                writer.writerow(row)

        stamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f'antibioticplay_{export_type}_{stamp}.csv'
        return Response(
            output.getvalue(),
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )


class AdminQuizCollection(Resource):
    @admin_required
    def get(self):
        units = Unit.query.order_by(Unit.order_index.asc()).all()
        quizzes = Quiz.query.order_by(Quiz.unit_id, Quiz.order_index.asc()).all()
        return {
            'units': [
                {
                    'id': u.id,
                    'title': u.title,
                    'description': u.description,
                    'color': u.color,
                }
                for u in units
            ],
            'quizzes': [q.to_dict(include_questions=True) for q in quizzes],
        }, 200

    @admin_required
    def post(self):
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        unit_id = data.get('unit_id')
        if not title:
            return {'message': 'عنوان مرحله الزامی است'}, 400

        quiz_id = (data.get('id') or '').strip() or f"quiz_{str(uuid.uuid4())[:8]}"
        if Quiz.query.filter_by(id=quiz_id).first():
            return {'message': 'مرحله‌ای با این شناسه از قبل وجود دارد'}, 409

        existing_count = Quiz.query.filter_by(unit_id=unit_id).count()
        quiz = Quiz(
            id=quiz_id,
            unit_id=unit_id,
            title=title,
            icon=data.get('icon') or 'star',
            description=data.get('description') or '',
            micro_lesson=data.get('micro_lesson') or '',
            order_index=existing_count,
        )
        db.session.add(quiz)
        db.session.commit()
        return quiz.to_dict(include_questions=True), 201


class AdminQuizItem(Resource):
    @admin_required
    def put(self, quiz_id):
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return {'message': 'مرحله یافت نشد'}, 404

        data = request.get_json() or {}
        if 'title' in data:
            quiz.title = (data['title'] or '').strip()
        if 'description' in data:
            quiz.description = data['description'] or ''
        if 'icon' in data:
            quiz.icon = data['icon'] or 'star'
        if 'unit_id' in data:
            quiz.unit_id = data['unit_id']
        if 'micro_lesson' in data:
            quiz.micro_lesson = data['micro_lesson'] or ''

        db.session.commit()
        return quiz.to_dict(include_questions=True), 200

    @admin_required
    def delete(self, quiz_id):
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return {'message': 'مرحله یافت نشد'}, 404
        db.session.delete(quiz)
        db.session.commit()
        return {'message': 'مرحله با موفقیت حذف شد'}, 200


class AdminQuestionCollection(Resource):
    @admin_required
    def post(self):
        data = request.get_json() or {}
        quiz_id = data.get('quiz_id')
        q_type = data.get('type')
        payload = data.get('payload') or {}

        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return {'message': 'مرحله مورد نظر یافت نشد'}, 404
        if not q_type or not isinstance(payload, dict):
            return {'message': 'نوع سوال و ساختار payload الزامی است'}, 400

        q_id = (data.get('id') or '').strip() or f"q_{str(uuid.uuid4())[:8]}"
        if Question.query.filter_by(id=q_id).first():
            return {'message': 'سوالی با این شناسه وجود دارد'}, 409

        if 'hint' in payload:
            payload['hint'] = normalize_asset_path(payload['hint'])
        if 'image' in payload:
            payload['image'] = normalize_asset_path(payload['image'])

        payload['id'] = q_id
        payload['type'] = q_type
        title = data.get('title') or payload.get('title') or ''
        points = int(data.get('points_per_correct') or payload.get('points_per_correct') or 10)
        payload['title'] = title
        payload['points_per_correct'] = points

        q = Question(
            id=q_id,
            quiz_id=quiz.id,
            order_index=len(quiz.questions),
            type=q_type,
            title=title,
            points_per_correct=points,
            payload=payload,
        )
        db.session.add(q)
        db.session.commit()
        return q.to_dict(), 201


class AdminQuestionItem(Resource):
    @admin_required
    def put(self, question_id):
        q = Question.query.filter_by(id=question_id).first()
        if not q:
            return {'message': 'سوال یافت نشد'}, 404

        data = request.get_json() or {}
        payload = data.get('payload')
        if isinstance(payload, dict):
            if 'hint' in payload:
                payload['hint'] = normalize_asset_path(payload['hint'])
            if 'image' in payload:
                payload['image'] = normalize_asset_path(payload['image'])
            payload['id'] = q.id
            q.type = data.get('type') or payload.get('type') or q.type
            payload['type'] = q.type
            q.title = data.get('title') if 'title' in data else payload.get('title', q.title)
            payload['title'] = q.title
            q.points_per_correct = int(
                data.get('points_per_correct') or payload.get('points_per_correct') or q.points_per_correct
            )
            payload['points_per_correct'] = q.points_per_correct
            q.payload = payload

        db.session.commit()
        return q.to_dict(), 200

    @admin_required
    def delete(self, question_id):
        q = Question.query.filter_by(id=question_id).first()
        if not q:
            return {'message': 'سوال یافت نشد'}, 404
        db.session.delete(q)
        db.session.commit()
        return {'message': 'سوال با موفقیت حذف شد'}, 200


class AdminFlashcardCollection(Resource):
    @admin_required
    def get(self):
        cards = Flashcard.query.order_by(Flashcard.id.asc()).all()
        return [
            {
                'id': c.id,
                'category': c.category,
                'subcategory': c.subcategory or '',
                'front': c.front,
                'back': c.back,
                'clinical_pearl': c.clinical_pearl or '',
                'related_question_id': c.related_question_id or '',
            }
            for c in cards
        ], 200

    @admin_required
    def post(self):
        data = request.get_json() or {}
        category = (data.get('category') or '').strip()
        front = (data.get('front') or '').strip()
        back = (data.get('back') or '').strip()
        if not category or not front or not back:
            return {'message': 'دسته، روی کارت و پشت کارت الزامی هستند'}, 400

        card = Flashcard(
            category=category,
            subcategory=(data.get('subcategory') or '').strip(),
            front=front,
            back=back,
            clinical_pearl=(data.get('clinical_pearl') or '').strip(),
            related_question_id=(data.get('related_question_id') or '').strip() or None,
        )
        db.session.add(card)
        db.session.commit()
        return {
            'id': card.id,
            'category': card.category,
            'subcategory': card.subcategory,
            'front': card.front,
            'back': card.back,
            'clinical_pearl': card.clinical_pearl,
            'related_question_id': card.related_question_id or '',
        }, 201


class AdminFlashcardItem(Resource):
    @admin_required
    def put(self, fc_id):
        card = Flashcard.query.filter_by(id=fc_id).first()
        if not card:
            return {'message': 'فلش‌کارت یافت نشد'}, 404

        data = request.get_json() or {}
        if 'category' in data:
            card.category = (data['category'] or '').strip()
        if 'subcategory' in data:
            card.subcategory = (data['subcategory'] or '').strip()
        if 'front' in data:
            card.front = (data['front'] or '').strip()
        if 'back' in data:
            card.back = (data['back'] or '').strip()
        if 'clinical_pearl' in data:
            card.clinical_pearl = (data['clinical_pearl'] or '').strip()
        if 'related_question_id' in data:
            card.related_question_id = (data['related_question_id'] or '').strip() or None

        db.session.commit()
        return {
            'id': card.id,
            'category': card.category,
            'subcategory': card.subcategory,
            'front': card.front,
            'back': card.back,
            'clinical_pearl': card.clinical_pearl,
            'related_question_id': card.related_question_id or '',
        }, 200

    @admin_required
    def delete(self, fc_id):
        card = Flashcard.query.filter_by(id=fc_id).first()
        if not card:
            return {'message': 'فلش‌کارت یافت نشد'}, 404
        db.session.delete(card)
        db.session.commit()
        return {'message': 'فلش‌کارت حذف شد'}, 200


class AdminUsersList(Resource):
    @admin_required
    def get(self):
        users = User.query.order_by(User.score.desc()).all()
        return [
            {
                'id': u.id,
                'username': u.username,
                'first_name': u.first_name or '',
                'last_name': u.last_name or '',
                'email': u.email,
                'role': u.role,
                'score': u.score,
                'level': u.level,
                'quizzes_completed': u.quizzes_completed,
                'survey_submitted': u.survey_response is not None,
            }
            for u in users
        ], 200


class AdminUserRoleUpdate(Resource):
    @admin_required
    def put(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        data = request.get_json() or {}
        role = data.get('role')
        if role not in ('student', 'admin'):
            return {'message': 'نقش نامعتبر است'}, 400

        user.role = role
        db.session.commit()
        return {'id': user.id, 'username': user.username, 'role': user.role}, 200
