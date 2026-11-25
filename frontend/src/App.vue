<template>
  <div id="main-container">
    <router-view />

    <BottomNav v-if="showBottomNav" />

    <NotificationDisplay
      :badge="quizStore.badgeToShowNotification"
      @close="quizStore.clearBadgeNotification"
    />

    <InstallPwaBanner />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useQuizStore } from './stores/quiz';
import NotificationDisplay from './components/NotificationDisplay.vue';
import BottomNav from './components/BottomNav.vue';
import InstallPwaBanner from './components/InstallPwaBanner.vue';

const quizStore = useQuizStore();
const route = useRoute();

const showBottomNav = computed(() => {
  const allowedRoutes = ['Dashboard', 'Leaderboard', 'Flashcards', 'Profile'];
  return allowedRoutes.includes(route.name);
});
</script>

<style>
#main-container {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0;
}
</style>
