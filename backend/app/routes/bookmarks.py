from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Quiz, Question, Bookmark


class BookmarkToggle(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        data = request.get_json() or {}
        quiz_id = data.get('quizId')
        question_id = data.get('questionId')

        if not quiz_id or not question_id:
            return {'message': 'Invalid data'}, 400

        user = User.find_by_username(current_user)
        if not user:
            return {'message': 'User not found'}, 404

        existing = Bookmark.query.filter_by(
            user_id=user.id, quiz_id=quiz_id, question_id=question_id
        ).first()

        if existing:
            db.session.delete(existing)
            action = 'removed'
        else:
            db.session.add(Bookmark(user_id=user.id, quiz_id=quiz_id, question_id=question_id))
            action = 'added'

        db.session.commit()

        return {
            'message': 'Success',
            'action': action,
            'bookmarks': user.get_bookmarks_list(),
        }, 200


class BookmarkList(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.find_by_username(current_user)
        if not user:
            return {'message': 'User not found'}, 404

        bookmarked_questions = []
        for bm in user.bookmarks.all():
            quiz = Quiz.query.filter_by(id=bm.quiz_id).first()
            question = Question.query.filter_by(id=bm.question_id).first()
            if quiz and question:
                q_dict = question.to_dict()
                q_dict['quiz_title'] = quiz.title
                q_dict['quiz_id'] = quiz.id
                bookmarked_questions.append(q_dict)

        return bookmarked_questions, 200
