from flask import Blueprint
from flask_restful import Api

from .auth import UserRegistration, UserLogin, UserProfile, UpdateAvatar
from .quiz import QuizList, QuizDetail, QuizSubmit
from .leaderboard import Leaderboard
from .badge_routes import AllBadges, EarnedBadges
from .bookmarks import BookmarkToggle, BookmarkList
from .flashcards import (
    FlashcardCategories,
    FlashcardDueList,
    FlashcardReview,
    FlashcardBookmarkToggle,
    FlashcardStats,
)
from .challenges import (
    DailyChallengeView,
    DailyChallengeAnswer,
    DuelCreate,
    DuelDetail,
    DuelSubmit,
)

auth_bp = Blueprint('auth_bp', __name__)
auth_api = Api(auth_bp)
auth_api.add_resource(UserRegistration, '/register')
auth_api.add_resource(UserLogin, '/login')
auth_api.add_resource(UserProfile, '/profile')
auth_api.add_resource(UpdateAvatar, '/update-avatar')

quiz_bp = Blueprint('quiz_bp', __name__)
quiz_api = Api(quiz_bp)
quiz_api.add_resource(QuizList, '/')
quiz_api.add_resource(QuizDetail, '/<string:quiz_id>')
quiz_api.add_resource(QuizSubmit, '/submit')

leaderboard_bp = Blueprint('leaderboard_bp', __name__)
leaderboard_api = Api(leaderboard_bp)
leaderboard_api.add_resource(Leaderboard, '/')

badge_bp = Blueprint('badge_bp', __name__)
badge_api = Api(badge_bp)
badge_api.add_resource(AllBadges, '/all')
badge_api.add_resource(EarnedBadges, '/earned')

bookmarks_bp = Blueprint('bookmarks_bp', __name__)
bookmarks_api = Api(bookmarks_bp)
bookmarks_api.add_resource(BookmarkToggle, '/')
bookmarks_api.add_resource(BookmarkList, '/list')

flashcards_bp = Blueprint('flashcards_bp', __name__)
flashcards_api = Api(flashcards_bp)
flashcards_api.add_resource(FlashcardCategories, '/categories')
flashcards_api.add_resource(FlashcardDueList, '/due')
flashcards_api.add_resource(FlashcardReview, '/review')
flashcards_api.add_resource(FlashcardBookmarkToggle, '/bookmark')
flashcards_api.add_resource(FlashcardStats, '/stats')

challenges_bp = Blueprint('challenges_bp', __name__)
challenges_api = Api(challenges_bp)
challenges_api.add_resource(DailyChallengeView, '/daily')
challenges_api.add_resource(DailyChallengeAnswer, '/daily/submit')
challenges_api.add_resource(DuelCreate, '/duel/create')
challenges_api.add_resource(DuelDetail, '/duel/<string:duel_id>')
challenges_api.add_resource(DuelSubmit, '/duel/<string:duel_id>/submit')
