<template>
  <div class="dashboard-layout">
    <header class="dashboard-topbar">
      <div class="topbar-content">
        <div class="right-section">
          <router-link to="/" class="dashboard-logo-link" title="صفحه اصلی سایت">
            <div class="logo-container">
              <font-awesome-icon icon="fas fa-microscope" class="logo-icon" />
              <h2 class="logo-text">AntibioticPlay</h2>
            </div>
          </router-link>
        </div>

        <div class="stats-bar">
          <div class="stat-item" :title="'لیگ: ' + (user?.league?.name || 'برنز')">
            <font-awesome-icon
              :icon="user?.league?.icon || 'fas fa-medal'"
              class="flag-icon"
              :style="{ color: user?.league?.color || '#b45309' }"
            />
            <span class="desktop-only">{{ user?.league?.name || 'برنز' }}</span>
          </div>

          <div class="stat-item" title="پاسخ صحیح متوالی">
            <font-awesome-icon
              icon="fas fa-fire"
              class="icon-fire"
              :class="{ 'animate-fire': (user?.correct_streak || 0) > 0 }"
            />
            <span>{{ toFa(user?.correct_streak || 0) }}</span>
          </div>

          <div class="stat-item" title="امتیاز کل">
            <font-awesome-icon icon="fas fa-star" class="icon-gem" />
            <span :class="{ 'score-pop-animation': scoreJustUpdated }">
              {{ toFa(score || 0) }}
            </span>
          </div>
        </div>

        <div class="left-section">
          <router-link
            v-if="user?.role === 'admin'"
            to="/admin"
            class="btn-ghost header-btn admin-btn"
            title="پنل مدیریت"
          >
            <font-awesome-icon icon="fas fa-sliders" />
            <span class="btn-label">مدیریت</span>
          </router-link>

          <router-link
            v-if="surveyStatus && !surveyStatus.submitted"
            to="/survey"
            class="btn-ghost header-btn"
            title="پرسشنامه ارزشیابی"
          >
            <font-awesome-icon icon="fas fa-clipboard-list" />
            <span class="btn-label">پرسشنامه</span>
          </router-link>

          <router-link to="/rules" class="btn-ghost header-btn" title="راهنما">
            <font-awesome-icon icon="fas fa-question-circle" />
            <span class="btn-label">راهنما</span>
          </router-link>

          <button @click="handleLogout" class="btn-ghost header-btn logout-btn" title="خروج از حساب">
            <font-awesome-icon icon="fas fa-sign-out-alt" />
            <span class="btn-label">خروج</span>
          </button>
        </div>
      </div>
    </header>

    <main class="dashboard-main">
      <div class="learning-path-column">
        <!-- بنر دعوت به پرسشنامه داخلی MEEGA+ -->
        <div
          v-if="surveyStatus && !surveyStatus.submitted && surveyStatus.eligible"
          class="survey-invite-banner"
        >
          <div class="survey-invite-text">
            <strong>نظرتان درباره AntibioticPlay چیست؟</strong>
            <p>با تکمیل پرسشنامه ارزشیابی، <strong>+۵۰ XP</strong> دریافت کنید.</p>
          </div>
          <router-link to="/survey" class="btn btn-primary survey-cta">
            تکمیل پرسشنامه
          </router-link>
        </div>

        <div v-if="quizStore.loading && !quizStore.modules.length" class="loading-state">
          در حال بارگذاری مسیر یادگیری...
        </div>

        <div v-else class="units-list">
          <div
            v-for="(unit, uIndex) in quizStore.modules"
            :key="unit.id"
            class="unit-card"
            :style="{ borderColor: getModuleColor(uIndex) }"
          >
            <header
              class="unit-header"
              :style="{ backgroundColor: getModuleColor(uIndex) }"
            >
              <h3>بخش {{ toFa(uIndex + 1) }}: {{ unit.title }}</h3>
              <p>{{ unit.description }}</p>
            </header>

            <div class="unit-body levels-path">
              <div
                v-for="level in unit.levels"
                :key="level.id"
                class="level-node-wrapper"
                :class="{
                  completed: level.is_completed,
                  locked: level.is_locked,
                }"
              >
                <button
                  class="level-button"
                  :style="getLevelButtonStyle(level, getModuleColor(uIndex))"
                  @click="startQuiz(level, getModuleColor(uIndex))"
                  :disabled="level.is_locked"
                >
                  <font-awesome-icon v-if="level.is_completed" icon="fas fa-check" class="check-icon" />
                  <font-awesome-icon v-else-if="level.is_locked" icon="fas fa-lock" class="lock-icon" />
                  <font-awesome-icon v-else :icon="['fas', cleanIconName(level.icon)]" class="level-icon" />
                </button>
                <span class="level-title">{{ level.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <aside class="sidebar-column">
        <!-- پروفایل کاربر -->
        <div class="sidebar-widget user-widget">
          <div class="user-avatar-img-container">
            <img :src="userAvatar" alt="Avatar" class="sidebar-avatar" />
          </div>
          <div class="user-info">
            <h3>{{ authStore.fullName }}</h3>
            <p class="user-email">{{ user?.email }}</p>
            <router-link to="/profile" class="profile-link-btn">
              <font-awesome-icon icon="fas fa-user-pen" />
              ویرایش پروفایل
            </router-link>
          </div>
        </div>

        <!-- ابزارهای تمرین و مرور هوشمند -->
        <div class="sidebar-widget tools-widget">
          <div class="widget-header">
            <h3>تمرین و مرور هوشمند</h3>
          </div>
          <div class="tools-stack">
            <router-link to="/flashcards" class="tool-btn tool-flashcards">
              <font-awesome-icon icon="fas fa-layer-group" />
              <span>فلش‌کارت‌های هوشمند (لایتنر)</span>
            </router-link>
            <router-link to="/daily-challenge" class="tool-btn tool-daily">
              <font-awesome-icon icon="fas fa-bolt" />
              <span>چالش روزانه (+۵۰ XP)</span>
            </router-link>
            <router-link to="/review" class="tool-btn tool-review">
              <font-awesome-icon icon="fas fa-bookmark" />
              <span>سوالات نشان‌دار</span>
            </router-link>
          </div>
        </div>

        <!-- لیگ -->
        <div class="sidebar-widget leaderboard-widget">
          <div class="widget-header">
            <h3>لیگ {{ user?.league?.name || 'برنز' }}</h3>
            <router-link to="/leaderboard" class="link-text">مشاهده لیگ</router-link>
          </div>

          <div v-if="userRank" class="league-status">
            <div class="league-icon-large" :style="{ color: user?.league?.color || '#b45309' }">
              <font-awesome-icon :icon="user?.league?.icon || 'fas fa-medal'" />
            </div>
            <div class="rank-info">
              <span class="rank-label">رتبه شما</span>
              <span class="rank-value">#{{ toFa(userRank) }}</span>
            </div>
            <div class="xp-info">{{ toFa(score) }} XP</div>
          </div>
          <div v-else class="league-placeholder">
            <font-awesome-icon icon="fas fa-trophy" class="league-icon-gray" />
            <p>در حال محاسبه رتبه...</p>
          </div>
        </div>

        <!-- نشان‌ها -->
        <div class="sidebar-widget badges-widget">
          <div class="widget-header">
            <h3>نشان‌های شما</h3>
          </div>
          <div v-if="earnedBadges.length > 0" class="badges-mini-grid">
            <div
              v-for="badge in earnedBadges.slice(0, 4)"
              :key="badge.id"
              class="mini-badge"
              :title="badge.name"
            >
              <font-awesome-icon :icon="badge.icon.split(' ')" />
            </div>
            <div v-if="earnedBadges.length > 4" class="more-badges">
              +{{ toFa(earnedBadges.length - 4) }}
            </div>
          </div>
          <div v-else class="empty-state">هنوز نشانی کسب نکرده‌اید.</div>
        </div>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useQuizStore } from '../stores/quiz';
import badgeService from '../services/badgeService';
import leaderboardService from '../services/leaderboardService';
import surveyService from '../services/surveyService';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faQuestionCircle,
  faUserPen,
  faLock,
  faMicroscope,
  faClipboardList,
  faSignOutAlt,
  faLayerGroup,
  faBolt,
  faBookmark,
  faShieldVirus,
  faFlask,
  faUserDoctor,
  faSliders,
} from '@fortawesome/free-solid-svg-icons';

