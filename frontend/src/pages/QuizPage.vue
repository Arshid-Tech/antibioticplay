<template>
  <div class="quiz-layout" :style="layoutStyles">
    <div class="bg-pattern-overlay"></div>

    <header class="quiz-header">
      <button class="close-btn" @click="confirmExit" title="خروج از آزمون">
        <font-awesome-icon icon="fas fa-times" />
      </button>

      <button
        v-if="hasMicroLesson"
        class="icon-btn micro-btn"
        @click="showMicroLessonModal = true"
        title="خلاصه درس این مرحله"
        :style="{ borderColor: themeColor, color: themeColor }"
      >
        <font-awesome-icon icon="fas fa-book-open" />
      </button>

      <button
        class="icon-btn"
        @click="handleBookmark"
        :class="{ active: isBookmarked }"
        title="ذخیره برای مرور"
        :style="bookmarkButtonStyle"
      >
        <font-awesome-icon :icon="isBookmarked ? 'fas fa-bookmark' : 'far fa-bookmark'" />
      </button>

      <div class="hint-wrapper">
        <button
          class="hint-btn icon-btn"
          @click="openHintModal"
          :disabled="hintsRemaining <= 0 && !usedHintForCurrent"
          title="راهنمایی"
          :style="hintButtonStyle"
        >
          <font-awesome-icon icon="fas fa-lightbulb" :class="{ 'bulb-on': showHintModal }" />
          <span class="hint-count" :style="{ backgroundColor: themeColor }">{{ hintsRemaining }}</span>
        </button>
      </div>

      <div class="progress-container">
        <div class="progress-bar" :style="{ width: progressPercentage + '%', backgroundColor: themeColor }">
          <div class="progress-highlight"></div>
        </div>
      </div>

      <div class="quiz-stats" v-if="currentStreak > 0">
        <font-awesome-icon icon="fas fa-fire" class="fire-icon" />
        <span>{{ currentStreak }}</span>
      </div>
    </header>

    <main class="quiz-body" ref="quizBody">
      <div v-if="quizStore.loading" class="loading-state">
        در حال آماده‌سازی سوالات...
      </div>

      <div v-else-if="currentQuestion" class="question-container" :class="{ 'shake-animation': applyShake }">
        <div v-if="duelId" class="duel-mode-banner">
          ⚔️ در حال انجام دوئل هم‌کلاسی — بهترین عملکردت را ثبت کن!
        </div>

        <h2 class="question-title">{{ currentQuestion.title }}</h2>

        <component
          :is="getComponentType(currentQuestion.type)"
          :question="currentQuestion"
          :feedback="feedback"
          :disabled="quizState !== 'answering'"
          @update:answer="userAnswer = $event"
        />
      </div>
    </main>

    <!-- مودال مینی‌درس (خلاصه درس پیش از مرحله) -->
    <transition name="fade">
      <div v-if="showMicroLessonModal" class="modal-overlay" @click.self="showMicroLessonModal = false">
        <div class="modal-card micro-lesson-card">
          <div class="modal-header">
            <h3>📖 خلاصه درس مرحله: {{ quizStore.currentQuiz?.title }}</h3>
            <button class="modal-close-icon" @click="showMicroLessonModal = false">
              <font-awesome-icon icon="fas fa-times" />
            </button>
          </div>
          <div class="modal-body micro-lesson-body">
            <p v-for="(line, idx) in microLessonLines" :key="idx" :class="{ 'lesson-heading': line.startsWith('###') }">
              {{ line.replace(/^###\s*/, '') }}
            </p>
          </div>
          <div class="modal-footer-actions">
            <button class="btn btn-primary" @click="showMicroLessonModal = false">
              متوجه شدم، شروع آزمون!
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- مودال راهنما -->
    <transition name="fade">
      <div v-if="showHintModal" class="modal-overlay" @click.self="showHintModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3>💡 راهنمایی علمی</h3>
            <button class="modal-close-icon" @click="showHintModal = false">
              <font-awesome-icon icon="fas fa-times" />
            </button>
          </div>

          <div class="modal-body">
            <div v-if="isImageHint" class="hint-image-wrapper">
              <img :src="currentQuestion.hint" alt="Hint Image" class="hint-img-content" />
            </div>
            <p v-else>
              {{ currentQuestion?.hint || 'راهنمایی برای این سوال موجود نیست.' }}
            </p>
          </div>
        </div>
      </div>
    </transition>

    <!-- دیالوگ دانشمند انتخابی کاربر -->
    <transition name="slide-up">
      <div v-if="(quizState === 'correct' || quizState === 'incorrect') && activeDialogue" class="character-popup">
        <img :src="activeDialogue.avatarUrl" class="character-img scientist-avatar" :alt="activeDialogue.name" />
        <div class="speech-bubble" :class="{ 'correct-bubble': quizState === 'correct' }">
          <span class="speaker-name">{{ activeDialogue.name }}:</span>
          <span>{{ activeDialogue.text }}</span>
        </div>
      </div>
    </transition>

    <Confetti v-if="quizState === 'correct'" />

    <footer
      class="quiz-footer"
      :class="{
        'footer-correct': quizState === 'correct',
        'footer-incorrect': quizState === 'incorrect',
      }"
    >
      <div class="footer-content">
        <div v-if="quizState !== 'answering'" class="feedback-message">
          <div class="feedback-icon-circle">
            <font-awesome-icon :icon="quizState === 'correct' ? 'fas fa-check' : 'fas fa-times'" />
          </div>
          <div class="feedback-text">
            <h3 v-if="quizState === 'correct'">
              عالی بود!
              <span v-if="lastSpeedBonus > 0" class="bonus-chip">⚡ +{{ lastSpeedBonus }} سرعت</span>
              <span v-if="lastStreakBonus > 0" class="bonus-chip streak">🔥 +{{ lastStreakBonus }} استریک</span>
            </h3>
            <h3 v-else>اشتباه بود!</h3>

            <p v-if="explanationText" class="explanation-text">{{ explanationText }}</p>
            <p v-if="queuedFlashcardsCount > 0" class="flashcard-queue-note">
              🗂️ {{ queuedFlashcardsCount }} فلش‌کارت مرتبط برای مرور به صف امروز شما اضافه شد.
            </p>
          </div>
        </div>

        <div class="action-button-wrapper">
          <button
            v-if="quizState === 'answering'"
            @click="checkAnswer"
            class="btn check-btn"
            :style="checkButtonStyle"
            :disabled="!isAnswerComplete"
          >
            بررسی
          </button>

          <button
            v-else
            @click="handleContinue"
            class="btn continue-btn"
            :class="quizState === 'correct' ? 'btn-primary' : 'btn-danger'"
          >
            ادامه
          </button>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useQuizStore } from '../stores/quiz';
import { useAuthStore } from '../stores/auth';
import { useBookmarkStore } from '../stores/bookmarkStore';
import challengeService from '../services/challengeService';
import { getScientistDialogue } from '../utils/scientistDialogues';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faTimes,
  faCheck,
  faFire,
  faLightbulb,
  faBookOpen,
  faBookmark as fasBookmark,
} from '@fortawesome/free-solid-svg-icons';
import { faBookmark as farBookmark } from '@fortawesome/free-regular-svg-icons';

