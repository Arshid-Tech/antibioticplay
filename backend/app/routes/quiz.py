from datetime import datetime, timezone
import math
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import (
    User,
    Unit,
    Quiz,
    Question,
    Badge,
    UserBadge,
    UserQuizProgress,
    Flashcard,
    UserFlashcardProgress,
)


# Smart speed-bonus thresholds (in seconds) tailored to each question type
# Tuple: (tier_5_sec, tier_4_sec, tier_3_sec, tier_2_sec)
SPEED_THRESHOLDS_BY_TYPE = {
    'true-false': (10, 18, 28, 40),
    'multiple-select': (15, 25, 35, 50),
    'drag-drop-fill': (20, 32, 45, 60),
    'drag-drop-match': (25, 40, 55, 75),
    'drag-drop-ordering': (25, 40, 55, 75),
    'image-labeling': (45, 65, 90, 120),
    'clinical-case': (45, 65, 90, 120),
}


def calculate_speed_bonus(question_type: str, time_taken: float) -> tuple[int, int]:
    """Return (speed_bonus_xp, top_tier_target_seconds) based on question complexity."""
    t5, t4, t3, t2 = SPEED_THRESHOLDS_BY_TYPE.get(question_type, (15, 25, 35, 50))
    if time_taken <= t5:
        return 5, t5
    if time_taken <= t4:
        return 4, t5
    if time_taken <= t3:
        return 3, t5
    if time_taken <= t2:
        return 2, t5
    return 0, t5


def score_question(question: dict, user_answer):
    """Shared scoring engine used by QuizSubmit and DailyChallenge."""
    question_type = question.get('type')
    solution = question.get('solution')
    points_total = question.get('points_per_correct', 10)

    score_earned = 0
    is_correct = False
    feedback = {}

    try:
        if question_type in ['drag-drop-match', 'drag-drop-ordering']:
            total_items_count = sum(len(items) for items in solution.values())
            points_per_item = points_total / total_items_count if total_items_count > 0 else 0
            correct_matches_count = 0

            for cat_id, correct_item_ids in solution.items():
                user_items_in_cat = user_answer.get(cat_id, []) if isinstance(user_answer, dict) else []
                user_item_ids = [
                    ui.get('id') if isinstance(ui, dict) else ui
                    for ui in (user_items_in_cat if isinstance(user_items_in_cat, list) else [])
                ]

                for c_item_id in correct_item_ids:
                    if c_item_id in user_item_ids:
                        feedback[c_item_id] = 'correct'
                        score_earned += points_per_item
                        correct_matches_count += 1
                    else:
                        feedback[c_item_id] = 'incorrect'

            is_correct = (correct_matches_count == total_items_count)

        elif question_type in ['multiple-select', 'clinical-case']:
            if isinstance(user_answer, str):
                user_answer = [user_answer]
            if isinstance(user_answer, list):
                user_selections = set(user_answer)
                correct_selections = set(solution if isinstance(solution, list) else [solution])

                correct_hits = user_selections.intersection(correct_selections)
                wrong_hits = user_selections.difference(correct_selections)

                points_per_option = points_total / len(correct_selections) if len(correct_selections) > 0 else 0
                current_score = (len(correct_hits) * points_per_option) - (len(wrong_hits) * points_per_option)
                score_earned = max(0, current_score)
                is_correct = (user_selections == correct_selections)

                for opt in question.get('options', []):
                    opt_id = opt['id'] if isinstance(opt, dict) else opt
                    feedback[opt_id] = 'correct' if opt_id in correct_selections else 'incorrect'
            else:
                is_correct = False

        elif question_type == 'true-false':
            statements = question.get('statements', [])
            total_stmts = len(statements)
            points_per_stmt = points_total / total_stmts if total_stmts > 0 else 0
            solution_dict = question.get('solution', {})

            correct_count = 0
            if isinstance(user_answer, dict):
                for stmt in statements:
                    stmt_id = stmt['id']
                    expected = solution_dict.get(stmt_id, stmt.get('solution'))
                    actual = user_answer.get(stmt_id)

                    if actual == expected:
                        feedback[stmt_id] = 'correct'
                        score_earned += points_per_stmt
                        correct_count += 1
                    else:
                        feedback[stmt_id] = 'incorrect'

            is_correct = (correct_count == total_stmts)

        elif question_type == 'drag-drop-fill':
            solution_dict = question.get('solution', {})
            total_blanks = len(solution_dict)
            points_per_blank = points_total / total_blanks if total_blanks > 0 else 0

            correct_count = 0
            if isinstance(user_answer, dict):
                for blank_id, expected_val in solution_dict.items():
                    actual_val = user_answer.get(blank_id)
                    if isinstance(expected_val, list):
                        is_match = actual_val in expected_val
                    else:
                        is_match = actual_val == expected_val

                    if is_match:
                        feedback[blank_id] = 'correct'
                        score_earned += points_per_blank
                        correct_count += 1
                    else:
                        feedback[blank_id] = 'incorrect'

            is_correct = (correct_count == total_blanks)

        elif question_type == 'image-labeling':
            total_zones = len(solution.keys())
            points_per_zone = points_total / total_zones if total_zones > 0 else 0
            correct_zones_count = 0

            if isinstance(user_answer, dict):
                for zone_id, correct_vals in solution.items():
                    if not isinstance(correct_vals, list):
                        correct_vals = [correct_vals]

                    user_vals = user_answer.get(zone_id, [])
                    if not isinstance(user_vals, list):
                        user_vals = []

                    user_val_ids = [
                        val.get('id') if isinstance(val, dict) else val
                        for val in user_vals
                    ]

                    if set(user_val_ids) == set(correct_vals):
                        feedback[zone_id] = 'correct'
                        score_earned += points_per_zone
                        correct_zones_count += 1
                    else:
                        feedback[zone_id] = 'incorrect'

            is_correct = (correct_zones_count == total_zones)

    except Exception as e:
        print(f'Error calculating score: {e}')
        return 0, False, {}

    score_earned = math.ceil(score_earned) if score_earned > 0 else 0
    return score_earned, is_correct, feedback


