<template>
  <div class="flashcards-page">
    <header class="fc-header">
      <div class="fc-header-inner">
        <router-link to="/dashboard" class="back-btn" title="بازگشت به داشبورد">
          <font-awesome-icon icon="fas fa-arrow-right" />
        </router-link>
        <div class="header-titles">
          <h1>فلش‌کارت‌های هوشمند آنتی‌میکروبیال</h1>
          <p>مرور مبتنی بر الگوریتم تکرار با فاصله (لایتنر / SM-2)</p>
        </div>
      </div>
    </header>

    <main class="fc-container">
      <!-- نوار آمار روزانه -->
      <section class="stats-strip" v-if="stats">
        <div class="stat-pill due">
          <span class="pill-value">{{ stats.due_today }}</span>
          <span class="pill-label">در صف امروز</span>
        </div>
        <div class="stat-pill reviewed">
          <span class="pill-value">{{ stats.reviewed_today }}</span>
          <span class="pill-label">مرور امروز</span>
        </div>
        <div class="stat-pill mastered">
          <span class="pill-value">{{ stats.mastered }}</span>
          <span class="pill-label">تسلط کامل</span>
        </div>
        <div class="stat-pill total">
          <span class="pill-value">{{ stats.total_cards }}</span>
          <span class="pill-label">کل کارت‌ها</span>
        </div>
      </section>

      <!-- تب‌های حالت مطالعه -->
      <section class="mode-tabs">
        <button
          class="mode-btn"
          :class="{ active: mode === 'due' }"
          @click="changeMode('due')"
        >
          مرور امروز
          <span v-if="stats" class="count-chip">{{ stats.due_today }}</span>
        </button>
        <button
          class="mode-btn"
          :class="{ active: mode === 'all' }"
          @click="changeMode('all')"
        >
          همه کارت‌ها
        </button>
        <button
          class="mode-btn"
          :class="{ active: mode === 'bookmarked' }"
          @click="changeMode('bookmarked')"
        >
          نشان‌شده‌ها
          <span v-if="stats" class="count-chip">{{ stats.bookmarked }}</span>
        </button>
      </section>

      <!-- فیلتر خانواده دارویی -->
      <section class="categories-scroller" v-if="categories.length">
        <button
          class="cat-chip"
          :class="{ active: selectedCategory === 'all' }"
          @click="selectCategory('all')"
        >
          همه دسته‌ها
        </button>
        <button
          v-for="cat in categories"
          :key="cat.name"
          class="cat-chip"
          :class="{ active: selectedCategory === cat.name }"
          @click="selectCategory(cat.name)"
        >
          <span>{{ cat.name }}</span>
          <span class="cat-badge" v-if="mode === 'due' && cat.due > 0">{{ cat.due }}</span>
          <span class="cat-badge neutral" v-else>{{ cat.total }}</span>
        </button>
      </section>

      <!-- وضعیت بارگذاری -->
      <div v-if="loading" class="state-box">
        <p>در حال آماده‌سازی فلش‌کارت‌ها...</p>
      </div>

      <!-- وضعیت اتمام مرور یا نبود کارت -->
      <div v-else-if="cards.length === 0 || currentIndex >= cards.length" class="state-box done-box">
        <div class="done-emoji">🎉</div>
        <h2 v-if="mode === 'due'">آفرین! تمام کارت‌های امروز مرور شدند</h2>
        <h2 v-else-if="mode === 'bookmarked'">هنوز کارتی نشان نشده است</h2>
        <h2 v-else>کارتی در این دسته یافت نشد</h2>
        <p v-if="sessionReviewed > 0">
          در این جلسه <strong>{{ sessionReviewed }}</strong> کارت مرور کردید و
          <strong>+{{ sessionXp }} XP</strong> دریافت کردید.
        </p>
        <div class="done-actions">
          <button v-if="mode === 'due'" class="btn btn-primary" @click="changeMode('all')">
            مرور آزاد همه کارت‌ها
          </button>
          <router-link to="/dashboard" class="btn btn-outline">
            بازگشت به داشبورد
          </router-link>
        </div>
      </div>

      <!-- ناحیه اصلی کارت سه‌بعدی -->
      <section v-else class="study-area">
        <div class="study-meta">
          <span class="card-counter">
            کارت {{ currentIndex + 1 }} از {{ cards.length }}
          </span>
          <span class="box-indicator" :class="'box-' + (currentCard.box || 0)">
            {{ boxLabel(currentCard.box) }}
          </span>
          <button
            class="bookmark-icon-btn"
            :class="{ bookmarked: currentCard.is_bookmarked }"
            @click.stop="toggleBookmark"
            title="نشان‌گذاری کارت"
          >
            <font-awesome-icon
              :icon="currentCard.is_bookmarked ? 'fas fa-bookmark' : 'far fa-bookmark'"
            />
          </button>
        </div>

        <div class="session-progress-bar">
          <div
            class="session-progress-fill"
            :style="{ width: `${((currentIndex) / cards.length) * 100}%` }"
          ></div>
        </div>

        <!-- کارت دوطرفه سه‌بعدی -->
        <div class="flip-scene" @click="flipCard">
          <div class="flip-card" :class="{ flipped: isFlipped }">
            <!-- روی کارت (سوال) -->
            <div class="card-face card-front">
              <div class="face-tags">
                <span class="tag-cat">{{ currentCard.category }}</span>
                <span v-if="currentCard.subcategory" class="tag-sub">
                  {{ currentCard.subcategory }}
                </span>
              </div>
              <div class="face-body">
                <h2 class="front-question">{{ currentCard.front }}</h2>
              </div>
              <div class="face-footer">
                <span>برای مشاهده پاسخ کلیک کنید (یا کلید Space)</span>
              </div>
            </div>

            <!-- پشت کارت (پاسخ + نکته بالینی) -->
            <div class="card-face card-back">
              <div class="face-tags">
                <span class="tag-cat">{{ currentCard.category }}</span>
                <span class="tag-answer">پاسخ علمی</span>
              </div>
              <div class="face-body back-body">
                <p class="back-answer">{{ currentCard.back }}</p>
                <div v-if="currentCard.clinical_pearl" class="pearl-box">
                  <strong>💡 نکته بالینی و بازار ایران:</strong>
                  <p>{{ currentCard.clinical_pearl }}</p>
                </div>
              </div>
              <div class="face-footer">
                <span>میزان تسلط خود را در پایین ثبت کنید</span>
              </div>
            </div>
          </div>
        </div>

        <!-- دکمه‌های امتیازدهی لایتنر / SM-2 -->
        <div class="controls-area">
          <button
            v-if="!isFlipped"
            class="btn btn-primary flip-cta"
            @click="flipCard"
          >
            نمایش پاسخ
          </button>

          <div v-else class="rating-grid">
            <button
              class="rate-btn rate-hard"
              :disabled="submitting"
              @click="rateCard('hard')"
            >
              <strong>سخت (۱)</strong>
              <span>مرور فردا • +۱ XP</span>
            </button>
            <button
              class="rate-btn rate-medium"
              :disabled="submitting"
              @click="rateCard('medium')"
            >
              <strong>متوسط (۲)</strong>
              <span>مرور چند روز بعد • +۲ XP</span>
            </button>
            <button
              class="rate-btn rate-easy"
              :disabled="submitting"
              @click="rateCard('easy')"
            >
              <strong>آسان (۳)</strong>
              <span>تسلط بالا • +۳ XP</span>
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import flashcardService from '../services/flashcardService';
import { useAuthStore } from '../stores/auth';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowRight, faBookmark as fasBookmark } from '@fortawesome/free-solid-svg-icons';
import { faBookmark as farBookmark } from '@fortawesome/free-regular-svg-icons';

