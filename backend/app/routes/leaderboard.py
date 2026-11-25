from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models import User


class Leaderboard(Resource):
    @jwt_required()
    def get(self):
        try:
            league_name = request.args.get('league', 'diamond').lower()

            min_score = 0
            max_score = 999999999

            if league_name == 'bronze':
                min_score = 0
                max_score = 500
            elif league_name == 'silver':
                min_score = 501
                max_score = 1000
            elif league_name == 'gold':
                min_score = 1001
                max_score = 2000
            elif league_name == 'diamond':
                min_score = 2001
                max_score = 999999999

            users = (
                User.query
                .filter(User.score >= min_score, User.score <= max_score)
                .order_by(User.score.desc())
                .limit(20)
                .all()
            )

            leaderboard_data = []
            for user in users:
                leaderboard_data.append({
                    'username': user.username,
                    'score': user.score,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'avatar_id': user.avatar_id or 'fleming',
                    'league': User.get_league_info(user.score),
                })

            return leaderboard_data, 200
        except Exception as e:
            return {'message': str(e)}, 500
