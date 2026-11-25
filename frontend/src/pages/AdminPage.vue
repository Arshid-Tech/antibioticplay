<template>
  <div class="admin-page">
    <header class="admin-header">
      <div class="header-inner">
        <router-link to="/dashboard" class="back-btn" title="بازگشت به داشبورد">
          <font-awesome-icon icon="fas fa-arrow-right" />
        </router-link>
        <div>
          <h1>پنل مدیریت محتوا و آنالیتیکس پژوهشی</h1>
          <p>مدیریت مراحل، سوالات، مینی‌درس‌ها، فلش‌کارت‌ها و خروجی مستقیم SPSS</p>
        </div>
      </div>
    </header>

    <div class="admin-tabs">
      <button
        v-for="t in tabs"
        :key="t.id"
        class="tab-btn"
        :class="{ active: activeTab === t.id }"
        @click="activeTab = t.id"
      >
        {{ t.label }}
      </button>
    </div>

    <main class="admin-body">
      <section v-if="activeTab === 'analytics'" class="tab-panel">
        <div class="export-bar card">
          <div>
            <h3>خروجی مستقیم داده‌های پژوهشی (Excel / SPSS)</h3>
            <p>فایل‌ها با انکودینگ UTF-8-SIG آماده باز شدن مستقیم در Excel و SPSS هستند.</p>
          </div>
          <div class="export-buttons">
            <button class="btn btn-primary" @click="exportCsv('combined')">
              خروجی ترکیبی (لاگ‌ها + MEEGA+)
            </button>
            <button class="btn btn-outline" @click="exportCsv('users')">
              لاگ عملکرد بازی
            </button>
            <button class="btn btn-outline" @click="exportCsv('survey')">
              پاسخ‌های MEEGA+
            </button>
          </div>
        </div>

        <div v-if="analytics" class="kpi-grid">
          <div class="kpi-card">
            <span class="kpi-val">{{ analytics.kpis.total_users }}</span>
            <span class="kpi-lbl">کل کاربران</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val">{{ analytics.kpis.active_users }}</span>
            <span class="kpi-lbl">کاربران فعال</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val">{{ analytics.kpis.survey_responses }}</span>
            <span class="kpi-lbl">پرسشنامه‌های ثبت‌شده</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val">{{ analytics.kpis.meega_total_mean }}</span>
            <span class="kpi-lbl">میانگین کل MEEGA+</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val">{{ analytics.kpis.total_flashcard_reviews }}</span>
            <span class="kpi-lbl">مرور فلش‌کارت</span>
          </div>
        </div>

        <div v-if="analytics" class="card">
          <h3>میانگین حیطه‌های پرسشنامه MEEGA+ (از ۵)</h3>
          <div class="domain-bars">
            <div v-for="d in analytics.meega_domains" :key="d.key" class="domain-row">
              <div class="domain-meta">
                <span>{{ d.label }}</span>
                <strong>{{ d.mean }} / 5</strong>
              </div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: `${(d.mean / 5) * 100}%` }"></div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="analytics" class="card table-card">
          <h3>عملکرد دانشجویان به تفکیک مراحل بازی</h3>
          <div class="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>مرحله</th>
                  <th>تعداد سوال</th>
                  <th>شروع‌کننده</th>
                  <th>تکمیل‌کننده</th>
                  <th>نرخ تکمیل</th>
                  <th>میانگین بهترین نمره</th>
                  <th>میانگین تلاش</th>
                  <th>حداکثر تلاش</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in analytics.quiz_stats" :key="row.id">
                  <td><strong>{{ row.title }}</strong></td>
                  <td>{{ row.questions_count }}</td>
                  <td>{{ row.started_count }}</td>
                  <td>{{ row.completed_count }}</td>
                  <td>{{ row.completion_rate }}٪</td>
                  <td>{{ row.avg_best_score }}</td>
                  <td>{{ row.avg_attempts }}</td>
                  <td>{{ row.max_attempts }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="analytics?.qualitative_notes?.length" class="card">
          <h3>نظرات کیفی دانشجویان</h3>
          <div class="notes-list">
            <div v-for="(n, idx) in analytics.qualitative_notes" :key="idx" class="note-item">
              <div class="note-head">
                <strong>@{{ n.username }}</strong>
              </div>
              <p>{{ n.text }}</p>
            </div>
          </div>
        </div>
      </section>

      <section v-else-if="activeTab === 'quizzes'" class="tab-panel">
        <div class="card">
          <h3>افزودن مرحله جدید</h3>
          <form class="inline-form" @submit.prevent="createQuiz">
            <select v-model="newQuiz.unit_id" required>
              <option value="" disabled>انتخاب بخش (Unit)</option>
              <option v-for="u in units" :key="u.id" :value="u.id">{{ u.title }}</option>
            </select>
            <input v-model="newQuiz.title" placeholder="عنوان مرحله جدید" required />
            <input v-model="newQuiz.description" placeholder="توضیح کوتاه" />
            <button type="submit" class="btn btn-primary">افزودن مرحله</button>
          </form>
        </div>

        <div v-for="quiz in quizzes" :key="quiz.id" class="card quiz-edit-card">
          <div class="quiz-edit-head">
            <div>
              <strong>{{ quiz.title }}</strong>
              <span class="id-badge">{{ quiz.id }}</span>
            </div>
            <div class="row-actions">
              <button class="btn-sm btn-save" @click="saveQuiz(quiz)">ذخیره تغییرات</button>
              <button class="btn-sm btn-del" @click="deleteQuiz(quiz.id)">حذف</button>
            </div>
          </div>
          <div class="form-grid">
            <label>
              عنوان مرحله
              <input v-model="quiz.title" />
            </label>
            <label>
              توضیحات
              <input v-model="quiz.description" />
            </label>
          </div>
          <label class="full-label">
            متن مینی‌درس (خلاصه درس پیش از شروع مرحله)
            <textarea v-model="quiz.micro_lesson" rows="4" placeholder="نکات کلیدی مرحله را اینجا بنویسید..."></textarea>
          </label>
        </div>
      </section>

      <section v-else-if="activeTab === 'questions'" class="tab-panel">
        <div class="card">
          <div class="filter-row">
            <label>انتخاب مرحله:</label>
            <select v-model="selectedQuizId">
              <option v-for="q in quizzes" :key="q.id" :value="q.id">
                {{ q.title }} ({{ q.questions?.length || 0 }} سوال)
              </option>
            </select>
            <button class="btn btn-primary" @click="openNewQuestionModal">+ سوال جدید</button>
          </div>
        </div>

        <div v-if="selectedQuiz" class="questions-list">
          <div v-for="item in selectedQuiz.questions" :key="item.id" class="card question-row">
            <div class="q-row-info">
              <span class="type-pill">{{ item.type }}</span>
              <strong>{{ item.title || item.id }}</strong>
              <span class="pts-pill">{{ item.points_per_correct || 10 }} امتیاز</span>
            </div>
            <div class="row-actions">
              <button class="btn-sm btn-save" @click="editQuestion(item)">ویرایش</button>
              <button class="btn-sm btn-del" @click="deleteQuestion(item.id)">حذف</button>
            </div>
          </div>
        </div>

        <div v-if="questionModal.open" class="modal-overlay" @click.self="questionModal.open = false">
          <div class="modal-card">
            <h3>{{ questionModal.isEdit ? 'ویرایش سوال' : 'افزودن سوال جدید' }}</h3>
            <div class="form-grid">
              <label>
                عنوان سوال
                <input v-model="questionModal.title" />
              </label>
              <label>
                نوع سوال
                <select v-model="questionModal.type">
                  <option value="clinical-case">clinical-case (کیس بالینی)</option>
                  <option value="multiple-select">multiple-select (چندانتخابی)</option>
                  <option value="true-false">true-false (درست/نادرست)</option>
                  <option value="drag-drop-match">drag-drop-match (تطبیق)</option>
                  <option value="drag-drop-fill">drag-drop-fill (جای خالی)</option>
                  <option value="image-labeling">image-labeling (برچسب‌گذاری تصویر)</option>
                </select>
              </label>
              <label>
                امتیاز
                <input v-model.number="questionModal.points" type="number" min="1" />
              </label>
            </div>
            <label class="full-label">
              ساختار JSON سوال (instruction, options, solution, hint, explanation, ...)
              <textarea v-model="questionModal.payloadJson" rows="12" dir="ltr" class="code-area"></textarea>
            </label>
            <p v-if="questionModal.error" class="err-text">{{ questionModal.error }}</p>
            <div class="modal-actions">
              <button class="btn btn-primary" @click="saveQuestionModal">ذخیره سوال</button>
              <button class="btn btn-outline" @click="questionModal.open = false">انصراف</button>
            </div>
          </div>
        </div>
      </section>

      <section v-else-if="activeTab === 'flashcards'" class="tab-panel">
        <div class="card">
          <h3>{{ fcForm.id ? 'ویرایش فلش‌کارت' : 'افزودن فلش‌کارت جدید' }}</h3>
          <form @submit.prevent="saveFlashcard" class="fc-form">
            <div class="form-grid">
              <label>
                دسته دارویی
                <input v-model="fcForm.category" placeholder="مثلاً: پنی‌سیلین‌ها و تست پوستی" required />
              </label>
              <label>
                زیردسته (اختیاری)
                <input v-model="fcForm.subcategory" placeholder="مثلاً: دوزینگ" />
              </label>
              <label>
                شناسه سوال مرتبط (اختیاری)
                <input v-model="fcForm.related_question_id" dir="ltr" placeholder="q_coamox_ratios" />
              </label>
            </div>
            <label class="full-label">
              روی کارت (سوال)
              <textarea v-model="fcForm.front" rows="2" required></textarea>
            </label>
            <label class="full-label">
              پشت کارت (پاسخ علمی)
              <textarea v-model="fcForm.back" rows="3" required></textarea>
            </label>
            <label class="full-label">
              نکته بالینی و بازار ایران (اختیاری)
              <textarea v-model="fcForm.clinical_pearl" rows="2"></textarea>
            </label>
            <div class="row-actions">
              <button type="submit" class="btn btn-primary">
                {{ fcForm.id ? 'بروزرسانی کارت' : 'افزودن کارت' }}
              </button>
              <button v-if="fcForm.id" type="button" class="btn btn-outline" @click="resetFcForm">
                انصراف از ویرایش
              </button>
            </div>
          </form>
        </div>

        <div class="card">
          <div class="filter-row">
            <input v-model="fcSearch" placeholder="جستجو در فلش‌کارت‌ها..." class="search-input" />
            <span>{{ filteredFlashcards.length }} کارت</span>
          </div>
          <div class="fc-list">
            <div v-for="c in filteredFlashcards" :key="c.id" class="fc-item">
              <div class="fc-item-body">
                <span class="type-pill">{{ c.category }}</span>
                <strong>{{ c.front }}</strong>
                <p>{{ c.back }}</p>
              </div>
              <div class="row-actions">
                <button class="btn-sm btn-save" @click="editFlashcard(c)">ویرایش</button>
                <button class="btn-sm btn-del" @click="deleteFlashcard(c.id)">حذف</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-else-if="activeTab === 'users'" class="tab-panel">
        <div class="card table-card">
          <h3>لیست کاربران و مدیریت دسترسی ادمین</h3>
          <div class="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>نام کاربری</th>
                  <th>نام و نام خانوادگی</th>
                  <th>ایمیل</th>
                  <th>امتیاز</th>
                  <th>پرسشنامه</th>
                  <th>نقش</th>
                  <th>عملیات</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.id">
                  <td><strong>{{ u.username }}</strong></td>
                  <td>{{ `${u.first_name} ${u.last_name}`.trim() || '-' }}</td>
                  <td dir="ltr">{{ u.email }}</td>
                  <td>{{ u.score }}</td>
                  <td>{{ u.survey_submitted ? 'ثبت شده' : '—' }}</td>
                  <td>
                    <span class="role-badge" :class="u.role">{{ u.role === 'admin' ? 'مدیر' : 'دانشجو' }}</span>
                  </td>
                  <td>
                    <button class="btn-sm btn-save" @click="toggleRole(u)">
                      {{ u.role === 'admin' ? 'تغییر به دانشجو' : 'ارتقا به مدیر' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import adminService from '../services/adminService';
import { useNotificationStore } from '../stores/notificationStore';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';

library.add(faArrowRight);

const notificationStore = useNotificationStore();

const tabs = [
  { id: 'analytics', label: 'آنالیتیکس و SPSS' },
  { id: 'quizzes', label: 'مراحل و مینی‌درس‌ها' },
  { id: 'questions', label: 'مدیریت سوالات' },
  { id: 'flashcards', label: 'مدیریت فلش‌کارت‌ها' },
  { id: 'users', label: 'کاربران و دسترسی‌ها' },
];

const activeTab = ref('analytics');
const analytics = ref(null);
const units = ref([]);
const quizzes = ref([]);
const selectedQuizId = ref('');
const flashcards = ref([]);
const fcSearch = ref('');
const users = ref([]);

const newQuiz = reactive({ unit_id: '', title: '', description: '' });

const questionModal = reactive({
  open: false,
  isEdit: false,
  id: '',
  title: '',
  type: 'clinical-case',
  points: 20,
  payloadJson: '',
  error: '',
});

const fcForm = reactive({
  id: null,
  category: '',
  subcategory: '',
  front: '',
  back: '',
  clinical_pearl: '',
  related_question_id: '',
});

const selectedQuiz = computed(() =>
  quizzes.value.find((q) => q.id === selectedQuizId.value) || null
);

const filteredFlashcards = computed(() => {
  const q = fcSearch.value.trim().toLowerCase();
  if (!q) return flashcards.value;
  return flashcards.value.filter(
    (c) =>
      c.category.toLowerCase().includes(q) ||
      c.front.toLowerCase().includes(q) ||
      c.back.toLowerCase().includes(q)
  );
});

const loadAll = async () => {
  try {
    const [anRes, qRes, fcRes, uRes] = await Promise.all([
      adminService.getAnalytics(),
      adminService.getQuizzes(),
      adminService.getFlashcards(),
      adminService.getUsers(),
    ]);
    analytics.value = anRes.data;
    units.value = qRes.data.units || [];
    quizzes.value = qRes.data.quizzes || [];
    if (!selectedQuizId.value && quizzes.value.length) {
      selectedQuizId.value = quizzes.value[0].id;
    }
    flashcards.value = fcRes.data || [];
    users.value = uRes.data || [];
  } catch (err) {
    console.error('Admin load error:', err);
    notificationStore.showNotification({
      title: 'خطا در دسترسی',
      message: err.response?.data?.message || 'خطا در بارگذاری اطلاعات پنل مدیریت.',
    });
  }
};

onMounted(loadAll);

const exportCsv = async (type) => {
  try {
    const res = await adminService.downloadExport(type);
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `antibioticplay_${type}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch {
    notificationStore.showNotification({
      title: 'خطا',
      message: 'دانلود فایل ناموفق بود.',
    });
  }
};

const createQuiz = async () => {
  try {
    const res = await adminService.createQuiz({ ...newQuiz });
    quizzes.value.push(res.data);
    newQuiz.title = '';
    newQuiz.description = '';
    notificationStore.showNotification({ title: 'انجام شد', message: 'مرحله جدید اضافه شد.' });
  } catch (err) {
    notificationStore.showNotification({
      title: 'خطا',
      message: err.response?.data?.message || 'ایجاد مرحله ناموفق بود.',
    });
  }
};

const saveQuiz = async (quiz) => {
  try {
    await adminService.updateQuiz(quiz.id, {
      title: quiz.title,
      description: quiz.description,
      micro_lesson: quiz.micro_lesson,
    });
    notificationStore.showNotification({ title: 'ذخیره شد', message: 'تغییرات مرحله ذخیره شد.' });
  } catch {
    notificationStore.showNotification({ title: 'خطا', message: 'ذخیره تغییرات ناموفق بود.' });
  }
};

const deleteQuiz = async (quizId) => {
  if (!confirm('آیا از حذف این مرحله و تمام سوالات آن مطمئن هستید؟')) return;
  await adminService.deleteQuiz(quizId);
  quizzes.value = quizzes.value.filter((q) => q.id !== quizId);
};

const openNewQuestionModal = () => {
  questionModal.open = true;
  questionModal.isEdit = false;
  questionModal.id = '';
  questionModal.title = '';
  questionModal.type = 'clinical-case';
  questionModal.points = 20;
  questionModal.error = '';
  questionModal.payloadJson = JSON.stringify(
    {
      instruction: 'مناسب‌ترین اقدام بالینی کدام است؟',
      patient: {
        age: '۳۵ سال',
        gender: 'خانم',
        setting: 'داروخانه شهری',
        chief_complaint: 'شرح حال کوتاه بیمار',
        details: 'جزئیات بالینی...',
      },
      options: [
        { id: 'opt1', text: 'گزینه ۱' },
        { id: 'opt2', text: 'گزینه ۲' },
      ],
      solution: ['opt1'],
      hint: 'راهنمایی علمی سوال',
      explanation: 'توضیح علمی پس از پاسخ',
    },
    null,
    2
  );
};

const editQuestion = (item) => {
  questionModal.open = true;
  questionModal.isEdit = true;
  questionModal.id = item.id;
  questionModal.title = item.title || '';
  questionModal.type = item.type || 'multiple-select';
  questionModal.points = item.points_per_correct || 10;
  questionModal.error = '';
  questionModal.payloadJson = JSON.stringify(item, null, 2);
};

const saveQuestionModal = async () => {
  questionModal.error = '';
  let parsed;
  try {
    parsed = JSON.parse(questionModal.payloadJson);
  } catch {
    questionModal.error = 'ساختار JSON نامعتبر است. لطفاً نحو JSON را بررسی کنید.';
    return;
  }

  try {
    if (questionModal.isEdit) {
      await adminService.updateQuestion(questionModal.id, {
        title: questionModal.title,
        type: questionModal.type,
        points_per_correct: questionModal.points,
        payload: parsed,
      });
    } else {
      await adminService.createQuestion({
        quiz_id: selectedQuizId.value,
        title: questionModal.title,
        type: questionModal.type,
        points_per_correct: questionModal.points,
        payload: parsed,
      });
    }
    questionModal.open = false;
    await loadAll();
    notificationStore.showNotification({ title: 'ذخیره شد', message: 'سوال با موفقیت ذخیره شد.' });
  } catch (err) {
    questionModal.error = err.response?.data?.message || 'خطا در ذخیره سوال.';
  }
};

const deleteQuestion = async (questionId) => {
  if (!confirm('این سوال حذف شود؟')) return;
  await adminService.deleteQuestion(questionId);
  await loadAll();
};

const resetFcForm = () => {
  fcForm.id = null;
  fcForm.category = '';
  fcForm.subcategory = '';
  fcForm.front = '';
  fcForm.back = '';
  fcForm.clinical_pearl = '';
  fcForm.related_question_id = '';
};

const editFlashcard = (c) => {
  fcForm.id = c.id;
  fcForm.category = c.category;
  fcForm.subcategory = c.subcategory;
  fcForm.front = c.front;
  fcForm.back = c.back;
  fcForm.clinical_pearl = c.clinical_pearl;
  fcForm.related_question_id = c.related_question_id;
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const saveFlashcard = async () => {
  try {
    if (fcForm.id) {
      await adminService.updateFlashcard(fcForm.id, { ...fcForm });
    } else {
      await adminService.createFlashcard({ ...fcForm });
    }
    resetFcForm();
    const res = await adminService.getFlashcards();
    flashcards.value = res.data;
    notificationStore.showNotification({ title: 'ذخیره شد', message: 'فلش‌کارت ذخیره شد.' });
  } catch (err) {
    notificationStore.showNotification({
      title: 'خطا',
      message: err.response?.data?.message || 'خطا در ذخیره فلش‌کارت.',
    });
  }
};

const deleteFlashcard = async (id) => {
  if (!confirm('این فلش‌کارت حذف شود؟')) return;
  await adminService.deleteFlashcard(id);
  flashcards.value = flashcards.value.filter((c) => c.id !== id);
};

const toggleRole = async (u) => {
  const nextRole = u.role === 'admin' ? 'student' : 'admin';
  await adminService.updateUserRole(u.id, nextRole);
  u.role = nextRole;
};
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: var(--color-background-page);
  direction: rtl;
  padding-bottom: 3rem;
}

.admin-header {
  background-color: var(--color-hero-bg);
  border-bottom: 4px solid #0d2a42;
  color: #fff;
  padding: 1.2rem 1.5rem;
}

.header-inner {
  max-width: 1120px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.admin-header h1 { margin: 0; font-size: 1.25rem; color: #fff; }
.admin-header p { margin: 0.2rem 0 0; font-size: 0.84rem; opacity: 0.9; }

.admin-tabs {
  max-width: 1120px;
  margin: 1rem auto 0;
  padding: 0 1rem;
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
}

.tab-btn {
  background: #fff;
  border: 2px solid var(--color-border);
  border-bottom-width: 4px;
  border-radius: 12px;
  padding: 0.6rem 1rem;
  font-weight: 800;
  font-size: 0.86rem;
  color: var(--color-text-light);
  cursor: pointer;
  white-space: nowrap;
}

.tab-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  border-bottom-color: var(--color-primary-shadow);
  color: #fff;
}

.admin-body {
  max-width: 1120px;
  margin: 1rem auto 0;
  padding: 0 1rem;
}

.card {
  background: #fff;
  border: 2px solid var(--color-border);
  border-bottom-width: 4px;
  border-radius: 16px;
  padding: 1.35rem;
  margin-bottom: 1.25rem;
}

.card h3 { margin: 0 0 1rem; color: var(--color-text); font-size: 1.05rem; }

.export-bar { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }
.export-bar p { margin: 0; font-size: 0.85rem; color: var(--color-text-light); }
.export-buttons { display: flex; gap: 0.5rem; flex-wrap: wrap; }

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.85rem;
  margin-bottom: 1.25rem;
}

.kpi-card {
  background: #fff;
  border: 2px solid var(--color-border);
  border-bottom-width: 4px;
  border-radius: 16px;
  padding: 1.1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.kpi-val { font-size: 1.8rem; font-weight: 900; color: var(--color-primary); }
.kpi-lbl { font-size: 0.82rem; color: var(--color-text-light); font-weight: 700; }

.domain-bars { display: flex; flex-direction: column; gap: 0.9rem; }
.domain-meta { display: flex; justify-content: space-between; font-size: 0.9rem; margin-bottom: 0.35rem; }
.bar-track { height: 12px; background: #dfe6ec; border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; background-color: var(--color-primary); border-radius: 999px; }

.table-scroll { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
th, td { padding: 0.7rem 0.6rem; border-bottom: 1px solid var(--color-border); text-align: right; }
th { background: var(--color-background-page); color: var(--color-text-light); font-weight: 800; }

.notes-list { display: flex; flex-direction: column; gap: 0.75rem; }
.note-item { background: var(--color-background-page); border-radius: 12px; padding: 0.85rem 1rem; border: 1px solid var(--color-border); }
.note-item p { margin: 0.35rem 0 0; color: var(--color-text); line-height: 1.6; }

.inline-form, .filter-row { display: flex; gap: 0.65rem; flex-wrap: wrap; align-items: center; }

input, select, textarea {
  border: 2px solid var(--color-border);
  border-radius: 10px;
  padding: 0.55rem 0.75rem;
  font-family: inherit;
  font-size: 0.9rem;
  background: var(--color-background-page);
  box-sizing: border-box;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.85rem;
  margin-bottom: 0.85rem;
}

.form-grid label, .full-label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-text);
}

.full-label { margin-bottom: 0.85rem; }
.code-area { font-family: monospace; font-size: 0.82rem; }

.quiz-edit-head, .question-row, .fc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.quiz-edit-head { margin-bottom: 0.9rem; }

.id-badge, .type-pill, .pts-pill, .role-badge {
  display: inline-block;
  padding: 0.18rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 800;
  margin-right: 0.4rem;
}
.id-badge { background: var(--color-background-off); color: var(--color-text-light); }
.type-pill { background: var(--color-secondary-light); color: var(--color-secondary-dark); }
.pts-pill { background: var(--color-warning-light); color: var(--color-warning-dark); }
.role-badge.admin { background: var(--color-secondary-light); color: var(--color-secondary-dark); }
.role-badge.student { background: var(--color-primary-light); color: var(--color-primary-dark); }

.row-actions { display: flex; gap: 0.45rem; }
.btn-sm { border: none; border-radius: 8px; padding: 0.42rem 0.75rem; font-size: 0.8rem; font-weight: 800; cursor: pointer; }
.btn-save { background: var(--color-secondary-light); color: var(--color-secondary-dark); }
.btn-del { background: var(--color-danger-light); color: var(--color-danger-dark); }

.fc-list { display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem; }
.fc-item { padding: 0.9rem; border: 1px solid var(--color-border); border-radius: 12px; align-items: flex-start; }
.fc-item-body { flex: 1; }
.fc-item-body strong { display: block; margin: 0.3rem 0; color: var(--color-text); }
.fc-item-body p { margin: 0; font-size: 0.86rem; color: var(--color-text-light); line-height: 1.6; }
.search-input { flex: 1; min-width: 220px; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(19, 34, 48, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
  padding: 1rem;
}
.modal-card {
  background: #fff;
  border-radius: 18px;
  padding: 1.5rem;
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-actions { display: flex; gap: 0.65rem; justify-content: flex-end; }
.err-text { color: var(--color-danger-dark); font-weight: 700; font-size: 0.85rem; }
</style>