library.add(
  faQuestionCircle,
  faUserPen,
  faLock,
  faMicroscope,
  faClipboardList,
  faSignOutAlt,
  faLayerGroup,
  faBolt,
  faBookmark,
  faShieldVirus,
  faFlask,
  faUserDoctor,
  faSliders
);

const authStore = useAuthStore();
const quizStore = useQuizStore();
const router = useRouter();

const { user, score } = storeToRefs(authStore);

const earnedBadges = ref([]);
const scoreJustUpdated = ref(false);
const userRank = ref(null);
const surveyStatus = ref(null);

const toFa = (val) => {
  if (val === null || val === undefined) return '';
  return String(val).replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[Number(d)]);
};

// Cohesive Clinical Palette (Teal, Medical Navy, Clinical Amber, Surgical Slate)
const moduleColors = ['#0f766e', '#1d5c8c', '#b45309', '#2b6cb0', '#9b2c2c'];
const getModuleColor = (index) => moduleColors[index % moduleColors.length];

const cleanIconName = (iconName) => {
  if (!iconName) return 'star';
  return iconName.replace(/^fa-/, '');
};

const userAvatar = computed(() => {
  const avatarId = authStore.user?.avatar_id || 'fleming';
  return `/avatars/avatar_${avatarId}.png`;
});

