<template>
  <div class="clinical-case-wrapper">
    <div v-if="question.patient" class="patient-chart">
      <div class="chart-header">
        <span class="chart-badge">پرونده بیمارنما</span>
        <span v-if="question.patient.setting" class="setting-badge">
          {{ question.patient.setting }}
        </span>
      </div>

      <div class="patient-meta">
        <span v-if="question.patient.gender"><strong>جنسیت:</strong> {{ question.patient.gender }}</span>
        <span v-if="question.patient.age"><strong>سن:</strong> {{ question.patient.age }}</span>
      </div>

      <div v-if="question.patient.chief_complaint" class="complaint-box">
        <strong>شکایت اصلی:</strong> {{ question.patient.chief_complaint }}
      </div>

      <p v-if="question.patient.details" class="patient-details">
        {{ question.patient.details }}
      </p>
    </div>

    <p class="case-instruction">{{ question.instruction }}</p>

    <div class="case-options">
      <button
        v-for="opt in normalizedOptions"
        :key="opt.id"
        type="button"
        class="case-option-card"
        :class="getOptionClass(opt.id)"
        :disabled="disabled"
        @click="selectOption(opt.id)"
      >
        <span class="radio-dot"></span>
        <span class="option-text">{{ opt.text }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  question: { type: Object, required: true },
  feedback: { type: Object, default: () => ({}) },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(['update:answer']);

const selectedIds = ref([]);

const isMulti = computed(() => {
  return Array.isArray(props.question.solution) && props.question.solution.length > 1;
});

const normalizedOptions = computed(() => {
  return (props.question.options || []).map((opt) =>
    typeof opt === 'string' ? { id: opt, text: opt } : opt
  );
});

watch(
  () => props.question,
  () => {
    selectedIds.value = [];
    emit('update:answer', null);
  },
  { immediate: true }
);

const selectOption = (optId) => {
  if (props.disabled) return;
  if (isMulti.value) {
    if (selectedIds.value.includes(optId)) {
      selectedIds.value = selectedIds.value.filter((id) => id !== optId);
    } else {
      selectedIds.value = [...selectedIds.value, optId];
    }
  } else {
    selectedIds.value = [optId];
  }
  emit('update:answer', [...selectedIds.value]);
};

const getOptionClass = (optId) => {
  const isSelected = selectedIds.value.includes(optId);
  const fb = props.feedback?.[optId];
  return {
    selected: isSelected && !fb,
    correct: fb === 'correct',
    incorrect: isSelected && fb === 'incorrect',
    disabled: props.disabled,
  };
};
</script>

<style scoped>
.clinical-case-wrapper {
  width: 100%;
  text-align: right;
  direction: rtl;
}

.patient-chart {
  background: #ffffff;
  border: 2px solid var(--color-border);
  border-right: 6px solid var(--color-secondary);
  border-radius: 16px;
  padding: 1.2rem 1.35rem;
  margin-bottom: 1.25rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.85rem;
}

.chart-badge {
  font-weight: 900;
  color: var(--color-secondary-dark);
  font-size: 0.95rem;
}

.setting-badge {
  background: var(--color-secondary-light);
  color: var(--color-secondary-dark);
  padding: 0.22rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 800;
}

.patient-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  font-size: 0.9rem;
  color: var(--color-text);
  margin-bottom: 0.65rem;
}

.complaint-box {
  background: var(--color-background-page);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  font-size: 0.94rem;
  color: var(--color-text);
  margin-bottom: 0.65rem;
}

.patient-details {
  margin: 0;
  font-size: 0.94rem;
  line-height: 1.75;
  color: var(--color-text-light);
}

.case-instruction {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--color-text);
  margin: 0 0 1rem;
}

.case-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.case-option-card {
  width: 100%;
  background: #ffffff;
  border: 2px solid var(--color-border);
  border-bottom-width: 4px;
  border-radius: 14px;
  padding: 1rem 1.15rem;
  text-align: right;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.15s ease;
  color: var(--color-text);
  font-size: 0.95rem;
  line-height: 1.65;
  font-weight: 700;
}

.case-option-card:hover:not(:disabled) {
  border-color: var(--color-secondary);
  background: #f8fbfd;
}

.radio-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--color-border-strong);
  margin-top: 4px;
  flex-shrink: 0;
  transition: all 0.15s;
}

.case-option-card.selected {
  border-color: var(--color-secondary);
  border-bottom-color: var(--color-secondary-shadow);
  background: var(--color-secondary-light);
  color: var(--color-secondary-dark);
}

.case-option-card.selected .radio-dot {
  border-color: var(--color-secondary);
  background: var(--color-secondary);
}

.case-option-card.correct {
  border-color: var(--color-primary) !important;
  border-bottom-color: var(--color-primary-shadow) !important;
  background: var(--color-primary-light) !important;
  color: var(--color-primary-dark) !important;
}

.case-option-card.correct .radio-dot {
  border-color: var(--color-primary);
  background: var(--color-primary);
}

.case-option-card.incorrect {
  border-color: var(--color-danger) !important;
  border-bottom-color: var(--color-danger-shadow) !important;
  background: var(--color-danger-light) !important;
  color: var(--color-danger-dark) !important;
}

.case-option-card.incorrect .radio-dot {
  border-color: var(--color-danger);
  background: var(--color-danger);
}

.case-option-card.disabled {
  cursor: not-allowed;
}
</style>
