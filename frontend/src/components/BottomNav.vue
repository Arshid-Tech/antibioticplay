<template>
  <nav class="bottom-nav">
    <router-link to="/dashboard" class="nav-item" active-class="active">
      <div class="icon-container">
        <font-awesome-icon icon="fas fa-house" />
      </div>
      <span class="nav-label">خانه</span>
    </router-link>

    <router-link to="/flashcards" class="nav-item" active-class="active">
      <div class="icon-container">
        <font-awesome-icon icon="fas fa-layer-group" />
      </div>
      <span class="nav-label">فلش‌کارت</span>
    </router-link>

    <router-link to="/leaderboard" class="nav-item" active-class="active">
      <div class="icon-container">
        <font-awesome-icon icon="fas fa-trophy" />
      </div>
      <span class="nav-label">لیگ</span>
    </router-link>

    <router-link to="/profile" class="nav-item" active-class="active">
      <div class="icon-container">
        <font-awesome-icon icon="fas fa-user" />
      </div>
      <span class="nav-label">پروفایل</span>
    </router-link>
  </nav>
</template>

<script setup>
import { library } from '@fortawesome/fontawesome-svg-core';
import { faHouse, faLayerGroup, faTrophy, faUser } from '@fortawesome/free-solid-svg-icons';

library.add(faHouse, faLayerGroup, faTrophy, faUser);
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 70px;
  background-color: white;
  border-top: 2px solid #e5e5e5;
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 999;
  padding-bottom: env(safe-area-inset-bottom);
  box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #afafaf;
  flex: 1;
  height: 100%;
  cursor: pointer;
  transition: color 0.2s;
}

.icon-container {
  font-size: 1.4rem;
  margin-bottom: 4px;
  transition: transform 0.1s;
}

.nav-label {
  font-size: 0.72rem;
  font-weight: 700;
}

.nav-item.active {
  color: var(--color-secondary);
}

.nav-item.active .icon-container {
  transform: translateY(-2px);
}

@media (min-width: 851px) {
  .bottom-nav {
    display: none;
  }
}
</style>
