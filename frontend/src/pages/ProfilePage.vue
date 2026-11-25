<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/dashboard" class="back-btn">
        <font-awesome-icon icon="fas fa-arrow-right" /> بازگشت به داشبورد
      </router-link>
      <h1>پروفایل کاربری</h1>
    </header>

    <div class="profile-header-card card">
      <div class="profile-avatar-section">
        <img :src="currentAvatarUrl" alt="Avatar" class="avatar-img-lg" />
        <div class="profile-names">
          <h2>{{ authStore.fullName }}</h2>
          <span class="email-text">{{ authStore.user?.username }} | {{ authStore.user?.email }}</span>
        </div>
      </div>

      <div class="stats-overview">
        <div class="stat-box">
          <span class="stat-label">سطح</span>
          <span class="stat-value">{{ toFa(authStore.user?.level || 1) }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">امتیاز کل</span>
          <span class="stat-value">{{ toFa(authStore.user?.score || 0) }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">آزمون‌ها</span>
          <span class="stat-value">{{ toFa(authStore.user?.quizzes_completed || 0) }}</span>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <div class="info-column">
        <div class="info-card card league-card">
          <h3>وضعیت لیگ</h3>
          <div class="league-details">
            <font-awesome-icon
              :icon="authStore.userLeague?.icon || 'fas fa-medal'"
              class="league-icon-big"
              :style="{ color: authStore.userLeague?.color || '#cd7f32' }"
            />
            <div class="league-text">
              <span class="league-name" :style="{ color: authStore.userLeague?.color }">
                لیگ {{ authStore.userLeague?.name }}
              </span>
              <div class="rank-display">
                <span class="label">رتبه شما:</span>
                <span class="value" v-if="userRank">#{{ toFa(userRank) }}</span>
                <span class="value" v-else>...</span>
              </div>
            </div>
          </div>
        </div>

        <div class="info-card card badges-card">
          <h3>نشان‌های افتخار</h3>
          <div v-if="earnedBadgesList.length > 0" class="badges-grid-profile">
            <div
              v-for="badge in earnedBadgesList"
              :key="badge.id"
              class="badge-item"
              :title="badge.name + ': ' + badge.description"
            >
              <div class="badge-icon-wrapper">
                <font-awesome-icon :icon="['fas', badge.icon.split(' ')[1]]" />
              </div>
              <span class="badge-name">{{ badge.name }}</span>
            </div>
          </div>
          <div v-else class="empty-badges">
            <p>هنوز نشانی کسب نکرده‌اید.</p>
            <router-link to="/dashboard" class="btn-text">شروع یادگیری</router-link>
          </div>
        </div>

        <!-- کارت تغییر رمز عبور -->
        <div class="info-card card password-card">
          <h3>تغییر رمز عبور</h3>
          <form @submit.prevent="handleChangePassword" class="password-form">
            <div class="pw-field">
              <label for="current-pw">رمز عبور فعلی</label>
              <input
                id="current-pw"
                v-model="pwForm.currentPassword"
                type="password"
                placeholder="رمز عبور فعلی خود را وارد کنید"
                dir="ltr"
                required
              />
            </div>
            <div class="pw-field">
              <label for="new-pw">رمز عبور جدید</label>
              <input
                id="new-pw"
                v-model="pwForm.newPassword"
                type="password"
                placeholder="حداقل ۶ کاراکتر"
                minlength="6"
                dir="ltr"
                required
              />
            </div>
            <div class="pw-field">
              <label for="confirm-pw">تکرار رمز عبور جدید</label>
              <input
                id="confirm-pw"
                v-model="pwForm.confirmPassword"
                type="password"
                placeholder="تکرار رمز عبور جدید"
                minlength="6"
                dir="ltr"
                required
              />
            </div>
            <p v-if="pwError" class="pw-error">{{ pwError }}</p>
            <button type="submit" class="btn btn-primary btn-block" :disabled="changingPassword">
              {{ changingPassword ? 'در حال ثبت...' : 'تغییر رمز عبور' }}
            </button>
          </form>
        </div>
      </div>

      <div class="avatar-selection-column">
        <div class="card selection-card">
          <h3>تغییر کاراکتر</h3>
          <p class="text-muted">دانشمند مورد علاقه خود را انتخاب کنید:</p>

          <div class="avatars-grid">
            <div
              v-for="avatar in avatars"
              :key="avatar.id"
              class="avatar-item"
              :class="{ selected: selectedAvatar === avatar.id }"
              @click="selectAvatar(avatar.id)"
            >
              <img :src="avatar.image" :alt="avatar.name" class="avatar-img-sm" />
              <div class="avatar-meta">
                <h4>{{ avatar.name }}</h4>
                <p>{{ avatar.role }}</p>
              </div>
              <div v-if="selectedAvatar === avatar.id" class="check-icon">
                <font-awesome-icon icon="fas fa-check-circle" />
              </div>
            </div>
          </div>

          <div class="actions">
            <button
              @click="saveAvatar"
              class="btn btn-primary btn-block"
              :disabled="isSaving || selectedAvatar === authStore.user?.avatar_id"
            >
              <span v-if="isSaving">در حال ذخیره...</span>
              <span v-else>ذخیره تغییرات</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notificationStore';
import api from '../services/api';
import badgeService from '../services/badgeService';
import leaderboardService from '../services/leaderboardService';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowRight, faCheckCircle, faMedal, faTrophy, faGem } from '@fortawesome/free-solid-svg-icons';

library.add(faArrowRight, faCheckCircle, faMedal, faTrophy, faGem);

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const selectedAvatar = ref('');
const isSaving = ref(false);
const earnedBadgesList = ref([]);
const userRank = ref(null);

const changingPassword = ref(false);
const pwError = ref('');
const pwForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
});

