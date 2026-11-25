<template>
  <div class="daily-page">
    <header class="daily-header">
      <div class="header-inner">
        <router-link to="/dashboard" class="back-btn">
          <font-awesome-icon icon="fas fa-arrow-right" />
        </router-link>
        <div>
          <h1>⚡ چالش روزانه آنتی‌بیوتیک</h1>
          <p>۵ سوال تصادفی امروز با پاداش ویژه XP</p>
        </div>
      </div>
    </header>

    <main class="daily-body">
      <div v-if="loading" class="state-card">در حال آماده‌سازی چالش امروز...</div>

      <div v-else-if="finished" class="state-card finish-card">
        <div class="trophy">🏆</div>
        <h2>چالش روزانه کامل شد!</h2>
        <p>
          شما به <strong>{{ correctCount }}</strong> از <strong>{{ questions.length }}</strong> سوال
          پاسخ صحیح دادید و <strong>+{{ totalXpEarned }} XP</strong> پاداش گرفتید.
        </p>
        <router-link to="/dashboard" class="btn btn-primary">بازگشت به داشبورد</router-link>
      </div>

      <div v-else-if="currentQuestion" class="question-wrapper">
        <div class="progress-row">
          <span>سوال {{ currentIndex + 1 }} از {{ questions.length }}</span>
          <span class="xp-pill">+{{ totalXpEarned }} XP</span>
        </div>
        <div class="progress-bar-bg">
          <div
            class="progress-bar-fill"
            :style="{ width: `${((currentIndex + 1) / questions.length) * 100}%` }"
          ></div>
        </div>

        <h2 class="q-title">{{ currentQuestion.title }}</h2>

        <component
          :is="getComponentType(currentQuestion.type)"
          :question="currentQuestion"
          :feedback="feedback"
          :disabled="state !== 'answering'"
          @update:answer="userAnswer = $event"
        />

        <div v-if="state !== 'answering'" class="feedback-box" :class="state">
          <strong>{{ state === 'correct' ? '✅ پاسخ صحیح!' : '❌ پاسخ نادرست' }}</strong>
          <p v-if="explanation">{{ explanation }}</p>
        </div>

        <div class="action-row">
          <button
            v-if="state === 'answering'"
            class="btn btn-primary action-btn"
            :disabled="!canSubmit"
            @click="submitAnswer"
          >
            بررسی پاسخ
          </button>
          <button
            v-else
            class="btn action-btn"
            :class="state === 'correct' ? 'btn-primary' : 'btn-danger'"
            @click="nextQuestion"
          >
            {{ currentIndex + 1 < questions.length ? 'سوال بعدی' : 'مشاهده نتیجه' }}
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import challengeService from '../services/challengeService';
import { useAuthStore } from '../stores/auth';
import DragDropMatch from '../components/DragDropMatch.vue';
import MultipleSelect from '../components/MultipleSelect.vue';
import TrueFalse from '../components/TrueFalse.vue';
import DragDropFill from '../components/DragDropFill.vue';
import ImageLabeling from '../components/ImageLabeling.vue';
import ClinicalCase from '../components/ClinicalCase.vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';

library.add(faArrowRight);

const authStore = useAuthStore();

const loading = ref(true);
const questions = ref([]);
const currentIndex = ref(0);
const userAnswer = ref(null);
const feedback = ref({});
const explanation = ref('');
const state = ref('answering'); // answering | correct | incorrect
const finished = ref(false);
const correctCount = ref(0);
const totalXpEarned = ref(0);

const currentQuestion = computed(() => questions.value[currentIndex.value] || null);

const getComponentType = (type) => {
  if (type === 'drag-drop-match' || type === 'drag-drop-ordering') return DragDropMatch;
  if (type === 'multiple-select') return MultipleSelect;
  if (type === 'true-false') return TrueFalse;
  if (type === 'drag-drop-fill') return DragDropFill;
  if (type === 'image-labeling') return ImageLabeling;
  if (type === 'clinical-case') return ClinicalCase;
  return null;
};