class QuizList(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user_username = get_jwt_identity()
            user = User.find_by_username(current_user_username)
            if not user:
                return {'message': 'User not found'}, 404

            completed_quizzes = set(user.get_completed_quiz_ids())
            unlock_next = True

            units = Unit.query.order_by(Unit.order_index.asc()).all()
            path_data = []

            for unit in units:
                unit_data = {
                    'id': unit.id,
                    'title': unit.title,
                    'description': unit.description,
                    'color': unit.color,
                    'levels': [],
                }

                for quiz in unit.quizzes:
                    is_completed = quiz.id in completed_quizzes
                    is_locked = not unlock_next

                    unit_data['levels'].append({
                        'id': quiz.id,
                        'title': quiz.title,
                        'icon': quiz.icon or 'star',
                        'is_completed': is_completed,
                        'is_locked': is_locked,
                        'total_questions': len(quiz.questions),
                        'has_micro_lesson': bool(quiz.micro_lesson),
                    })

                    if is_completed:
                        unlock_next = True
                    else:
                        unlock_next = False

                path_data.append(unit_data)

            return path_data, 200
        except Exception as e:
            return {'message': str(e)}, 500


class QuizDetail(Resource):
    @jwt_required()
    def get(self, quiz_id):
        try:
            quiz = Quiz.query.filter_by(id=quiz_id).first()
            if quiz:
                return quiz.to_dict(include_questions=True), 200
            return {'message': 'آزمون یافت نشد'}, 404
        except Exception as e:
            return {'message': str(e)}, 500


class QuizSubmit(Resource):

    def _calculate_score(self, question, user_answer):
        return score_question(question, user_answer)

    def _calculate_level(self, score):
        return math.floor(int(score) / 200) + 1

    def _queue_related_flashcards(self, user_id: int, question_id: str) -> int:
        related_cards = Flashcard.query.filter_by(related_question_id=question_id).all()
        if not related_cards:
            return 0

        now = datetime.now(timezone.utc)
        queued = 0
        for card in related_cards:
            prog = UserFlashcardProgress.query.filter_by(
                user_id=user_id, flashcard_id=card.id
            ).first()
            if not prog:
                prog = UserFlashcardProgress(
                    user_id=user_id,
                    flashcard_id=card.id,
                    box=1,
                    ease_factor=2.5,
                    interval_days=1,
                    repetitions=0,
                    next_review_at=now,
                )
                db.session.add(prog)
            else:
                prog.box = 1
                prog.repetitions = 0
                prog.interval_days = 1
                prog.next_review_at = now
            queued += 1
        return queued

    def _check_and_award_badges(self, user: User):
        newly_earned_badges = []
        existing_badge_ids = set(user.get_earned_badge_ids())
        all_badges = Badge.query.all()

        for badge in all_badges:
            if badge.id in existing_badge_ids:
                continue

            criteria = badge.criteria or {}
            ctype = criteria.get('type')
            earned = False

            if ctype == 'reach_score' and user.score >= criteria.get('score', 0):
                earned = True
            elif ctype == 'reach_level' and user.level >= criteria.get('level', 1):
                earned = True
            elif ctype == 'complete_quiz' and user.quizzes_completed >= criteria.get('count', 0):
                earned = True
            elif ctype == 'correct_streak' and user.correct_streak >= criteria.get('count', 0):
                earned = True

            if earned:
                db.session.add(UserBadge(user_id=user.id, badge_id=badge.id))
                newly_earned_badges.append(badge.to_dict())

        if newly_earned_badges:
            db.session.commit()

        return newly_earned_badges

    @jwt_required()
    def post(self):
        data = request.get_json() or {}
        quiz_id = data.get('quizId')
        question_id = data.get('questionId')
        user_answer = data.get('answer')
        is_last_question = data.get('isLastQuestion', False)
        time_taken = data.get('timeTaken', 30)

        if not question_id or user_answer is None or not quiz_id:
            return {'message': 'اطلاعات ناقص است'}, 400

        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return {'message': 'آزمون یافت نشد'}, 404

        questions_list = quiz.questions
        question_obj = next((q for q in questions_list if q.id == question_id), None)
        if not question_obj:
            return {'message': 'سوال یافت نشد'}, 404

        question_index = next((i for i, q in enumerate(questions_list) if q.id == question_id), -1)
        question_dict = question_obj.to_dict()

        base_score, is_correct, feedback = self._calculate_score(question_dict, user_answer)

        speed_bonus = 0
        streak_bonus = 0
        target_time = 15

        current_user_username = get_jwt_identity()
        user = User.find_by_username(current_user_username)
        if not user:
            return {'message': 'کاربر یافت نشد'}, 404

        new_streak = user.correct_streak + 1 if is_correct else 0

        if is_correct:
            speed_bonus, target_time = calculate_speed_bonus(
                question_dict.get('type', 'multiple-select'),
                time_taken,
            )
            if new_streak > 0 and new_streak % 5 == 0:
                streak_bonus = 20

        total_question_score = base_score + speed_bonus + streak_bonus

        queued_flashcards_count = 0
        if not is_correct:
            queued_flashcards_count = self._queue_related_flashcards(user.id, question_id)

        progress = UserQuizProgress.query.filter_by(user_id=user.id, quiz_id=quiz_id).first()
        if not progress:
            progress = UserQuizProgress(
                user_id=user.id,
                quiz_id=quiz_id,
                best_score=0,
                current_session_score=0,
                current_session_correct_count=0,
                attempts=0,
                is_completed=False,
            )
            db.session.add(progress)

        if question_index == 0:
            progress.current_session_score = 0
            progress.current_session_correct_count = 0
            progress.attempts += 1

        progress.current_session_score += total_question_score
        if is_correct:
            progress.current_session_correct_count += 1

        xp_gained_this_step = 0
        stage_completed_perfectly = False

        if is_last_question:
            final_session_score = progress.current_session_score
            if final_session_score > progress.best_score:
                xp_gained_this_step = final_session_score - progress.best_score
                progress.best_score = final_session_score

            if progress.current_session_correct_count == len(questions_list):
                stage_completed_perfectly = True

            if final_session_score > 0:
                if not progress.is_completed:
                    progress.is_completed = True
                user.quizzes_completed += 1

            progress.current_session_score = 0
            progress.current_session_correct_count = 0

        new_total_score = user.score + xp_gained_this_step
        new_level = self._calculate_level(new_total_score)
        level_up = new_level > user.level

        user.score = new_total_score
        user.level = new_level
        user.correct_streak = new_streak

        db.session.commit()

        newly_earned_badges = self._check_and_award_badges(user)

        return {
            'message': 'جواب ثبت شد',
            'isCorrect': is_correct,
            'feedback': feedback,
            'scoreEarned': total_question_score,
            'xpGained': xp_gained_this_step,
            'speedBonus': speed_bonus,
            'targetTime': target_time,
            'streakBonus': streak_bonus,
            'newTotalScore': new_total_score,
            'newLevel': new_level,
            'levelUp': level_up,
            'newlyEarnedBadges': newly_earned_badges,
            'explanation': question_dict.get('explanation', ''),
            'stageCompleted': stage_completed_perfectly,
            'queuedFlashcardsCount': queued_flashcards_count,
        }, 200
