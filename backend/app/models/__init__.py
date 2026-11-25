from datetime import datetime, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


def _utcnow():
    return datetime.now(timezone.utc)


def normalize_asset_path(value):
    """Fix legacy typo '/image/questions/...' -> '/images/questions/...'."""
    if isinstance(value, str) and value.startswith('/image/'):
        return value.replace('/image/', '/images/', 1)
    return value


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(80), nullable=True, default='')
    last_name = db.Column(db.String(80), nullable=True, default='')
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' | 'admin'

    score = db.Column(db.Integer, nullable=False, default=0, index=True)
    level = db.Column(db.Integer, nullable=False, default=1)
    quizzes_completed = db.Column(db.Integer, nullable=False, default=0)
    correct_streak = db.Column(db.Integer, nullable=False, default=0)
    avatar_id = db.Column(db.String(40), nullable=False, default='fleming')
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)

    quiz_progresses = db.relationship(
        'UserQuizProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )
    earned_badges = db.relationship(
        'UserBadge', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )
    bookmarks = db.relationship(
        'Bookmark', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )
    flashcard_progresses = db.relationship(
        'UserFlashcardProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )
    survey_response = db.relationship(
        'SurveyResponse', backref='user', uselist=False, cascade='all, delete-orphan'
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def check_password(user_hash: str, password: str) -> bool:
        return check_password_hash(user_hash, password)

    @staticmethod
    def find_by_username(username: str):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def find_by_email(email: str):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_league_info(score):
        score = int(score or 0)
        if score <= 500:
            return {'name': 'برنز', 'icon': 'fas fa-medal', 'color': '#cd7f32'}
        elif score <= 1000:
            return {'name': 'نقره', 'icon': 'fas fa-medal', 'color': '#c0c0c0'}
        elif score <= 2000:
            return {'name': 'طلا', 'icon': 'fas fa-trophy', 'color': '#ffd700'}
        else:
            return {'name': 'الماس', 'icon': 'fas fa-gem', 'color': '#b9f2ff'}

    def get_earned_badge_ids(self):
        return [ub.badge_id for ub in self.earned_badges.all()]

    def get_completed_quiz_ids(self):
        return [
            p.quiz_id
            for p in self.quiz_progresses.filter_by(is_completed=True).all()
        ]

    def get_bookmarks_list(self):
        return [
            {'quiz_id': b.quiz_id, 'question_id': b.question_id}
            for b in self.bookmarks.all()
        ]


class Unit(db.Model):
    __tablename__ = 'units'

    id = db.Column(db.String(80), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True, default='')
    color = db.Column(db.String(30), nullable=True, default='#4caf50')
    order_index = db.Column(db.Integer, nullable=False, default=0)

    quizzes = db.relationship(
        'Quiz',
        backref='unit',
        lazy='select',
        order_by='Quiz.order_index',
        cascade='all, delete-orphan',
    )


class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.String(80), primary_key=True)
    unit_id = db.Column(db.String(80), db.ForeignKey('units.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(80), nullable=True, default='star')
    description = db.Column(db.Text, nullable=True, default='')
    micro_lesson = db.Column(db.Text, nullable=True, default='')
    order_index = db.Column(db.Integer, nullable=False, default=0)

    questions = db.relationship(
        'Question',
        backref='quiz',
        lazy='select',
        order_by='Question.order_index',
        cascade='all, delete-orphan',
    )

    def to_dict(self, include_questions=True):
        data = {
            'id': self.id,
            'unit_id': self.unit_id,
            'title': self.title,
            'icon': self.icon,
            'description': self.description,
            'micro_lesson': self.micro_lesson or '',
        }
        if include_questions:
            data['questions'] = [q.to_dict() for q in self.questions]
        return data


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.String(100), primary_key=True)
    quiz_id = db.Column(db.String(80), db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False, index=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(300), nullable=True, default='')
    points_per_correct = db.Column(db.Integer, nullable=False, default=10)
    # Stores all flexible fields (instruction, text, hint, image, options, zones, categories, items, statements, solution, explanation, etc.)
    payload = db.Column(db.JSON, nullable=False, default=dict)

    def to_dict(self):
        result = dict(self.payload or {})
        result['id'] = self.id
        result['type'] = self.type
        if self.title and 'title' not in result:
            result['title'] = self.title
        if 'points_per_correct' not in result:
            result['points_per_correct'] = self.points_per_correct
        if 'hint' in result:
            result['hint'] = normalize_asset_path(result['hint'])
        if 'image' in result:
            result['image'] = normalize_asset_path(result['image'])
        return result


class Badge(db.Model):
    __tablename__ = 'badges'

    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True, default='')
    icon = db.Column(db.String(80), nullable=True, default='fas fa-medal')
    criteria = db.Column(db.JSON, nullable=False, default=dict)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'criteria': self.criteria or {},
        }


class UserBadge(db.Model):
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    badge_id = db.Column(db.String(80), db.ForeignKey('badges.id', ondelete='CASCADE'), nullable=False)
    earned_at = db.Column(db.DateTime(timezone=True), default=_utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),
    )