const canSubmit = computed(() => {
  if (!currentQuestion.value || userAnswer.value === null) return false;
  const ans = userAnswer.value;
  if (Array.isArray(ans)) return ans.length > 0;
  if (typeof ans === 'object') return Object.keys(ans).length > 0;
  return true;
});

onMounted(async () => {
  try {
    const res = await challengeService.getDailyChallenge();
    questions.value = res.data.questions || [];
  } catch (err) {
    console.error('Failed to load daily challenge:', err);
  } finally {
    loading.value = false;
  }
});

const submitAnswer = async () => {
  if (!currentQuestion.value) return;
  const isLast = currentIndex.value >= questions.value.length - 1;
  try {
    const res = await challengeService.submitDailyAnswer(
      currentQuestion.value.id,
      userAnswer.value,
      isLast
    );
    const data = res.data;
    feedback.value = data.feedback || {};
    explanation.value = data.explanation || '';
    state.value = data.isCorrect ? 'correct' : 'incorrect';
    if (data.isCorrect) correctCount.value += 1;
    totalXpEarned.value += data.xpAwarded || 0;
    if (typeof data.newTotalScore === 'number') {
      authStore.updateUserScore(data.newTotalScore);
      authStore.updateUserLevel(data.newLevel);
    }
  } catch (err) {
    console.error('Failed to submit daily answer:', err);
  }
};

const nextQuestion = () => {
  if (currentIndex.value + 1 < questions.value.length) {
    currentIndex.value += 1;
    userAnswer.value = null;
    feedback.value = {};
    explanation.value = '';
    state.value = 'answering';
  } else {
    finished.value = true;
  }
};
</script>

<style scoped>
.daily-page {
  min-height: 100vh;
  background: #f6f8fb;
  direction: rtl;
  padding-bottom: 3rem;
}

.daily-header {
  background: linear-gradient(135deg, #ff9600, #ff6f00);
  color: #fff;
  padding: 1rem 1.5rem;
}

.header-inner {
  max-width: 820px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.daily-header h1 {
  margin: 0;
  font-size: 1.25rem;
}

.daily-header p {
  margin: 0.15rem 0 0;
  font-size: 0.85rem;
  opacity: 0.92;
}

.daily-body {
  max-width: 820px;
  margin: 1.5rem auto;
  padding: 0 1rem;
}

.state-card {
  background: #fff;
  border: 2px solid #e5e5e5;
  border-radius: 20px;
  padding: 2.5rem 1.5rem;
  text-align: center;
}

.trophy {
  font-size: 3.5rem;
  margin-bottom: 0.5rem;
}

.question-wrapper {
  background: #fff;
  border: 2px solid #e5e5e5;
  border-radius: 20px;
  padding: 1.5rem;
}

.progress-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-weight: 800;
  color: #555;
}

.xp-pill {
  background: #fff3e0;
  color: #e65100;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.85rem;
}

.progress-bar-bg {
  height: 10px;
  background: #eceff1;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 1.25rem;
}

.progress-bar-fill {
  height: 100%;
  background: #ff9600;
  transition: width 0.3s ease;
}

.q-title {
  margin: 0 0 1.2rem;
  font-size: 1.25rem;
  color: #2c3e50;
}

.feedback-box {
  margin-top: 1.25rem;
  padding: 1rem;
  border-radius: 12px;
}

.feedback-box.correct {
  background: #e8f5e9;
  color: #1b5e20;
}

.feedback-box.incorrect {
  background: #ffebee;
  color: #b71c1c;
}

.feedback-box p {
  margin: 0.4rem 0 0;
  font-size: 0.92rem;
  line-height: 1.65;
}

.action-row {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
}

.action-btn {
  min-width: 200px;
  padding: 0.85rem 1.5rem;
}
</style>
