from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Badge


class AllBadges(Resource):
    @jwt_required()
    def get(self):
        try:
            all_badges = [b.to_dict() for b in Badge.query.all()]
            return all_badges, 200
        except Exception as e:
            return {'message': str(e)}, 500


class EarnedBadges(Resource):
    @jwt_required()
    def get(self):
        current_user_username = get_jwt_identity()
        user = User.find_by_username(current_user_username)
        if not user:
            return {'message': 'User not found'}, 404

        earned_badge_ids = user.get_earned_badge_ids()
        if not earned_badge_ids:
            return [], 200

        badges = Badge.query.filter(Badge.id.in_(earned_badge_ids)).all()
        return [b.to_dict() for b in badges], 200