library.add(faArrowRight, fasBookmark, farBookmark);

const authStore = useAuthStore();

const categories = ref([]);
const stats = ref(null);
const cards = ref([]);
const loading = ref(true);
const submitting = ref(false);

const mode = ref('due');
const selectedCategory = ref('all');
const currentIndex = ref(0);
const isFlipped = ref(false);
const sessionReviewed = ref(0);
const sessionXp = ref(0);

const currentCard = computed(() => cards.value[currentIndex.value] || null);

const boxLabel = (box) => {
  if (!box || box === 0) return 'کارت جدید';
  if (box === 1) return 'جعبه ۱ (نیازمند مرور)';
  if (box === 2) return 'جعبه ۲ (در حال یادگیری)';
  if (box === 3) return 'جعبه ۳ (آشنا)';
  if (box === 4) return 'جعبه ۴ (مسلط)';
  return 'جعبه ۵ (تثبیت‌شده)';
};

const fetchMeta = async () => {
  try {
    const [catRes, statsRes] = await Promise.all([
      flashcardService.getCategories(),
      flashcardService.getStats(),
    ]);
    categories.value = catRes.data;
    stats.value = statsRes.data;
  } catch (err) {
    console.error('Error loading flashcard metadata:', err);
  }
};

const fetchCards = async () => {
  loading.value = true;
  isFlipped.value = false;
  currentIndex.value = 0;
  try {
    const res = await flashcardService.getCards({
      category: selectedCategory.value,
      mode: mode.value,
      limit: 60,
    });
    cards.value = res.data;
  } catch (err) {
    console.error('Error loading flashcards:', err);
  } finally {
    loading.value = false;
  }
};

