from datetime import datetime, timedelta, timezone
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Flashcard, UserFlashcardProgress


def _utcnow():
    return datetime.now(timezone.utc)


def _serialize_card(card: Flashcard, progress: UserFlashcardProgress | None):
    now = _utcnow()
    next_review = progress.next_review_at if progress else None
    is_due = True
    if next_review is not None:
        if next_review.tzinfo is None:
            next_review = next_review.replace(tzinfo=timezone.utc)
        is_due = next_review <= now

    return {
        'id': card.id,
        'category': card.category,
        'subcategory': card.subcategory or '',
        'front': card.front,
        'back': card.back,
        'clinical_pearl': card.clinical_pearl or '',
        'related_question_id': card.related_question_id,
        'box': progress.box if progress else 0,
        'interval_days': progress.interval_days if progress else 0,
        'repetitions': progress.repetitions if progress else 0,
        'is_bookmarked': progress.is_bookmarked if progress else False,
        'is_due': is_due,
        'next_review_at': next_review.isoformat() if next_review else None,
    }


class FlashcardCategories(Resource):
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        cards = Flashcard.query.order_by(Flashcard.id.asc()).all()
        progress_map = {
            p.flashcard_id: p
            for p in UserFlashcardProgress.query.filter_by(user_id=user.id).all()
        }

        now = _utcnow()
        categories = {}
        for card in cards:
            cat = card.category
            if cat not in categories:
                categories[cat] = {
                    'name': cat,
                    'total': 0,
                    'due': 0,
                    'mastered': 0,
                    'bookmarked': 0,
                }
            entry = categories[cat]
            entry['total'] += 1

            prog = progress_map.get(card.id)
            if not prog:
                entry['due'] += 1
            else:
                nr = prog.next_review_at
                if nr and nr.tzinfo is None:
                    nr = nr.replace(tzinfo=timezone.utc)
                if not nr or nr <= now:
                    entry['due'] += 1
                if prog.box >= 4:
                    entry['mastered'] += 1
                if prog.is_bookmarked:
                    entry['bookmarked'] += 1

        return list(categories.values()), 200


class FlashcardDueList(Resource):
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        category = request.args.get('category')
        mode = request.args.get('mode', 'due').lower()  # due | all | bookmarked
        limit = request.args.get('limit', type=int) or 50

        query = Flashcard.query
        if category and category != 'all':
            query = query.filter_by(category=category)

        cards = query.order_by(Flashcard.id.asc()).all()
        progress_map = {
            p.flashcard_id: p
            for p in UserFlashcardProgress.query.filter_by(user_id=user.id).all()
        }

        now = _utcnow()
        result = []
        for card in cards:
            prog = progress_map.get(card.id)
            serialized = _serialize_card(card, prog)

            if mode == 'due' and not serialized['is_due']:
                continue
            if mode == 'bookmarked' and not serialized['is_bookmarked']:
                continue
            result.append(serialized)

        # Prioritize urgent/box-1 cards first (including auto-queued wrong quiz cards)
        result.sort(key=lambda c: (0 if c['box'] == 1 else (1 if c['box'] == 0 else 2), c['box'], c['id']))
        return result[:limit], 200


