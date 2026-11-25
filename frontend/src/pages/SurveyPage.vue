<template>
  <div class="survey-page">
    <header class="survey-header">
      <div class="header-inner">
        <router-link to="/dashboard" class="back-btn" title="بازگشت به داشبورد">
          <font-awesome-icon icon="fas fa-arrow-right" />
        </router-link>
        <div>
          <h1>پرسشنامه ارزشیابی بازی آموزشی (MEEGA+)</h1>
          <p>دیدگاه شما به ارتقای کیفیت علمی و آموزشی AntibioticPlay کمک می‌کند (+۵۰ XP پاداش)</p>
        </div>
      </div>
    </header>

    <main class="survey-container">
      <div v-if="loading" class="state-card">در حال بررسی وضعیت پرسشنامه...</div>

      <!-- قبلاً ثبت شده -->
      <div v-else-if="alreadySubmitted" class="state-card success-card">
        <div class="big-emoji">✅</div>
        <h2>پرسشنامه شما با موفقیت ثبت شده است</h2>
        <p>از همکاری ارزشمند شما در این پژوهش آموزشی سپاسگزاریم.</p>
        <router-link to="/dashboard" class="btn btn-primary">بازگشت به داشبورد</router-link>
      </div>

      <!-- فرم اصلی ۳۱ سوالی -->
      <form v-else @submit.prevent="handleSubmit" class="survey-form">
        <!-- نوار پیشرفت -->
        <div class="sticky-progress">
          <div class="progress-info">
            <span>پیشرفت تکمیل پرسشنامه</span>
            <strong>{{ answeredCount }} از ۳۱ سوال</strong>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${(answeredCount / 31) * 100}%` }"></div>
          </div>
        </div>

        <!-- بخش ۱: اطلاعات دموگرافیک (۴ سوال) -->
        <section class="form-section card">
          <h2>بخش اول: اطلاعات جمعیت‌شناختی</h2>

          <div class="demo-grid">
            <div class="field-group">
              <label for="age">۱. سن (سال)</label>
              <input
                id="age"
                v-model.number="form.age"
                type="number"
                min="16"
                max="80"
                placeholder="مثلاً ۲۳"
                required
              />
            </div>

            <div class="field-group">
              <label>۲. جنسیت</label>
              <div class="choice-row">
                <button
                  type="button"
                  class="choice-pill"
                  :class="{ active: form.gender === 'زن' }"
                  @click="form.gender = 'زن'"
                >
                  زن
                </button>
                <button
                  type="button"
                  class="choice-pill"
                  :class="{ active: form.gender === 'مرد' }"
                  @click="form.gender = 'مرد'"
                >
                  مرد
                </button>
              </div>
            </div>
          </div>

          <div class="field-group">
            <label>۳. معمولاً با چه تواتری بازی‌های دیجیتالی انجام می‌دهید؟</label>
            <div class="choice-row wrap">
              <button
                v-for="opt in gameFrequencies"
                :key="'d-' + opt"
                type="button"
                class="choice-pill"
                :class="{ active: form.digital_game_freq === opt }"
                @click="form.digital_game_freq = opt"
              >
                {{ opt }}
              </button>
            </div>
          </div>

          <div class="field-group">
            <label>۴. معمولاً با چه تواتری بازی‌های معمولی انجام می‌دهید؟ (مانند تخته نرد، شطرنج، مونوپولی و غیره)</label>
            <div class="choice-row wrap">
              <button
                v-for="opt in gameFrequencies"
                :key="'t-' + opt"
                type="button"
                class="choice-pill"
                :class="{ active: form.traditional_game_freq === opt }"
                @click="form.traditional_game_freq = opt"
              >
                {{ opt }}
              </button>
            </div>
          </div>
        </section>

        <!-- بخش ۲: ۲۷ گویه استاندارد MEEGA+ در ۴ حیطه -->
        <section
          v-for="group in meegaGroups"
          :key="group.title"
          class="form-section card"
        >
          <h2>{{ group.title }}</h2>
          <p class="section-hint">میزان موافقت خود را با هر عبارت از ۱ (کاملاً مخالفم) تا ۵ (کاملاً موافقم) مشخص کنید.</p>

          <div
            v-for="item in group.items"
            :key="item.key"
            class="likert-row"
            :class="{ unanswered: showValidation && !form.answers[item.key] }"
          >
            <p class="likert-question">
              <span class="q-num">{{ item.num }}.</span>
              {{ item.text }}
            </p>
            <div class="likert-options">
              <button
                v-for="opt in likertScale"
                :key="opt.value"
                type="button"
                class="likert-btn"
                :class="{ selected: form.answers[item.key] === opt.value }"
                @click="form.answers[item.key] = opt.value"
              >
                <span class="likert-num">{{ opt.value }}</span>
                <span class="likert-label">{{ opt.label }}</span>
              </button>
            </div>
          </div>
        </section>

        <!-- بخش ۳: بازخورد کیفی اختیاری -->
        <section class="form-section card">
          <h2>نظرات و پیشنهادات تکمیلی (اختیاری)</h2>
          <textarea
            v-model="form.qualitative_feedback"
            rows="4"
            class="feedback-textarea"
            placeholder="نقاط قوت، ضعف یا پیشنهادهای خود برای بهبود بازی را بنویسید..."
          ></textarea>
        </section>

        <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

        <div class="submit-row">
          <button type="submit" class="btn btn-primary submit-btn" :disabled="submitting">
            {{ submitting ? 'در حال ثبت...' : 'ثبت پرسشنامه و دریافت +۵۰ XP' }}
          </button>
        </div>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import surveyService from '../services/surveyService';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notificationStore';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';

library.add(faArrowRight);

const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const loading = ref(true);
const alreadySubmitted = ref(false);
const submitting = ref(false);
const showValidation = ref(false);
const errorMsg = ref('');

const gameFrequencies = [
  'هرگز',
  'به ندرت',
  'ماهانه (یک‌بار در ماه)',
  'هفتگی (یک یا چندبار در هفته)',
  'روزانه (هر روز)',
];

const likertScale = [
  { value: 1, label: 'کاملاً مخالفم' },
  { value: 2, label: 'مخالفم' },
  { value: 3, label: 'نظری ندارم' },
  { value: 4, label: 'موافقم' },
  { value: 5, label: 'کاملاً موافقم' },
];

const meegaGroups = [
  {
    title: 'حیطه اول: طراحی بصری و رابط کاربری',
    items: [
      { num: 1, key: 'q1', text: 'طراحی بازی جذاب بود (گرافیک، اشکال، ...).' },
      { num: 2, key: 'q2', text: 'رنگ و فونت متن هم‌خوانی داشت و به خوبی با هم ترکیب شده بود.' },
      { num: 8, key: 'q8', text: 'فونت بازی (سایز و نوع آن) خوانا است.' },
      { num: 9, key: 'q9', text: 'رنگ‌های به کار رفته در بازی معنی‌دار است.' },
    ],
  },
  {
    title: 'حیطه دوم: قابلیت استفاده و سهولت یادگیری',
    items: [
      { num: 3, key: 'q3', text: 'آموزش‌های قبل از هر مرحله از بازی جهت انجام بازی ضروری و مفید بود.' },
      { num: 4, key: 'q4', text: 'یادگیری نحوه انجام بازی برای من آسان بود.' },
      { num: 5, key: 'q5', text: 'قواعد انجام بازی ساده و قابل فهم بود.' },
      { num: 6, key: 'q6', text: 'فکر می‌کنم انجام این بازی آسان است.' },
      { num: 7, key: 'q7', text: 'قواعد بازی بسیار واضح و قابل فهم است.' },
    ],
  },
  {
    title: 'حیطه سوم: چالش، درگیری و غرقگی (Flow)',
    items: [
      { num: 11, key: 'q11', text: 'این بازی به طور مناسبی برای من چالش‌برانگیز است.' },
      { num: 12, key: 'q12', text: 'این بازی چالش‌های جدیدی را (موانع، موقعیت‌ها یا تغییرات جدید) با سرعت مناسب ارائه می‌دهد.' },
      { num: 13, key: 'q13', text: 'بازی با تکالیف تکراری یا کسل‌کننده یکنواخت نمی‌شد.' },
      { num: 14, key: 'q14', text: 'انجام تکالیف بازی احساس رضایت‌بخش از موفقیت را به من بخشید.' },
      { num: 15, key: 'q15', text: 'این به خاطر تلاش شخصی من است که توانستم در بازی پیشرفت کنم.' },
      { num: 18, key: 'q18', text: 'بازی سرگرم‌کننده بود.' },
      { num: 19, key: 'q19', text: 'در طول بازی اتفاقاتی افتاد (عناصر بازی، رقابت و ...) که باعث شد بخندم.' },
      { num: 20, key: 'q20', text: 'در شروع بازی چیزهای جالبی وجود داشت که توجه من را به خود جلب کرد.' },
      { num: 21, key: 'q21', text: 'من آنقدر درگیر بازی بودم که گذر زمان را حس نکردم.' },
      { num: 22, key: 'q22', text: 'چنان غرق بازی بودم که به محیط پیرامونم توجه نداشتم.' },
    ],
  },
  {
    title: 'حیطه چهارم: ارزش آموزشی و یادگیری درک‌شده',
    items: [
      { num: 10, key: 'q10', text: 'محتوا و ساختار بازی به من کمک می‌کرد که اطمینان حاصل کنم که من از این بازی یاد خواهم گرفت.' },
      { num: 16, key: 'q16', text: 'من از چیزهایی که از بازی آموخته‌ام احساس رضایت دارم.' },
      { num: 17, key: 'q17', text: 'من این بازی را به دوستانم توصیه می‌کنم.' },
      { num: 23, key: 'q23', text: 'برای من روشن است که محتوای بازی با محتوای کلاس درس مرتبط است.' },
      { num: 24, key: 'q24', text: 'این بازی به تنهایی جهت تدریس این موضوع کفایت می‌کند.' },
      { num: 25, key: 'q25', text: 'من یادگیری با این بازی را به یادگیری از طریق روش‌های دیگر (به عنوان مثال سایر روش‌های تدریس) ترجیح می‌دهم.' },
      { num: 26, key: 'q26', text: 'بازی به یادگیری من در این موضوع کمک کرده است.' },
      { num: 27, key: 'q27', text: 'یادگیری کارآمد به واسطه بازی در مقایسه با سایر روش‌ها امکان‌پذیر بود.' },
    ],
  },
];

const form = reactive({
  age: null,
  gender: '',
  digital_game_freq: '',
  traditional_game_freq: '',
  answers: {},
  qualitative_feedback: '',
});

const answeredCount = computed(() => {
  let count = 0;
  if (form.age) count++;
  if (form.gender) count++;
  if (form.digital_game_freq) count++;
  if (form.traditional_game_freq) count++;
  count += Object.keys(form.answers).length;
  return count;
});

onMounted(async () => {
  try {
    const res = await surveyService.getStatus();
    alreadySubmitted.value = Boolean(res.data?.submitted);
  } catch (err) {
    console.error('Error loading survey status:', err);
  } finally {
    loading.value = false;
  }
});

const handleSubmit = async () => {
  errorMsg.value = '';
  showValidation.value = true;

  if (answeredCount.value < 31) {
    errorMsg.value = 'لطفاً به تمام ۳۱ سوال (۴ سوال دموگرافیک و ۲۷ گویه پرسشنامه) پاسخ دهید.';
    return;
  }

  submitting.value = true;
  try {
    const res = await surveyService.submitSurvey({
      age: form.age,
      gender: form.gender,
      digital_game_freq: form.digital_game_freq,
      traditional_game_freq: form.traditional_game_freq,
      answers: form.answers,
      qualitative_feedback: form.qualitative_feedback,
    });

    if (typeof res.data.new_total_score === 'number') {
      authStore.updateUserScore(res.data.new_total_score);
      authStore.updateUserLevel(res.data.new_level);
    }

    alreadySubmitted.value = true;
    notificationStore.showNotification({
      title: '🎉 سپاس از مشارکت شما!',
      message: `پرسشنامه با موفقیت ثبت شد و +${res.data.xp_awarded || 50} XP به امتیاز شما اضافه گردید.`,
    });
    router.push('/dashboard');
  } catch (err) {
    errorMsg.value = err.response?.data?.message || 'خطا در ثبت پرسشنامه. لطفاً دوباره تلاش کنید.';
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.survey-page {
  min-height: 100vh;
  background: #f6f8fb;
  direction: rtl;
  padding-bottom: 3rem;
}

.survey-header {
  background: linear-gradient(135deg, #0288d1, #009688);
  color: #fff;
  padding: 1.25rem 1.5rem;
}

.header-inner {
  max-width: 860px;
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
  flex-shrink: 0;
}

.survey-header h1 {
  margin: 0;
  font-size: 1.25rem;
}

.survey-header p {
  margin: 0.2rem 0 0;
  font-size: 0.85rem;
  opacity: 0.92;
}

.survey-container {
  max-width: 860px;
  margin: 1.25rem auto 0;
  padding: 0 1rem;
}

.sticky-progress {
  position: sticky;
  top: 0;
  z-index: 15;
  background: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 14px;
  padding: 0.85rem 1.1rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.88rem;
  color: #4b5563;
  margin-bottom: 0.45rem;
}

.progress-track {
  height: 9px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #0288d1, #009688);
  transition: width 0.3s ease;
}

.card {
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 18px;
  padding: 1.4rem;
  margin-bottom: 1.25rem;
}

.form-section h2 {
  margin: 0 0 0.4rem;
  font-size: 1.12rem;
  color: #0277bd;
}

.section-hint {
  margin: 0 0 1.1rem;
  font-size: 0.84rem;
  color: #6b7280;
}

.demo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.field-group {
  margin-bottom: 1rem;
}

.field-group label {
  display: block;
  font-weight: 700;
  font-size: 0.92rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.field-group input {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 0.95rem;
  box-sizing: border-box;
}

.choice-row {
  display: flex;
  gap: 0.5rem;
}

.choice-row.wrap {
  flex-wrap: wrap;
}

.choice-pill {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.5rem 0.9rem;
  font-size: 0.86rem;
  font-weight: 700;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.15s;
}

.choice-pill.active {
  background: #e1f5fe;
  border-color: #0288d1;
  color: #01579b;
}

.likert-row {
  padding: 0.95rem 0.85rem;
  border-radius: 12px;
  border: 1px solid #f0f2f5;
  margin-bottom: 0.75rem;
  background: #fafbfc;
}

.likert-row.unanswered {
  border-color: #ef9a9a;
  background: #fff5f5;
}

.likert-question {
  margin: 0 0 0.7rem;
  font-size: 0.94rem;
  color: #1f2937;
  font-weight: 700;
  line-height: 1.6;
}

.q-num {
  color: #0288d1;
  margin-left: 0.25rem;
}

.likert-options {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.45rem;
}

.likert-btn {
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.45rem 0.25rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  color: #4b5563;
  transition: all 0.15s;
}

.likert-btn:hover {
  border-color: #90caf9;
}

.likert-btn.selected {
  background: #0288d1;
  border-color: #0288d1;
  color: #fff;
}

.likert-num {
  font-size: 1rem;
  font-weight: 900;
}

.likert-label {
  font-size: 0.7rem;
  text-align: center;
}

.feedback-textarea {
  width: 100%;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 0.85rem;
  font-family: inherit;
  font-size: 0.94rem;
  box-sizing: border-box;
  resize: vertical;
}

.error-banner {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ef9a9a;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  font-weight: 700;
}

.submit-row {
  display: flex;
  justify-content: center;
}

.submit-btn {
  width: 100%;
  max-width: 380px;
  padding: 1rem 1.5rem;
  font-size: 1.05rem;
}

.state-card {
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  padding: 2.5rem 1.5rem;
  text-align: center;
}

.big-emoji {
  font-size: 3.5rem;
  margin-bottom: 0.5rem;
}

@media (max-width: 650px) {
  .demo-grid {
    grid-template-columns: 1fr;
  }
  .likert-label {
    font-size: 0.62rem;
  }
}
</style>
