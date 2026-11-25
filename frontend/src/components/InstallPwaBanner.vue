<template>
  <transition name="slide-up">
    <div v-if="showInstallBanner" class="pwa-banner install-banner" role="region" aria-label="نصب اپلیکیشن">
      <div class="pwa-banner-content">
        <img src="/images/antibioticplay.ir.png" alt="AntibioticPlay" class="pwa-app-icon" />
        <div class="pwa-text">
          <strong>نصب اپلیکیشن AntibioticPlay</strong>
          <p v-if="isIos">
            در مرورگر Safari دکمه <strong>Share</strong> و سپس <strong>Add to Home Screen</strong> را بزنید.
          </p>
          <p v-else>
            برای دسترسی سریع‌تر و تجربه تمام‌صفحه، اپلیکیشن را روی دستگاه خود نصب کنید.
          </p>
        </div>
      </div>
      <div class="pwa-actions">
        <button v-if="!isIos" class="pwa-btn pwa-btn-primary" @click="triggerInstall">
          نصب
        </button>
        <button class="pwa-btn pwa-btn-ghost" @click="dismissBanner">
          بستن
        </button>
      </div>
    </div>
  </transition>

  <transition name="slide-up">
    <div v-if="needRefresh" class="pwa-banner update-banner" role="alert">
      <div class="pwa-banner-content">
        <div class="pwa-text">
          <strong>نسخه جدید آماده است</strong>
          <p>برای دریافت امکانات و محتوای جدید، برنامه را بروزرسانی کنید.</p>
        </div>
      </div>
      <div class="pwa-actions">
        <button class="pwa-btn pwa-btn-primary" @click="updateServiceWorker(true)">
          بروزرسانی
        </button>
        <button class="pwa-btn pwa-btn-ghost" @click="needRefresh = false">
          بعداً
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRegisterSW } from 'virtual:pwa-register/vue';

const DISMISS_KEY = 'pwa_install_dismissed_at';
const DISMISS_DAYS = 7;

const deferredPrompt = ref(null);
const showInstallBanner = ref(false);
const isIos = ref(false);

const { needRefresh, updateServiceWorker } = useRegisterSW({
  onRegistered(r) {
    if (r) {
      setInterval(() => {
        r.update();
      }, 60 * 60 * 1000);
    }
  },
});

const isRecentlyDismissed = () => {
  const saved = localStorage.getItem(DISMISS_KEY);
  if (!saved) return false;
  const elapsed = Date.now() - Number(saved);
  return elapsed < DISMISS_DAYS * 24 * 60 * 60 * 1000;
};

const isStandalone = () => {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true
  );
};

const handleBeforeInstallPrompt = (e) => {
  e.preventDefault();
  deferredPrompt.value = e;
  if (!isStandalone() && !isRecentlyDismissed()) {
    showInstallBanner.value = true;
  }
};

const handleAppInstalled = () => {
  showInstallBanner.value = false;
  deferredPrompt.value = null;
};

const triggerInstall = async () => {
  if (!deferredPrompt.value) return;
  deferredPrompt.value.prompt();
  const { outcome } = await deferredPrompt.value.userChoice;
  if (outcome === 'accepted') {
    showInstallBanner.value = false;
  }
  deferredPrompt.value = null;
};

const dismissBanner = () => {
  showInstallBanner.value = false;
  localStorage.setItem(DISMISS_KEY, String(Date.now()));
};

onMounted(() => {
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  window.addEventListener('appinstalled', handleAppInstalled);

  const ua = window.navigator.userAgent.toLowerCase();
  isIos.value = /iphone|ipad|ipod/.test(ua);
  if (isIos.value && !isStandalone() && !isRecentlyDismissed()) {
    showInstallBanner.value = true;
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  window.removeEventListener('appinstalled', handleAppInstalled);
});
</script>

<style scoped>
.pwa-banner {
  position: fixed;
  bottom: 1.25rem;
  right: 1.25rem;
  left: 1.25rem;
  max-width: 460px;
  margin: 0 auto;
  background: #ffffff;
  border: 2px solid var(--color-border);
  border-bottom-width: 4px;
  border-radius: 16px;
  padding: 1rem 1.2rem;
  z-index: 1200;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  direction: rtl;
}

.update-banner {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.pwa-banner-content {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.pwa-app-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  object-fit: contain;
  flex-shrink: 0;
  background: var(--color-background-page);
  padding: 4px;
}

.pwa-text strong {
  display: block;
  font-size: 0.96rem;
  color: var(--color-text);
  margin-bottom: 0.2rem;
}

.pwa-text p {
  margin: 0;
  font-size: 0.84rem;
  color: var(--color-text-light);
  line-height: 1.5;
}

.pwa-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.pwa-btn {
  min-width: 0 !important;
  border: 2px solid transparent;
  border-bottom-width: 3px;
  border-radius: 10px;
  padding: 0.45rem 1rem;
  font-size: 0.86rem;
  font-weight: 800;
  cursor: pointer;
}

.pwa-btn-primary {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  border-bottom-color: var(--color-primary-shadow);
  color: #ffffff;
}

.pwa-btn-ghost {
  background-color: var(--color-background-off);
  border-color: var(--color-border);
  color: var(--color-text-light);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.25s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

@media (max-width: 850px) {
  .pwa-banner { bottom: 84px; }
}
</style>