const toFa = (val) => {
  if (val === null || val === undefined) return '';
  return String(val).replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[Number(d)]);
};

const avatars = [
  { id: 'fleming', name: 'الکساندر فلمینگ', role: 'کاشف پنی‌سیلین', image: '/avatars/avatar_fleming.png' },
  { id: 'waksman', name: 'سلمان واکسمن', role: 'کاشف استرپتومایسین', image: '/avatars/avatar_waksman.png' },
  { id: 'domagk', name: 'گرهارد دماک', role: 'کاشف سولفونامید', image: '/avatars/avatar_domagk.png' },
  { id: 'florey', name: 'هاوارد فلوری', role: 'توسعه تولید پنی‌سیلین', image: '/avatars/avatar_florey.png' },
  { id: 'hodgkin', name: 'دوروتی هاجکین', role: 'تعیین ساختار پنی‌سیلین', image: '/avatars/avatar_hodgkin.png' },
  { id: 'bugie', name: 'الیزابت بوگی', role: 'همکار در کشف استرپتومایسین', image: '/avatars/avatar_bugie.png' },
  { id: 'youyou', name: 'تو یویو', role: 'کاشف آرتمیسینین (ضد مالاریا)', image: '/avatars/avatar_youyou.png' },
];

const currentAvatarUrl = computed(() => {
  const id = authStore.user?.avatar_id || 'fleming';
  const found = avatars.find((a) => a.id === id);
  return found ? found.image : '/avatars/avatar_fleming.png';
});

onMounted(async () => {
  if (authStore.user) {
    selectedAvatar.value = authStore.user.avatar_id || 'fleming';
  }

  await authStore.fetchUser();

  try {
    const response = await badgeService.getEarnedBadges();
    earnedBadgesList.value = response.data;
  } catch (error) {
    console.error('Error fetching badges:', error);
  }

  try {
    const currentLeagueId =
      authStore.userLeague?.name === 'الماس'
        ? 'diamond'
        : authStore.userLeague?.name === 'طلا'
          ? 'gold'
          : authStore.userLeague?.name === 'نقره'
            ? 'silver'
            : 'bronze';

    const lbResponse = await leaderboardService.getLeaderboard(currentLeagueId);
    const leaderboard = lbResponse.data;
    const myIndex = leaderboard.findIndex((u) => u.username === authStore.username);
    userRank.value = myIndex !== -1 ? myIndex + 1 : '20+';
  } catch (err) {
    console.error('Failed to fetch rank:', err);
  }
});

const selectAvatar = (id) => {
  selectedAvatar.value = id;
};

const saveAvatar = async () => {
  if (!selectedAvatar.value) return;
  isSaving.value = true;
  try {
    await api.post('/auth/update-avatar', { avatar_id: selectedAvatar.value });
    if (authStore.user) {
      authStore.user.avatar_id = selectedAvatar.value;
    }
    localStorage.setItem('user', JSON.stringify(authStore.user));
    const chosen = avatars.find((a) => a.id === selectedAvatar.value);
    notificationStore.showNotification({
      title: '✅ آواتار ذخیره شد',
      message: `کاراکتر شما با موفقیت به «${chosen?.name || selectedAvatar.value}» تغییر یافت.`,
      imageSrc: chosen?.image || null,
    });
  } catch (error) {
    console.error('Error updating avatar:', error);
    notificationStore.showNotification({
      title: '❌ خطا در ذخیره',
      message: 'ذخیره آواتار ناموفق بود. لطفاً دوباره تلاش کنید.',
    });
  } finally {
    isSaving.value = false;
  }
};

const handleChangePassword = async () => {
  pwError.value = '';
  if (pwForm.newPassword.length < 6) {
    pwError.value = 'رمز عبور جدید باید حداقل ۶ کاراکتر باشد.';
    return;
  }
  if (pwForm.newPassword !== pwForm.confirmPassword) {
    pwError.value = 'رمز عبور جدید و تکرار آن یکسان نیستند.';
    return;
  }

  changingPassword.value = true;
  try {
    const res = await api.post('/auth/change-password', {
      current_password: pwForm.currentPassword,
      new_password: pwForm.newPassword,
    });
    pwForm.currentPassword = '';
    pwForm.newPassword = '';
    pwForm.confirmPassword = '';
    notificationStore.showNotification({
      title: '🔒 رمز عبور تغییر یافت',
      message: res.data?.message || 'رمز عبور شما با موفقیت بروزرسانی شد.',
    });
  } catch (err) {
    pwError.value = err.response?.data?.message || 'خطا در تغییر رمز عبور.';
  } finally {
    changingPassword.value = false;
  }
};
</script>

