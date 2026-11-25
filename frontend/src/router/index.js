import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

import HomePage from '../pages/HomePage.vue';
import LoginPage from '../pages/LoginPage.vue';
import RegisterPage from '../pages/RegisterPage.vue';
import ForgotPasswordPage from '../pages/ForgotPasswordPage.vue';
import DashboardPage from '../pages/DashboardPage.vue';
import QuizPage from '../pages/QuizPage.vue';
import LeaderboardPage from '../pages/LeaderboardPage.vue';
import QuizResultPage from '../pages/QuizResultPage.vue';
import RulesPage from '../pages/RulesPage.vue';
import ReviewPage from '../pages/ReviewPage.vue';
import TermsPage from '../pages/TermsPage.vue';
import AboutPage from '../pages/AboutPage.vue';
import ContactPage from '../pages/ContactPage.vue';
import FlashcardsPage from '../pages/FlashcardsPage.vue';
import ProfilePage from '../pages/ProfilePage.vue';
import DailyChallengePage from '../pages/DailyChallengePage.vue';
import DuelPage from '../pages/DuelPage.vue';
import SurveyPage from '../pages/SurveyPage.vue';

const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/register', name: 'Register', component: RegisterPage },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPasswordPage },
  { path: '/dashboard', name: 'Dashboard', component: DashboardPage, meta: { requiresAuth: true } },
  { path: '/quiz/:id', name: 'Quiz', component: QuizPage, meta: { requiresAuth: true } },
  { path: '/leaderboard', name: 'Leaderboard', component: LeaderboardPage, meta: { requiresAuth: true } },
  { path: '/quiz/result', name: 'QuizResult', component: QuizResultPage, meta: { requiresAuth: true } },
  { path: '/rules', name: 'Rules', component: RulesPage, meta: { requiresAuth: true } },
  { path: '/review', name: 'Review', component: ReviewPage, meta: { requiresAuth: true } },
  { path: '/terms', name: 'Terms', component: TermsPage },
  { path: '/about', name: 'About', component: AboutPage },
  { path: '/contact', name: 'Contact', component: ContactPage },
  { path: '/flashcards', name: 'Flashcards', component: FlashcardsPage, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/daily-challenge', name: 'DailyChallenge', component: DailyChallengePage, meta: { requiresAuth: true } },
  { path: '/duel/:id', name: 'Duel', component: DuelPage, meta: { requiresAuth: true } },
  { path: '/survey', name: 'Survey', component: SurveyPage, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    return { top: 0 };
  },
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    authStore.returnUrl = to.fullPath;
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;