import DragDropMatch from '../components/DragDropMatch.vue';
import MultipleSelect from '../components/MultipleSelect.vue';
import TrueFalse from '../components/TrueFalse.vue';
import DragDropFill from '../components/DragDropFill.vue';
import ImageLabeling from '../components/ImageLabeling.vue';
import ClinicalCase from '../components/ClinicalCase.vue';
import Confetti from '../components/Confetti.vue';

library.add(faTimes, faCheck, faFire, faLightbulb, faBookOpen, fasBookmark, farBookmark);

const route = useRoute();
const router = useRouter();
const quizStore = useQuizStore();
const authStore = useAuthStore();
const bookmarkStore = useBookmarkStore();
const quizBody = ref(null);

const currentQuestionIndex = ref(0);
const userAnswer = ref(null);
const feedback = ref({});
const quizState = ref('answering');
const currentStreak = ref(0);
const applyShake = ref(false);
const explanationText = ref('');
const questionStartTime = ref(Date.now());
const hintsRemaining = ref(3);
const showHintModal = ref(false);
const usedHintForCurrent = ref(false);
const showMicroLessonModal = ref(false);
const activeDialogue = ref(null);
const lastSpeedBonus = ref(0);
const lastStreakBonus = ref(0);
const queuedFlashcardsCount = ref(0);

const duelId = computed(() => route.query.duelId || null);

const hasMicroLesson = computed(() => Boolean(quizStore.currentQuiz?.micro_lesson));
const microLessonLines = computed(() => {
  const raw = quizStore.currentQuiz?.micro_lesson || '';
  return raw.split('\n').map((l) => l.trim()).filter(Boolean);
});

const isImageHint = computed(() => {
  const hint = currentQuestion.value?.hint;
  if (!hint) return false;
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'];
  return imageExtensions.some((ext) => hint.toLowerCase().endsWith(ext));
});