<style scoped>
.page-container { padding: 1.5rem 1rem; max-width: 1000px; margin: 0 auto; min-height: 100vh; padding-bottom: 95px; box-sizing: border-box; }
.page-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
.back-btn { color: var(--color-text-light); text-decoration: none; font-weight: bold; }
h1 { margin: 0; font-size: 1.5rem; color: var(--color-text); }

.card { background: white; border: 2px solid #e5e5e5; border-radius: 16px; padding: 1.35rem; box-sizing: border-box; }

.profile-header-card { display: flex; flex-direction: column; gap: 1.5rem; margin-bottom: 1.5rem; background: linear-gradient(135deg, white, #f0f7ff); border-color: var(--color-primary-light); }
.profile-avatar-section { display: flex; align-items: center; gap: 1.25rem; }
.avatar-img-lg { width: 92px; height: 92px; border-radius: 50%; border: 4px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); background-color: #eee; object-fit: cover; }
.profile-names h2 { margin: 0; font-size: 1.55rem; color: var(--color-primary); }
.email-text { color: var(--color-text-light); font-size: 0.92rem; word-break: break-all; }

.stats-overview { display: flex; gap: 2.5rem; padding-top: 1rem; border-top: 2px solid rgba(0,0,0,0.05); }
.stat-box { display: flex; flex-direction: column; gap: 0.25rem; }
.stat-label { font-size: 0.85rem; color: var(--color-text-light); font-weight: bold; }
.stat-value { font-size: 1.35rem; font-weight: 800; color: var(--color-text); }

.content-grid { display: grid; grid-template-columns: 1fr 1.45fr; gap: 1.5rem; }
.info-column { display: flex; flex-direction: column; gap: 1.5rem; }
.info-card h3 { margin: 0 0 1rem; font-size: 1.05rem; color: var(--color-text-light); }

.league-details { display: flex; align-items: center; gap: 1rem; }
.league-icon-big { font-size: 3.2rem; }
.league-text { display: flex; flex-direction: column; }
.league-name { font-size: 1.3rem; font-weight: 900; }
.rank-display { margin-top: 0.2rem; font-size: 0.95rem; color: var(--color-text); }
.rank-display .value { font-weight: bold; margin-right: 0.3rem; font-size: 1.15rem; }

.badges-grid-profile { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 1rem; }
.badge-item { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 0.5rem; }
.badge-icon-wrapper { width: 58px; height: 58px; background-color: #fff9c4; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.7rem; color: #fbc02d; border: 2px solid #fbc02d; }
.badge-name { font-size: 0.8rem; color: var(--color-text); font-weight: bold; }
.empty-badges { text-align: center; padding: 1rem; color: var(--color-text-light); }

/* Change Password Card */
.password-form { display: flex; flex-direction: column; gap: 0.85rem; }
.pw-field { display: flex; flex-direction: column; gap: 0.35rem; }
.pw-field label { font-size: 0.86rem; font-weight: 700; color: var(--color-text); }
.pw-field input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 0.95rem;
  box-sizing: border-box;
  background: #fafafa;
}
.pw-field input:focus {
  outline: none;
  border-color: var(--color-secondary);
  background: #fff;
}
.pw-error {
  margin: 0;
  color: #c62828;
  font-size: 0.84rem;
  font-weight: 700;
}

/* Avatar Selection */
.selection-card h3 { margin-top: 0; }
.avatars-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(135px, 1fr)); gap: 0.9rem; margin-top: 1.25rem; max-height: 520px; overflow-y: auto; padding-right: 0.25rem; }

.avatar-item { cursor: pointer; border: 2px solid transparent; border-radius: 12px; padding: 0.9rem; text-align: center; position: relative; transition: all 0.2s; background: #f9f9f9; }
.avatar-item:hover { background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transform: translateY(-2px); }
.avatar-item.selected { border-color: var(--color-primary); background-color: var(--color-primary-light); }

.avatar-img-sm { width: 68px; height: 68px; border-radius: 50%; object-fit: cover; margin-bottom: 0.45rem; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.avatar-meta h4 { font-size: 0.88rem; margin: 0.4rem 0 0.2rem; color: var(--color-text); }
.avatar-meta p { font-size: 0.74rem; color: var(--color-text-light); margin: 0; line-height: 1.25; }

.check-icon { position: absolute; top: 8px; right: 8px; color: var(--color-primary); font-size: 1.15rem; background: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; }

.actions { margin-top: 1.5rem; }
.btn-block { width: 100%; padding: 0.8rem; font-size: 0.98rem; }

@media (max-width: 850px) {
  .content-grid { grid-template-columns: 1fr; }
  .profile-header-card { flex-direction: column; align-items: center; text-align: center; }
  .profile-avatar-section { flex-direction: column; text-align: center; }
  .stats-overview { justify-content: center; width: 100%; }
}
</style>
