<template>
  <div class="clinical-case-wrapper">
    <!-- پرونده بیمار -->
    <div v-if="question.patient" class="patient-chart">
      <div class="chart-header">
        <span class="chart-badge">🩺 پرونده بیمارنما</span>
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

    <!-- گزینه‌های تصمیم بالینی -->
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
  border: 2px solid #cfe8fc;
  border-right: 6px solid #0288d1;
  border-radius: 16px;
  padding: 1.2rem 1.35rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 4px 14px rgba(2, 136, 209, 0.08);
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
  font-weight: 800;
  color: #0277bd;
  font-size: 0.95rem;
}

.setting-badge {
  background: #e1f5fe;
  color: #0277bd;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
}

.patient-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  font-size: 0.9rem;
  color: #374151;
  margin-bottom: 0.65rem;
}

.complaint-box {
  background: #f8fafc;
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  font-size: 0.94rem;
  color: #1f2937;
  margin-bottom: 0.65rem;
}

.patient-details {
  margin: 0;
  font-size: 0.94rem;
  line-height: 1.75;
  color: #4b5563;
}

.case-instruction {
  font-size: 1.05rem;
  font-weight: 800;
  color: #2c3e50;
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
  border: 2px solid #e5e7eb;
  border-bottom-width: 4px;
  border-radius: 14px;
  padding: 1rem 1.15rem;
  text-align: right;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.15s ease;
  color: #374151;
  font-size: 0.95rem;
  line-height: 1.65;
  font-weight: 600;
}

.case-option-card:hover:not(:disabled) {
  border-color: #90caf9;
  background: #f8fbff;
}

.radio-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #cbd5e1;
  margin-top: 4px;
  flex-shrink: 0;
  transition: all 0.15s;
}

.case-option-card.selected {
  border-color: #0288d1;
  background: #e1f5fe;
  color: #01579b;
}

.case-option-card.selected .radio-dot {
  border-color: #0288d1;
  background: #0288d1;
}

.case-option-card.correct {
  border-color: #43a047 !important;
  background: #e8f5e9 !important;
  color: #1b5e20 !important;
}

.case-option-card.correct .radio-dot {
  border-color: #43a047;
  background: #43a047;
}

.case-option-card.incorrect {
  border-color: #e53935 !important;
  background: #ffebee !important;
  color: #b71c1c !important;
}

.case-option-card.incorrect .radio-dot {
  border-color: #e53935;
  background: #e53935;
}

.case-option-card.disabled {
  cursor: not-allowed;
}
</style>