const changeMode = async (newMode) => {
  if (mode.value === newMode) return;
  mode.value = newMode;
  await fetchCards();
};

const selectCategory = async (catName) => {
  selectedCategory.value = catName;
  await fetchCards();
};

const flipCard = () => {
  if (!currentCard.value) return;
  isFlipped.value = !isFlipped.value;
};

const rateCard = async (rating) => {
  if (!currentCard.value || submitting.value) return;
  submitting.value = true;
  try {
    const res = await flashcardService.submitReview(currentCard.value.id, rating);
    const { xp_earned, new_total_score } = res.data;
    sessionReviewed.value += 1;
    sessionXp.value += xp_earned || 0;
    if (typeof new_total_score === 'number') {
      authStore.updateUserScore(new_total_score);
    }

    isFlipped.value = false;
    currentIndex.value += 1;
    await fetchMeta();
  } catch (err) {
    console.error('Error submitting flashcard review:', err);
  } finally {
    submitting.value = false;
  }
};

const toggleBookmark = async () => {
  if (!currentCard.value) return;
  try {
    const res = await flashcardService.toggleBookmark(currentCard.value.id);
    currentCard.value.is_bookmarked = res.data.is_bookmarked;
    await fetchMeta();
  } catch (err) {
    console.error('Error toggling flashcard bookmark:', err);
  }
};

const handleKeydown = (e) => {
  if (!currentCard.value) return;
  if (e.code === 'Space') {
    e.preventDefault();
    flipCard();
  } else if (isFlipped.value && e.key === '1') {
    rateCard('hard');
  } else if (isFlipped.value && e.key === '2') {
    rateCard('medium');
  } else if (isFlipped.value && e.key === '3') {
    rateCard('easy');
  }
};

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown);
  await Promise.all([fetchMeta(), fetchCards()]);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.flashcards-page {
  min-height: 100vh;
  background-color: #f6f8fb;
  direction: rtl;
  padding-bottom: 95px;
}

.fc-header {
  background: #ffffff;
  border-bottom: 2px solid #e5e5e5;
  padding: 1rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 20;
}

.fc-header-inner {
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
  background: #f0f2f5;
  color: #555;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  flex-shrink: 0;
}

.header-titles h1 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 800;
  color: #2c3e50;
}

.header-titles p {
  margin: 0.15rem 0 0;
  font-size: 0.85rem;
  color: #777;
}

.fc-container {
  max-width: 820px;
  margin: 1.25rem auto 0;
  padding: 0 1rem;
}

/* Stats Strip */
.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.1rem;
}