const themeColor = computed(() => route.query.theme || '#58cc02');

const layoutStyles = computed(() => {
  const svgPattern = `data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E`;
  return {
    backgroundColor: `${themeColor.value}1a`,
    backgroundImage: `url("${svgPattern}")`,
  };
});

function adjustColor(color, amount) {
  return (
    '#' +
    color
      .replace(/^#/, '')
      .replace(/../g, (c) =>
        ('0' + Math.min(255, Math.max(0, parseInt(c, 16) + amount)).toString(16)).substr(-2)
      )
  );
}

const checkButtonStyle = computed(() => ({
  backgroundColor: themeColor.value,
  color: 'white',
  borderBottomColor: adjustColor(themeColor.value, -20),
}));

const hintButtonStyle = computed(() => ({
  borderColor: themeColor.value,
  color: themeColor.value,
}));

const bookmarkButtonStyle = computed(() => ({
  color: isBookmarked.value ? themeColor.value : '#e5e5e5',
  borderColor: isBookmarked.value ? themeColor.value : '#e5e5e5',
}));

const currentQuestion = computed(() => {
  if (quizStore.currentQuiz?.questions) {
    return quizStore.currentQuiz.questions[currentQuestionIndex.value];
  }
  return null;
});

const getComponentType = (type) => {
  if (type === 'drag-drop-match' || type === 'drag-drop-ordering') return DragDropMatch;
  if (type === 'multiple-select') return MultipleSelect;
  if (type === 'true-false') return TrueFalse;
  if (type === 'drag-drop-fill') return DragDropFill;
  if (type === 'image-labeling') return ImageLabeling;
  if (type === 'clinical-case') return ClinicalCase;
  return null;
};

const progressPercentage = computed(() => {
  if (!quizStore.currentQuiz?.questions) return 0;
  return (currentQuestionIndex.value / quizStore.currentQuiz.questions.length) * 100;
});

const isAnswerComplete = computed(() => {
  if (!currentQuestion.value || userAnswer.value === null) return false;
  const type = currentQuestion.value.type;
  const answer = userAnswer.value;

  if (type === 'drag-drop-match' || type === 'drag-drop-ordering') {
    const totalItems = currentQuestion.value.items ? currentQuestion.value.items.length : 0;
    const currentBankCount = answer.bank ? answer.bank.length : 0;
    return totalItems > 0 && currentBankCount < totalItems;
  }
  if (type === 'multiple-select' || type === 'clinical-case') {
    return Array.isArray(answer) && answer.length > 0;
  }
  if (type === 'true-false') {
    return currentQuestion.value.statements.length === Object.keys(answer).length;
  }
  if (type === 'drag-drop-fill') {
    const template = currentQuestion.value.instruction_template || '';
    const matches = template.match(/_BLANK[0-9]+_/g);
    const totalBlanks = matches ? matches.length : 0;
    return totalBlanks > 0 && totalBlanks === Object.values(answer).filter(Boolean).length;
  }
  if (type === 'image-labeling') {
    if (!answer || typeof answer !== 'object') return false;
    const placedItemsCount = Object.values(answer).reduce(
      (count, items) => count + (Array.isArray(items) ? items.length : 0),
      0
    );
    return placedItemsCount > 0;
  }
  return true;
});

const isBookmarked = computed(() => {
  if (!currentQuestion.value || !quizStore.currentQuiz) return false;
  return bookmarkStore.isBookmarked(quizStore.currentQuiz.id, currentQuestion.value.id);
});

const handleBookmark = async () => {
  if (!currentQuestion.value || !quizStore.currentQuiz) return;
  await bookmarkStore.toggleBookmark(quizStore.currentQuiz.id, currentQuestion.value.id);
};

watch(currentQuestion, () => {
  questionStartTime.value = Date.now();
  showHintModal.value = false;
  usedHintForCurrent.value = false;
  userAnswer.value = null;
});

onMounted(async () => {
  const quizId = route.params.id;
  if (quizId) {
    await quizStore.fetchQuizDetails(quizId);
    if (quizStore.currentQuiz?.micro_lesson && !duelId.value) {
      showMicroLessonModal.value = true;
    }
  }
});

const openHintModal = () => {
  if (!usedHintForCurrent.value) {
    if (hintsRemaining.value <= 0) return;
    hintsRemaining.value--;
    usedHintForCurrent.value = true;
  }
  showHintModal.value = true;
};

const playSound = (soundFile) => {
  try {
    const audio = new Audio(`/${soundFile}`);
    audio.play();
  } catch (error) {
    console.error('Error playing sound:', error);
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (quizBody.value) {
      quizBody.value.scrollTo({
        top: quizBody.value.scrollHeight,
        behavior: 'smooth',
      });
    }
  });
};