class UserQuizProgress(db.Model):
    __tablename__ = 'user_quiz_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    quiz_id = db.Column(db.String(80), db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False, index=True)
    best_score = db.Column(db.Integer, nullable=False, default=0)
    current_session_score = db.Column(db.Integer, nullable=False, default=0)
    current_session_correct_count = db.Column(db.Integer, nullable=False, default=0)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'quiz_id', name='uq_user_quiz_progress'),
    )


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    quiz_id = db.Column(db.String(80), db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.String(100), db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'quiz_id', 'question_id', name='uq_user_bookmark'),
    )


# --- Future-ready tables for Phases 3, 4, 5, 6 ---

class Flashcard(db.Model):
    __tablename__ = 'flashcards'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(120), nullable=False, index=True)
    subcategory = db.Column(db.String(120), nullable=True, default='')
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    clinical_pearl = db.Column(db.Text, nullable=True, default='')
    related_question_id = db.Column(db.String(100), nullable=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)


class UserFlashcardProgress(db.Model):
    __tablename__ = 'user_flashcard_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcards.id', ondelete='CASCADE'), nullable=False)
    box = db.Column(db.Integer, nullable=False, default=1)  # Leitner box 1..5
    ease_factor = db.Column(db.Float, nullable=False, default=2.5)
    interval_days = db.Column(db.Integer, nullable=False, default=1)
    repetitions = db.Column(db.Integer, nullable=False, default=0)
    is_bookmarked = db.Column(db.Boolean, nullable=False, default=False)
    next_review_at = db.Column(db.DateTime(timezone=True), default=_utcnow, index=True)
    last_reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'flashcard_id', name='uq_user_flashcard'),
    )


class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    digital_game_freq = db.Column(db.String(50), nullable=True)
    traditional_game_freq = db.Column(db.String(50), nullable=True)
    answers = db.Column(db.JSON, nullable=False, default=dict)  # MEEGA+ 27 items
    qualitative_feedback = db.Column(db.Text, nullable=True, default='')
    submitted_at = db.Column(db.DateTime(timezone=True), default=_utcnow)


class DailyChallenge(db.Model):
    __tablename__ = 'daily_challenges'

    id = db.Column(db.Integer, primary_key=True)
    challenge_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    question_ids = db.Column(db.JSON, nullable=False, default=list)
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)


class DuelSession(db.Model):
    __tablename__ = 'duel_sessions'

    id = db.Column(db.String(36), primary_key=True)
    quiz_id = db.Column(db.String(80), db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    challenger_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    opponent_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    challenger_score = db.Column(db.Integer, nullable=False, default=0)
    opponent_score = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending | completed
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)
