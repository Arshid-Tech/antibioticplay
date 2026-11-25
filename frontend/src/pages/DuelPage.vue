<template>
  <div class="duel-page">
    <div class="duel-card">
      <div v-if="loading" class="center-msg">در حال بارگذاری اطلاعات دوئل...</div>

      <div v-else-if="error" class="center-msg error">
        <p>{{ error }}</p>
        <router-link to="/dashboard" class="btn btn-primary">بازگشت به داشبورد</router-link>
      </div>

      <template v-else-if="duel">
        <span class="duel-badge">دوئل هم‌کلاسی‌ها</span>
        <h1 class="duel-title">{{ duel.quiz_title }}</h1>

        <div class="versus-row">
          <div class="player-box">
            <img
              :src="`/avatars/avatar_${duel.challenger.avatar_id || 'fleming'}.png`"
              class="duel-avatar"
              alt="Challenger"
            />
            <strong>{{ duel.challenger.full_name }}</strong>
            <span class="score-tag">{{ toFa(duel.challenger.score) }} امتیاز</span>
          </div>

          <div class="vs-circle">VS</div>

          <div class="player-box">
            <template v-if="duel.opponent">
              <img
                :src="`/avatars/avatar_${duel.opponent.avatar_id || 'fleming'}.png`"
                class="duel-avatar"
                alt="Opponent"
              />
              <strong>{{ duel.opponent.full_name }}</strong>
              <span class="score-tag">{{ toFa(duel.opponent.score) }} امتیاز</span>
            </template>
            <template v-else>
              <div class="duel-avatar placeholder">؟</div>
              <strong>حریف منتظر است</strong>
              <span class="score-tag pending">آماده رقابت</span>
            </template>
          </div>
        </div>

        <div v-if="duel.status === 'completed'" class="result-banner">
          <h2 v-if="duel.winner === 'tie'">مسابقه مساوی شد!</h2>
          <h2 v-else-if="duel.winner === 'challenger'">
            برنده: {{ duel.challenger.full_name }}
          </h2>
          <h2 v-else>برنده: {{ duel.opponent?.full_name }}</h2>
          <p>برنده دوئل +۳۰ XP پاداش دریافت کرد.</p>
          <router-link to="/dashboard" class="btn btn-primary">بازگشت به داشبورد</router-link>
        </div>

        <div v-else class="duel-actions">
          <p v-if="isSelfChallenger" class="self-note">
            این لینک دوئلِ خودِ شماست! لینک صفحه را کپی کنید و برای هم‌کلاسی‌تان بفرستید:
          </p>
          <div v-if="isSelfChallenger" class="share-row">
            <button class="btn btn-primary" @click="copyLink">کپی لینک دوئل</button>
            <router-link to="/dashboard" class="btn btn-outline">داشبورد</router-link>
          </div>
          <div v-else class="accept-row">
            <p>فکر می‌کنی می‌تونی امتیاز <strong>{{ toFa(duel.challenger.score) }}</strong> رو بشکنی؟</p>
            <button class="btn btn-primary start-duel-btn" @click="acceptDuel">
              قبول چالش و شروع آزمون
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import challengeService from '../services/challengeService';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notificationStore';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const loading = ref(true);
const error = ref('');
const duel = ref(null);

const toFa = (val) => {
  if (val === null || val === undefined) return '';
  return String(val).replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[Number(d)]);
};

const isSelfChallenger = computed(() => {
  return duel.value && duel.value.challenger?.username === authStore.username;
});

onMounted(async () => {
  try {
    const res = await challengeService.getDuel(route.params.id);
    duel.value = res.data;
  } catch (err) {
    error.value = 'لینک دوئل نامعتبر است یا یافت نشد.';
  } finally {
    loading.value = false;
  }
});

const acceptDuel = () => {
  router.push({
    name: 'Quiz',
    params: { id: duel.value.quiz_id },
    query: { duelId: duel.value.id, theme: '#1d5c8c' },
  });
};

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href);
    notificationStore.showNotification({
      title: 'لینک کپی شد',
      message: 'لینک دوئل را برای هم‌کلاسی خود ارسال کنید تا امتیازتان مقایسه شود.',
    });
  } catch {
    notificationStore.showNotification({
      title: 'لینک دوئل',
      message: window.location.href,
    });
  }
};
</script>

<style scoped>
.duel-page {
  min-height: 100vh;
  background-color: var(--color-background-page);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  direction: rtl;
}

.duel-card {
  width: 100%;
  max-width: 560px;
  background: #ffffff;
  border: 2px solid var(--color-border);
  border-bottom-width: 5px;
  border-radius: 22px;
  padding: 2rem;
  text-align: center;
}

.duel-badge {
  display: inline-block;
  background: var(--color-secondary-light);
  color: var(--color-secondary-dark);
  padding: 0.3rem 0.9rem;
  border-radius: 999px;
  font-weight: 800;
  font-size: 0.84rem;
  margin-bottom: 0.75rem;
}

.duel-title {
  margin: 0 0 1.75rem;
  font-size: 1.35rem;
  color: var(--color-text);
}

.versus-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 1rem;
  margin-bottom: 2rem;
}

.player-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.45rem;
  flex: 1;
}

.duel-avatar {
  width: 82px;
  height: 82px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--color-secondary);
  background: var(--color-background-off);
}

.duel-avatar.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 900;
  color: #94a3b8;
  border-style: dashed;
}

.score-tag {
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 800;
}

.score-tag.pending {
  background: var(--color-background-off);
  color: var(--color-text-light);
}

.vs-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-hero-bg);
  color: #fff;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.result-banner {
  background: var(--color-primary-light);
  border: 2px solid #99d5cc;
  border-radius: 16px;
  padding: 1.25rem;
}

.result-banner h2 { margin: 0 0 0.4rem; color: var(--color-primary-dark); }
.result-banner p { margin: 0 0 1rem; color: var(--color-text); }

.share-row { display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap; }
.start-duel-btn { padding: 0.9rem 1.8rem; font-size: 1rem; }
.self-note { color: var(--color-text-light); margin-bottom: 1rem; }
</style>