const adjustColor = (color, amount) => {
  return (
    '#' +
    color
      .replace(/^#/, '')
      .replace(/../g, (c) =>
        ('0' + Math.min(255, Math.max(0, parseInt(c, 16) + amount)).toString(16)).substr(-2)
      )
  );
};

const getLevelButtonStyle = (level, unitColor) => {
  if (level.is_locked) {
    return {
      backgroundColor: '#e2e8f0',
      boxShadow: 'none',
      cursor: 'not-allowed',
      color: '#94a3b8',
    };
  }
  if (level.is_completed) {
    return {
      backgroundColor: '#d97706',
      boxShadow: '0 6px 0 #a35504',
      color: 'white',
    };
  }
  return {
    backgroundColor: unitColor,
    boxShadow: `0 6px 0 ${adjustColor(unitColor, -38)}`,
    color: 'white',
  };
};

onMounted(async () => {
  if (authStore.triggerScoreAnimation === true) {
    scoreJustUpdated.value = true;
    authStore.resetScoreAnimationTrigger();
    setTimeout(() => {
      scoreJustUpdated.value = false;
    }, 600);
  }

  await authStore.fetchUser();
  quizStore.fetchModules();

  try {
    const response = await badgeService.getEarnedBadges();
    earnedBadges.value = response.data;
  } catch (error) {
    console.error('Failed to fetch earned badges:', error);
  }

  try {
    const sRes = await surveyService.getStatus();
    surveyStatus.value = sRes.data;
  } catch (err) {
    console.error('Failed to fetch survey status:', err);
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
    const myIndex = leaderboard.findIndex((u) => u.username === user.value?.username);
    userRank.value = myIndex !== -1 ? myIndex + 1 : '20+';
  } catch (err) {
    console.error('Failed to fetch rank:', err);
  }
});

const handleLogout = () => {
  authStore.logout();
};

const startQuiz = (level, unitColor) => {
  if (!level || level.is_locked) return;
  router.push({
    name: 'Quiz',
    params: { id: level.id },
    query: { theme: unitColor },
  });
};
</script>

<style scoped>
.dashboard-layout { min-height: 100vh; background-color: var(--color-background-page); display: flex; flex-direction: column; }

.dashboard-topbar { background-color: #ffffff; border-bottom: 2px solid var(--color-border); position: sticky; top: 0; z-index: 100; padding: 0.75rem 2rem; }
.topbar-content { max-width: 1050px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; }

.dashboard-logo-link { text-decoration: none; display: inline-flex; align-items: center; }
.logo-container { display: flex; align-items: center; gap: 0.5rem; }
.logo-icon {
  font-size: 1.25rem;
  color: #ffffff;
  background-color: var(--color-primary);
  padding: 0.42rem;
  border-radius: 10px;
}
.logo-text {
  color: var(--color-text);
  font-weight: 900;
  font-size: 1.25rem;
  margin: 0;
  letter-spacing: -0.02em;
}

.left-section { display: flex; gap: 0.35rem; align-items: center; }
.header-btn {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.45rem 0.65rem; border-radius: 12px;
  color: var(--color-text-light); font-weight: 700;
  text-decoration: none; background: transparent; border: none;
  cursor: pointer; min-width: auto !important;
}
.header-btn:hover { background-color: var(--color-background-off); color: var(--color-text); }
.admin-btn { color: var(--color-secondary); }
.btn-label { font-size: 0.86rem; }
.logout-btn { color: var(--color-danger); }
.logout-btn:hover { background-color: var(--color-danger-light); color: var(--color-danger-dark); }

.stats-bar { display: flex; gap: 1.2rem; align-items: center; }
.stat-item { display: flex; align-items: center; gap: 0.35rem; font-weight: 800; color: var(--color-text-light); cursor: default; }
.icon-fire { color: var(--color-warning); font-size: 1.15rem; }
.icon-gem { color: var(--color-secondary); font-size: 1.15rem; }
.flag-icon { font-size: 1.15rem; }

.dashboard-main { flex: 1; max-width: 1050px; width: 100%; margin: 0 auto; padding: 1.75rem 1rem; display: flex; gap: 2.25rem; box-sizing: border-box; }
.learning-path-column { flex: 1; }

/* Survey Invite Banner - Crisp Clinical Card */
.survey-invite-banner {
  background-color: var(--color-primary-light);
  border: 2px solid #99d5cc;
  border-bottom-width: 4px;
  border-radius: 18px;
  padding: 1.1rem 1.3rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}
.survey-invite-text strong { display: block; color: var(--color-primary-dark); font-size: 0.98rem; margin-bottom: 0.2rem; }
.survey-invite-text p { margin: 0; font-size: 0.86rem; color: var(--color-text); }
.survey-cta { padding: 0.6rem 1.15rem; font-size: 0.88rem; white-space: nowrap; }

/* Unit Cards & Path */
.unit-card { border: 2px solid; border-bottom-width: 4px; border-radius: 20px; overflow: hidden; margin-bottom: 1.75rem; text-align: right; background: #ffffff; }
.unit-header { padding: 1.25rem 1.5rem; color: #ffffff; }
.unit-header h3 { margin: 0 0 0.3rem; font-size: 1.22rem; color: #ffffff; }
.unit-header p { margin: 0; opacity: 0.92; font-size: 0.9rem; }

.levels-path {
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.65rem;
  background-color: #ffffff;
}

.level-node-wrapper { display: flex; flex-direction: column; align-items: center; gap: 0.55rem; }
.level-node-wrapper:nth-child(odd) { transform: translateX(-28px); }
.level-node-wrapper:nth-child(even) { transform: translateX(28px); }

.level-button {
  width: 78px; height: 78px; border-radius: 50%; border: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: transform 0.1s; font-size: 1.85rem;
  min-width: 0 !important;
}
.level-button:active:not(:disabled) { transform: translateY(4px); }
.level-title { font-weight: 800; font-size: 0.9rem; color: var(--color-text); }

.level-node-wrapper.locked .level-button {
  background-color: #e2e8f0 !important;
  box-shadow: 0 4px 0 #cbd5e1 !important;
  transform: none !important;
}
.level-node-wrapper.locked .level-title { color: #94a3b8; }
.lock-icon { font-size: 1.35rem; opacity: 0.7; }

/* Sidebar */
.sidebar-column { width: 340px; display: flex; flex-direction: column; gap: 1.2rem; }
.sidebar-widget { border: 2px solid var(--color-border); border-bottom-width: 4px; border-radius: 18px; padding: 1.25rem; background-color: #ffffff; }

.user-widget { display: flex; align-items: center; gap: 1rem; }
.user-avatar-img-container {
  width: 66px; height: 66px; border-radius: 50%; overflow: hidden;
  border: 3px solid var(--color-primary); background-color: white; flex-shrink: 0;
}
.sidebar-avatar { width: 100%; height: 100%; object-fit: cover; }
.user-info h3 { margin: 0; font-size: 1.08rem; }
.user-email { margin: 0.15rem 0 0.45rem; color: var(--color-text-light); font-size: 0.84rem; }
.profile-link-btn {
  font-size: 0.84rem; color: var(--color-secondary); text-decoration: none;
  font-weight: 800; display: inline-flex; align-items: center; gap: 0.35rem;
}

/* Tools Widget - Tactile Clinical Buttons */
.tools-stack { display: flex; flex-direction: column; gap: 0.65rem; }
.tool-btn {
  display: flex; align-items: center; gap: 0.65rem;
  padding: 0.75rem 1rem; border-radius: 14px;
  text-decoration: none; font-weight: 800; font-size: 0.88rem;
  border: 2px solid transparent; border-bottom-width: 4px;
  transition: transform 0.08s ease;
}
.tool-btn:active { transform: translateY(2px); border-bottom-width: 2px; }
.tool-flashcards { background: var(--color-primary-light); color: var(--color-primary-dark); border-color: #99d5cc; border-bottom-color: #5eb8ac; }
.tool-daily { background: var(--color-warning-light); color: var(--color-warning-dark); border-color: #f6d38b; border-bottom-color: #e2aa42; }
.tool-review { background: var(--color-secondary-light); color: var(--color-secondary-dark); border-color: #b2cde3; border-bottom-color: #7ea8cc; }

.widget-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.9rem; }
.widget-header h3 { margin: 0; color: var(--color-text); font-size: 1rem; }
.link-text { color: var(--color-secondary); text-decoration: none; font-weight: 800; font-size: 0.86rem; }

.league-status { display: flex; align-items: center; gap: 1rem; }
.league-icon-large { font-size: 2.6rem; }
.rank-info { flex: 1; display: flex; flex-direction: column; }
.rank-label { font-size: 0.78rem; color: var(--color-text-light); font-weight: 700; }
.rank-value { font-size: 1.6rem; font-weight: 900; color: var(--color-text); }
.xp-info { font-weight: 800; color: var(--color-text); background: var(--color-background-off); padding: 0.25rem 0.65rem; border-radius: 8px; font-size: 0.86rem; }
.league-placeholder { text-align: center; color: var(--color-text-light); }
.league-icon-gray { font-size: 2.4rem; color: var(--color-border-strong); margin-bottom: 0.4rem; }

.badges-mini-grid { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.mini-badge { width: 46px; height: 46px; background-color: var(--color-warning-light); border: 2px solid #f6d38b; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: var(--color-warning-dark); font-size: 1.3rem; }
.more-badges { width: 46px; height: 46px; background-color: var(--color-background-off); border-radius: 50%; display: flex; justify-content: center; align-items: center; font-weight: 800; color: var(--color-text-light); }
.empty-state { color: var(--color-text-light); font-size: 0.86rem; }

@media (max-width: 850px) {
  .dashboard-main { flex-direction: column-reverse; padding-bottom: 100px; }
  .sidebar-column { width: 100%; }
  .desktop-only, .btn-label { display: none; }
  .dashboard-topbar { padding: 0.65rem 0.85rem; }
  .logo-text { font-size: 1rem; }
  .logo-icon { font-size: 1.1rem; }
  .stats-bar { gap: 0.75rem; font-size: 0.9rem; }
  .header-btn { padding: 0.35rem 0.45rem; }
}

@media (max-width: 420px) {
  .logo-text { display: none; }
}
</style>
