<template>
  <div class="result-page">
    <div class="result-header">
      <h1 class="completion-title">درس تمام شد!</h1>
      <div class="result-image-wrapper">
        <img :src="resultImage" class="result-img" alt="Result" />
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card xp-card">
        <div class="stat-label">XP دریافتی</div>
        <div class="stat-value text-warning">
          <font-awesome-icon icon="fas fa-plus" class="small-icon" />
          {{ xpGainedDisplay }}
        </div>
      </div>

      <div class="stat-card streak-card">
        <div class="stat-label">پاسخ صحیح متوالی</div>
        <div class="stat-value text-fire">
          <font-awesome-icon icon="fas fa-fire" />
          {{ authStore.user?.correct_streak || 0 }}
        </div>
      </div>

      <div class="stat-card feedback-card">
        <div class="stat-label">عملکرد</div>
        <div class="stat-value text-primary">
          {{ performanceLabel }}
        </div>
      </div>
    </div>

    <div v-if="didLevelUp" class="level-up-banner slide-up-animation">
      <div class="level-content">
        <font-awesome-icon icon="fas fa-arrow-up" class="level-icon" />
        <div>
          <h3>ارتقای سطح!</h3>
          <p>تبریک! شما به سطح {{ authStore.level }} رسیدید.</p>
        </div>
      </div>
    </div>

    <footer class="result-footer">
      <button
        v-if="quizStore.currentQuiz?.id"
        class="btn duel-share-btn"
        :disabled="creatingDuel"
        @click="createAndShareDuel"
      >
        ⚔️ {{ creatingDuel ? 'در حال ساخت لینک دوئل...' : 'به چالش کشیدن هم‌کلاسی (ساخت دوئل)' }}
      </button>

      <router-link to="/dashboard" class="btn btn-primary continue-btn">
        ادامه
      </router-link>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useQuizStore } from '../stores/quiz';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notificationStore';
import challengeService from '../services/challengeService';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faFire, faPlus, faArrowUp } from '@fortawesome/free-solid-svg-icons';

import resultGoodImg from '../assets/result_good.jpg';
import resultBadImg from '../assets/result_bad.jpg';

library.add(faFire, faPlus, faArrowUp);

const router = useRouter();
const quizStore = useQuizStore();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const creatingDuel = ref(false);

const xpGainedDisplay = computed(() => {
  return quizStore.lastSubmissionResult?.xpGained || 0;
});

const performanceLabel = computed(() => {
  const score = quizStore.currentSessionScore;
  const possible = quizStore.currentQuiz?.total_possible_score || 50;
  const percentage = (score / possible) * 100;

  if (percentage >= 80) return 'عالی!';
  if (percentage >= 50) return 'خوب';
  return 'تلاش بیشتر';
});

const resultImage = computed(() => {
  const score = quizStore.currentSessionScore;
  const possible = quizStore.currentQuiz?.total_possible_score || 50;
  return score >= possible / 2 ? resultGoodImg : resultBadImg;
});

const didLevelUp = computed(() => {
  return quizStore.lastSubmissionResult && quizStore.lastSubmissionResult.levelUp;
});

const createAndShareDuel = async () => {
  if (!quizStore.currentQuiz?.id || creatingDuel.value) return;
  creatingDuel.value = true;
  try {
    const res = await challengeService.createDuel(
      quizStore.currentQuiz.id,
      quizStore.currentSessionScore
    );
    const duelId = res.data.duel_id;
    const shareUrl = `${window.location.origin}/duel/${duelId}`;
    try {
      await navigator.clipboard.writeText(shareUrl);
      notificationStore.showNotification({
        title: '⚔️ لینک دوئل ساخته و کپی شد!',
        message: 'لینک را برای هم‌کلاسی‌تان بفرستید تا ببینید کی امتیاز بالاتری می‌گیرد.',
      });
    } catch {
      // Clipboard might be blocked; user is redirected to duel page anyway
    }
    router.push({ name: 'Duel', params: { id: duelId } });
  } catch (err) {
    notificationStore.showNotification({
      title: 'خطا',
      message: 'در ساخت لینک دوئل خطایی رخ داد.',
    });
  } finally {
    creatingDuel.value = false;
  }
};
</script>

<style scoped>
.result-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: white;
  padding: 2rem;
  text-align: center;
}

.result-header {
  margin-top: 2rem;
  margin-bottom: 2.5rem;
}

.completion-title {
  color: var(--color-warning);
  font-size: 2.4rem;
  font-weight: 900;
  margin-bottom: 1rem;
}

.result-image-wrapper {
  width: 190px;
  height: 190px;
  margin: 0 auto;
}

.result-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  width: 100%;
  max-width: 600px;
  margin-bottom: 2rem;
}

.stat-card {
  background-color: #fff;
  border: 2px solid var(--color-border);
  border-radius: 16px;
  padding: 1rem 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 0 var(--color-border);
}

.stat-label {
  font-size: 0.9rem;
  color: var(--color-text-light);
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 900;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.text-warning { color: var(--color-warning); }
.text-fire { color: #ff9600; }
.text-primary { color: var(--color-primary); }
.small-icon { font-size: 1rem; }

.level-up-banner {
  background-color: #d7ffb8;
  border: 2px solid var(--color-primary);
  border-radius: 16px;
  padding: 1rem 2rem;
  margin-bottom: 2rem;
  width: 100%;
  max-width: 600px;
  box-sizing: border-box;
}

.level-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: right;
}

.level-icon {
  font-size: 2rem;
  color: var(--color-primary);
  background: white;
  padding: 10px;
  border-radius: 50%;
}

.level-content h3 { margin: 0 0 0.2rem; color: var(--color-primary-dark); }
.level-content p { margin: 0; color: var(--color-text); font-size: 0.95rem; }

.result-footer {
  margin-top: auto;
  width: 100%;
  max-width: 600px;
  padding-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.duel-share-btn {
  width: 100%;
  padding: 0.95rem;
  font-size: 1.02rem;
  background: #ede7f6;
  color: #4a148c;
  border: 2px solid #b39ddb;
  border-bottom-width: 4px;
  border-radius: 14px;
  font-weight: 800;
  cursor: pointer;
}

.continue-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.2rem;
}

@media (max-width: 600px) {
  .stats-grid { grid-template-columns: 1fr; }
  .stat-card { flex-direction: row; justify-content: space-between; padding: 1rem 2rem; }
  .stat-label { margin-bottom: 0; }
}
</style>