const checkAnswer = async () => {
  if (!currentQuestion.value) return;
  const timeTaken = Math.floor((Date.now() - questionStartTime.value) / 1000);
  const isLast = currentQuestionIndex.value >= quizStore.currentQuiz.questions.length - 1;

  try {
    const response = await quizStore.submitAnswer(
      quizStore.currentQuiz.id,
      currentQuestion.value.id,
      userAnswer.value,
      isLast,
      timeTaken
    );

    const data = response.data;
    feedback.value = data.feedback || {};
    explanationText.value = data.explanation || '';
    lastSpeedBonus.value = data.speedBonus || 0;
    lastStreakBonus.value = data.streakBonus || 0;
    queuedFlashcardsCount.value = data.queuedFlashcardsCount || 0;

    authStore.updateUserScore(data.newTotalScore);
    authStore.updateUserLevel(data.newLevel);
    quizStore.addSessionScore(data.scoreEarned);

    if (data.newlyEarnedBadges?.length > 0) {
      quizStore.setNewlyEarnedBadges(data.newlyEarnedBadges);
    }

    const avatarId = authStore.user?.avatar_id || 'fleming';
    if (data.isCorrect) {
      playSound('correct.mp3');
      quizState.value = 'correct';
      currentStreak.value++;
      activeDialogue.value = getScientistDialogue(avatarId, 'correct', currentStreak.value);
    } else {
      playSound('incorrect.mp3');
      quizState.value = 'incorrect';
      currentStreak.value = 0;
      activeDialogue.value = getScientistDialogue(avatarId, 'incorrect', 0);
      applyShake.value = true;
      setTimeout(() => {
        applyShake.value = false;
      }, 500);
    }

    scrollToBottom();
  } catch (err) {
    console.error('Error checking answer:', err);
  }
};

const handleContinue = async () => {
  if (currentQuestionIndex.value < quizStore.currentQuiz.questions.length - 1) {
    currentQuestionIndex.value++;
    quizState.value = 'answering';
    feedback.value = {};
    userAnswer.value = null;
    explanationText.value = '';
    activeDialogue.value = null;
    queuedFlashcardsCount.value = 0;
  } else {
    currentStreak.value = 0;
    if (duelId.value) {
      try {
        await challengeService.submitDuel(duelId.value, quizStore.currentSessionScore);
      } catch (err) {
        console.error('Error submitting duel:', err);
      }
      router.push({ name: 'Duel', params: { id: duelId.value } });
    } else {
      router.push({ name: 'QuizResult' });
    }
  }
};

const confirmExit = () => {
  if (confirm('آیا مطمئنید می‌خواهید آزمون را ترک کنید؟')) router.push('/dashboard');
};
</script>

<style scoped>
.quiz-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  background-color: white;
  overflow: hidden;
  position: relative;
}

.bg-pattern-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.quiz-header {
  flex: 0 0 auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  background-color: transparent;
  z-index: 20;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(0, 0, 0, 0.3);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  min-width: auto;
}
.close-btn:hover {
  color: rgba(0, 0, 0, 0.6);
}

.icon-btn {
  background: white;
  border: 2px solid;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom-width: 4px;
  padding: 0;
  min-width: auto;
  font-size: 1.1rem;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}
.icon-btn:active:not(:disabled) {
  transform: translateY(2px);
  border-bottom-width: 2px;
}
.icon-btn.active {
  background-color: #fffdf0;
}

.hint-wrapper {
  position: relative;
}
.bulb-on {
  filter: drop-shadow(0 0 5px currentColor);
}
.hint-count {
  position: absolute;
  top: -5px;
  right: -5px;
  color: white;
  font-size: 0.75rem;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
}