class FlashcardReview(Resource):
    """
    Hybrid SM-2 + Leitner spaced repetition update.
    rating: 'hard' | 'medium' | 'easy'
    """
    @jwt_required()
    def post(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        data = request.get_json() or {}
        flashcard_id = data.get('flashcard_id')
        rating = (data.get('rating') or '').lower()

        if not flashcard_id or rating not in ('hard', 'medium', 'easy'):
            return {'message': 'اطلاعات ارسالی نامعتبر است'}, 400

        card = Flashcard.query.filter_by(id=flashcard_id).first()
        if not card:
            return {'message': 'فلش‌کارت یافت نشد'}, 404

        prog = UserFlashcardProgress.query.filter_by(
            user_id=user.id, flashcard_id=card.id
        ).first()
        if not prog:
            prog = UserFlashcardProgress(
                user_id=user.id,
                flashcard_id=card.id,
                box=1,
                ease_factor=2.5,
                interval_days=1,
                repetitions=0,
            )
            db.session.add(prog)

        now = _utcnow()

        if rating == 'hard':
            prog.box = 1
            prog.repetitions = 0
            prog.interval_days = 1
            prog.ease_factor = max(1.3, prog.ease_factor - 0.2)
            xp_reward = 1
        elif rating == 'medium':
            prog.box = min(5, max(1, prog.box) + 1)
            prog.repetitions += 1
            if prog.repetitions == 1:
                prog.interval_days = 2
            elif prog.repetitions == 2:
                prog.interval_days = 6
            else:
                prog.interval_days = max(1, round(prog.interval_days * prog.ease_factor))
            xp_reward = 2
        else:  # easy
            prog.box = min(5, max(1, prog.box) + 2)
            prog.repetitions += 1
            prog.ease_factor = min(3.0, prog.ease_factor + 0.15)
            if prog.repetitions == 1:
                prog.interval_days = 4
            else:
                prog.interval_days = max(4, round(prog.interval_days * prog.ease_factor * 1.2))
            xp_reward = 3

        prog.last_reviewed_at = now
        prog.next_review_at = now + timedelta(days=prog.interval_days)

        # Small XP incentive for active flashcard study
        user.score = int(user.score or 0) + xp_reward
        db.session.commit()

        return {
            'message': 'مرور ثبت شد',
            'xp_earned': xp_reward,
            'new_total_score': user.score,
            'card': _serialize_card(card, prog),
        }, 200


class FlashcardBookmarkToggle(Resource):
    @jwt_required()
    def post(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        data = request.get_json() or {}
        flashcard_id = data.get('flashcard_id')
        if not flashcard_id:
            return {'message': 'شناسه فلش‌کارت الزامی است'}, 400

        card = Flashcard.query.filter_by(id=flashcard_id).first()
        if not card:
            return {'message': 'فلش‌کارت یافت نشد'}, 404

        prog = UserFlashcardProgress.query.filter_by(
            user_id=user.id, flashcard_id=card.id
        ).first()
        if not prog:
            prog = UserFlashcardProgress(
                user_id=user.id,
                flashcard_id=card.id,
                box=0,
                ease_factor=2.5,
                interval_days=0,
                repetitions=0,
                is_bookmarked=True,
                next_review_at=_utcnow(),
            )
            db.session.add(prog)
        else:
            prog.is_bookmarked = not prog.is_bookmarked

        db.session.commit()
        return {
            'flashcard_id': card.id,
            'is_bookmarked': prog.is_bookmarked,
        }, 200


class FlashcardStats(Resource):
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        user = User.find_by_username(username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        total = Flashcard.query.count()
        progresses = UserFlashcardProgress.query.filter_by(user_id=user.id).all()
        now = _utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        reviewed_today = 0
        mastered = 0
        bookmarked = 0
        not_due = 0
        boxes = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for p in progresses:
            if p.last_reviewed_at:
                lr = p.last_reviewed_at
                if lr.tzinfo is None:
                    lr = lr.replace(tzinfo=timezone.utc)
                if lr >= today_start:
                    reviewed_today += 1
            if p.box in boxes:
                boxes[p.box] += 1
            if p.box >= 4:
                mastered += 1
            if p.is_bookmarked:
                bookmarked += 1
            nr = p.next_review_at
            if nr:
                if nr.tzinfo is None:
                    nr = nr.replace(tzinfo=timezone.utc)
                if nr > now:
                    not_due += 1

        return {
            'total_cards': total,
            'due_today': max(0, total - not_due),
            'reviewed_today': reviewed_today,
            'mastered': mastered,
            'bookmarked': bookmarked,
            'boxes': boxes,
        }, 200
