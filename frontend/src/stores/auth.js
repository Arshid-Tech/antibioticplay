import { defineStore } from 'pinia';
import authService from '../services/authService';
import router from '../router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    returnUrl: null,
    triggerScoreAnimation: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    username: (state) => state.user?.username,
    fullName: (state) => {
      if (state.user && state.user.first_name && state.user.last_name) {
        return `${state.user.first_name} ${state.user.last_name}`;
      }
      return state.user?.username || 'کاربر';
    },
    score: (state) => state.user?.score || 0,
    level: (state) => state.user?.level || 1,
    userLeague: (state) =>
      state.user?.league || { name: 'برنز', color: '#cd7f32', icon: 'fas fa-medal' },
    correctStreak: (state) => state.user?.correct_streak || 0,
  },

  actions: {
    async fetchUser() {
      try {
        const response = await authService.getProfile();
        this.user = response.data;
        localStorage.setItem('user', JSON.stringify(this.user));
      } catch (error) {
        console.error('Failed to fetch user profile:', error);
        // Only logout on explicit 401; preserve session on transient network/cold-start errors
        if (error.response && error.response.status === 401) {
          this.logout();
        }
      }
    },

    async login(username, password) {
      try {
        const response = await authService.login(username, password);
        this.token = response.data.access_token;
        localStorage.setItem('token', response.data.access_token);
        await this.fetchUser();
        router.push(this.returnUrl || '/dashboard');
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },

    async register(username, email, password, firstName, lastName) {
      try {
        await authService.register(username, email, password, firstName, lastName);
        await this.login(username, password);
      } catch (error) {
        console.error('Registration failed:', error);
        throw error;
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      router.push('/login');
    },

    updateUserScore(newScore) {
      if (this.user) {
        const oldScore = this.user.score;
        this.user.score = newScore;
        localStorage.setItem('user', JSON.stringify(this.user));
        if (newScore > oldScore) {
          this.triggerScoreAnimation = true;
        }
      }
    },

    updateUserLevel(newLevel) {
      if (this.user) {
        this.user.level = newLevel;
        localStorage.setItem('user', JSON.stringify(this.user));
      }
    },

    resetScoreAnimationTrigger() {
      this.triggerScoreAnimation = false;
    },
  },
});
