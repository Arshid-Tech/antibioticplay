import sys
from copy import deepcopy
from app import create_app, db
from app.models import Unit, Quiz, Question, Badge, normalize_asset_path
from app.quiz_data import QUIZZES, LEARNING_PATH
from app.badge_data import BADGES


def _clean_question_payload(q_dict: dict) -> dict:
    cleaned = deepcopy(q_dict)
    if 'hint' in cleaned:
        cleaned['hint'] = normalize_asset_path(cleaned['hint'])
    if 'image' in cleaned:
        cleaned['image'] = normalize_asset_path(cleaned['image'])
    return cleaned


def seed_database(if_empty: bool = False):
    app = create_app()
    with app.app_context():
        db.create_all()

        if if_empty and Quiz.query.first() is not None:
            print('ℹ️ Database already seeded. Skipping seed (--if-empty).')
            return

        print('--- Starting PostgreSQL Database Seed ---')

        # 1. Upsert Units and Quizzes from LEARNING_PATH & QUIZZES
        quiz_to_unit = {}
        for u_idx, unit_data in enumerate(LEARNING_PATH):
            unit = Unit.query.filter_by(id=unit_data['id']).first()
            if not unit:
                unit = Unit(id=unit_data['id'])
                db.session.add(unit)
            unit.title = unit_data['title']
            unit.description = unit_data.get('description', '')
            unit.color = unit_data.get('color', '#4caf50')
            unit.order_index = u_idx

            for q_idx, quiz_id in enumerate(unit_data.get('levels', [])):
                quiz_to_unit[quiz_id] = (unit_data['id'], q_idx)

        db.session.flush()

        quiz_count = 0
        question_count = 0

        for quiz_id, quiz_data in QUIZZES.items():
            unit_id, order_idx = quiz_to_unit.get(quiz_id, (None, quiz_count))
            quiz = Quiz.query.filter_by(id=quiz_id).first()
            if not quiz:
                quiz = Quiz(id=quiz_id)
                db.session.add(quiz)

            quiz.unit_id = unit_id
            quiz.title = quiz_data['title']
            quiz.icon = quiz_data.get('icon', 'star')
            quiz.description = quiz_data.get('description', '')
            quiz.order_index = order_idx
            quiz_count += 1

            db.session.flush()

            for idx, q_dict in enumerate(quiz_data.get('questions', [])):
                q_id = q_dict['id']
                cleaned_payload = _clean_question_payload(q_dict)

                question = Question.query.filter_by(id=q_id).first()
                if not question:
                    question = Question(id=q_id, quiz_id=quiz_id)
                    db.session.add(question)

                question.quiz_id = quiz_id
                question.order_index = idx
                question.type = cleaned_payload.get('type', 'multiple-select')
                question.title = cleaned_payload.get('title', '')
                question.points_per_correct = cleaned_payload.get('points_per_correct', 10)
                question.payload = cleaned_payload
                question_count += 1

        # 2. Upsert Badges
        badge_count = 0
        for badge_id, badge_data in BADGES.items():
            badge = Badge.query.filter_by(id=badge_id).first()
            if not badge:
                badge = Badge(id=badge_id)
                db.session.add(badge)
            badge.name = badge_data['name']
            badge.description = badge_data.get('description', '')
            badge.icon = badge_data.get('icon', 'fas fa-medal')
            badge.criteria = badge_data.get('criteria', {})
            badge_count += 1

        db.session.commit()
        print(f'🚀 Seeded {len(LEARNING_PATH)} units, {quiz_count} quizzes, {question_count} questions, and {badge_count} badges.')
        print('--- Database Seed Complete ---')


if __name__ == '__main__':
    if_empty_flag = '--if-empty' in sys.argv
    seed_database(if_empty=if_empty_flag)