.progress-container {
  flex-grow: 1;
  height: 16px;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  overflow: hidden;
  margin: 0 0.5rem;
}
.progress-bar {
  height: 100%;
  border-radius: 10px;
  position: relative;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.progress-highlight {
  position: absolute;
  top: 20%;
  left: 5%;
  right: 5%;
  height: 30%;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}

.quiz-stats {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #ff9600;
  font-weight: bold;
  font-size: 1.2rem;
}

.quiz-body {
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 1rem 2rem 2rem;
  display: flex;
  justify-content: center;
  position: relative;
  scroll-behavior: smooth;
  z-index: 10;
}

.question-container {
  width: 100%;
  max-width: 800px;
  text-align: center;
  margin-top: 0.5rem;
}

.duel-mode-banner {
  background: #ede7f6;
  color: #4a148c;
  padding: 0.6rem 1rem;
  border-radius: 12px;
  font-weight: 800;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.question-title {
  font-size: 1.65rem;
  color: var(--color-text);
  margin-bottom: 1.5rem;
  text-align: right;
  font-weight: 800;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 1rem;
  direction: rtl;
}

.modal-card {
  background: #fff;
  border-radius: 20px;
  max-width: 560px;
  width: 100%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.05rem;
  color: #2c3e50;
}

.modal-close-icon {
  background: #f0f0f0;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  color: #666;
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: auto !important;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  text-align: right;
  line-height: 1.8;
  color: #374151;
}

.micro-lesson-body p {
  margin: 0 0 0.75rem;
  font-size: 0.94rem;
}

.micro-lesson-body .lesson-heading {
  font-weight: 900;
  font-size: 1.05rem;
  color: #0277bd;
  margin-bottom: 0.9rem;
}

.modal-footer-actions {
  padding: 0.9rem 1.25rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
}

.hint-image-wrapper {
  display: flex;
  justify-content: center;
}

.hint-img-content {
  max-width: 100%;
  max-height: 300px;
  border-radius: 12px;
  object-fit: contain;
}

/* Scientist Dialogue Popup */
.character-popup {
  position: fixed;
  bottom: 155px;
  right: 20px;
  z-index: 90;
  display: flex;
  align-items: flex-end;
  gap: 10px;
  pointer-events: none;
  max-width: 360px;
}

.scientist-avatar {
  width: 78px;
  height: 78px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
  background: #fff;
  flex-shrink: 0;
}

.speech-bubble {
  background: white;
  border: 2px solid #ffcdd2;
  padding: 0.75rem 1rem;
  border-radius: 18px 18px 0 18px;
  font-weight: 700;
  color: #c62828;
  font-size: 0.88rem;
  line-height: 1.5;
  text-align: right;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.correct-bubble {
  color: #2e7d32;
  border-color: #a5d6a7;
  background-color: #fafff5;
}

.speaker-name {
  display: block;
  font-size: 0.76rem;
  opacity: 0.75;
  margin-bottom: 0.15rem;
}

/* Footer */
.quiz-footer {
  flex: 0 0 auto;
  width: 100%;
  padding: 1.5rem 2rem;
  border-top: 2px solid rgba(0, 0, 0, 0.05);
  background-color: white;
  transition: background-color 0.2s, border-color 0.2s;
  z-index: 100;
  position: relative;
}

.footer-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feedback-message {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  flex: 1;
}

.feedback-icon-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.8rem;
  flex-shrink: 0;
}

.footer-correct .feedback-icon-circle { color: var(--color-primary); }
.footer-incorrect .feedback-icon-circle { color: var(--color-danger); }

.feedback-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: right;
}

.feedback-text h3 {
  margin: 0 0 0.4rem;
  font-size: 1.4rem;
  font-weight: 900;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.bonus-chip {
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.85);
  color: #0277bd;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
}

.bonus-chip.streak {
  color: #e65100;
}

.footer-correct .feedback-text h3 { color: var(--color-primary-dark); }
.footer-incorrect .feedback-text h3 { color: var(--color-danger-dark); }

.explanation-text {
  font-size: 0.95rem;
  color: #4b4b4b;
  margin: 0;
  line-height: 1.6;
  max-width: 650px;
}

.flashcard-queue-note {
  margin: 0.45rem 0 0;
  font-size: 0.82rem;
  font-weight: 700;
  color: #5d4037;
}

.action-button-wrapper {
  margin-right: 1.5rem;
}

.check-btn,
.continue-btn {
  min-width: 170px;
  padding: 0.95rem 2rem;
  font-size: 1.1rem;
}

.footer-correct { background-color: #d7ffb8; border-color: #d7ffb8; }
.footer-incorrect { background-color: #ffdfe0; border-color: #ffdfe0; }

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(40px);
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .footer-content {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  .action-button-wrapper {
    width: 100%;
    margin: 0;
  }
  .check-btn,
  .continue-btn {
    width: 100%;
  }
  .character-popup {
    display: none;
  }
  .quiz-header {
    padding: 0.8rem 1rem;
    gap: 0.5rem;
  }
  .icon-btn {
    width: 38px;
    height: 38px;
  }
}
</style>