.stat-pill {
  background: #ffffff;
  border: 2px solid #e8ecf1;
  border-radius: 14px;
  padding: 0.7rem 0.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.pill-value {
  font-size: 1.35rem;
  font-weight: 900;
}

.pill-label {
  font-size: 0.78rem;
  color: #6b7785;
  font-weight: 700;
}

.stat-pill.due .pill-value { color: #ff9600; }
.stat-pill.reviewed .pill-value { color: #0288d1; }
.stat-pill.mastered .pill-value { color: #43a047; }
.stat-pill.total .pill-value { color: #5e35b1; }

/* Mode Tabs */
.mode-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.9rem;
}

.mode-btn {
  flex: 1;
  background: #ffffff;
  border: 2px solid #e5e5e5;
  border-radius: 12px;
  padding: 0.65rem 0.75rem;
  font-weight: 800;
  font-size: 0.9rem;
  color: #555;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  transition: all 0.2s;
}

.mode-btn.active {
  background: #0288d1;
  border-color: #0288d1;
  color: #ffffff;
}

.count-chip {
  background: rgba(0, 0, 0, 0.12);
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  font-size: 0.78rem;
}

/* Categories */
.categories-scroller {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  margin-bottom: 1.1rem;
  scrollbar-width: thin;
}

.cat-chip {
  white-space: nowrap;
  background: #ffffff;
  border: 2px solid #e5e5e5;
  border-radius: 999px;
  padding: 0.42rem 0.85rem;
  font-size: 0.83rem;
  font-weight: 700;
  color: #4b5563;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s;
}

.cat-chip.active {
  border-color: #009688;
  background: #e0f2f1;
  color: #00695c;
}

.cat-badge {
  background: #ff9600;
  color: #fff;
  border-radius: 999px;
  padding: 0.05rem 0.45rem;
  font-size: 0.72rem;
}

.cat-badge.neutral {
  background: #e5e7eb;
  color: #4b5563;
}

/* Study Area */
.study-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.card-counter {
  font-weight: 800;
  color: #555;
  font-size: 0.9rem;
}

.box-indicator {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  background: #eef2f7;
  color: #4b5563;
}

.box-indicator.box-1 { background: #ffebee; color: #c62828; }
.box-indicator.box-2 { background: #fff3e0; color: #e65100; }
.box-indicator.box-3 { background: #e3f2fd; color: #1565c0; }
.box-indicator.box-4,
.box-indicator.box-5 { background: #e8f5e9; color: #2e7d32; }

.bookmark-icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 2px solid #e5e5e5;
  background: #fff;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.bookmark-icon-btn.bookmarked {
  border-color: #ffb300;
  color: #ffb300;
  background: #fffdf0;
}

.session-progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 1.2rem;
}

.session-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #0288d1, #009688);
  transition: width 0.35s ease;
}

/* 3D Flip Card */
.flip-scene {
  perspective: 1200px;
  width: 100%;
  min-height: 340px;
  cursor: pointer;
  margin-bottom: 1.25rem;
}

.flip-card {
  position: relative;
  width: 100%;
  min-height: 340px;
  transform-style: preserve-3d;
  transition: transform 0.55s cubic-bezier(0.22, 1, 0.36, 1);
}

.flip-card.flipped {
  transform: rotateY(180deg);
}

.card-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  background: #ffffff;
  border: 2px solid #e2e8f0;
  border-bottom-width: 5px;
  border-radius: 22px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

.card-back {
  transform: rotateY(180deg);
  border-color: #0288d1;
  background: #fafdff;
}

.face-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.tag-cat {
  background: #e3f2fd;
  color: #0277bd;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
}

.tag-sub {
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
}

.tag-answer {
  background: #d7ffb8;
  color: #2e7d32;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
}

.face-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1rem 0;
}

.front-question {
  margin: 0;
  font-size: 1.25rem;
  line-height: 1.85;
  color: #1f2937;
  text-align: center;
  font-weight: 800;
}

.back-body {
  justify-content: flex-start;
  overflow-y: auto;
  gap: 0.9rem;
}

.back-answer {
  margin: 0;
  font-size: 1rem;
  line-height: 1.85;
  color: #1f2937;
  white-space: pre-line;
}

.pearl-box {
  background: #fff8e1;
  border-right: 4px solid #ffb300;
  border-radius: 10px;
  padding: 0.75rem 0.95rem;
  font-size: 0.88rem;
  color: #5d4037;
}

.pearl-box strong {
  display: block;
  margin-bottom: 0.25rem;
}

.pearl-box p {
  margin: 0;
  line-height: 1.65;
}

.face-footer {
  text-align: center;
  font-size: 0.8rem;
  color: #9ca3af;
  padding-top: 0.5rem;
  border-top: 1px dashed #e5e7eb;
}

/* Controls */
.controls-area {
  display: flex;
  justify-content: center;
}

.flip-cta {
  width: 100%;
  max-width: 340px;
  padding: 0.95rem 1.5rem;
  font-size: 1.05rem;
}

.rating-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  width: 100%;
}

.rate-btn {
  border: 2px solid transparent;
  border-bottom-width: 4px;
  border-radius: 14px;
  padding: 0.8rem 0.6rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  transition: transform 0.1s, filter 0.15s;
}

.rate-btn:active:not(:disabled) {
  transform: translateY(2px);
}

.rate-btn strong {
  font-size: 0.98rem;
}

.rate-btn span {
  font-size: 0.75rem;
  opacity: 0.88;
}

.rate-hard {
  background: #ffebee;
  color: #c62828;
  border-color: #ef9a9a;
}

.rate-medium {
  background: #e3f2fd;
  color: #1565c0;
  border-color: #90caf9;
}

.rate-easy {
  background: #e8f5e9;
  color: #2e7d32;
  border-color: #a5d6a7;
}

/* Empty / Done State */
.state-box {
  background: #ffffff;
  border: 2px solid #e5e5e5;
  border-radius: 20px;
  padding: 2.5rem 1.5rem;
  text-align: center;
}

.done-emoji {
  font-size: 3.5rem;
  margin-bottom: 0.5rem;
}

.done-box h2 {
  margin: 0 0 0.75rem;
  color: #2c3e50;
}

.done-box p {
  color: #5c6b7a;
  margin-bottom: 1.5rem;
}

.done-actions {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

@media (max-width: 600px) {
  .stats-strip {
    grid-template-columns: repeat(2, 1fr);
  }
  .flip-scene,
  .flip-card {
    min-height: 380px;
  }
  .front-question {
    font-size: 1.08rem;
  }
  .rating-grid {
    gap: 0.5rem;
  }
  .rate-btn span {
    font-size: 0.7rem;
  }
}
</style>
