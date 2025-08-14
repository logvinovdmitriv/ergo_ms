<template>
  <div class="row g-3">
    <div v-for="card in cards" :key="card.label" class="col-12 col-md-4 col-lg-2">
      <div class="card text-center h-100">
        <div class="card-body">
          <div class="h5 mb-1">{{ card.value }}</div>
          <div class="text-muted small">{{ card.label }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  summary: { type: Object, default: () => ({}) },
  role: { type: String, default: 'student' }
})

const cards = computed(() => {
  if (props.role === 'teacher') {
    return [
      { label: 'Активных курсов', value: props.summary?.active_courses || 0 },
      { label: 'Записано', value: props.summary?.enrolled || 0 },
      { label: 'Завершённость %', value: props.summary?.completion_rate || 0 },
      { label: 'В срок %', value: props.summary?.on_time_rate || 0 },
      { label: 'Средний балл', value: props.summary?.avg_grade ?? '-' },
      { label: 'На проверке', value: props.summary?.pending_reviews || 0 }
    ]
  }
  return [
    { label: 'Курсов в прогрессе', value: props.summary?.in_progress || 0 },
    { label: 'Завершено', value: props.summary?.completed || 0 },
    { label: 'GPA', value: props.summary?.gpa ?? '-' },
    { label: 'Просрочки', value: props.summary?.overdue_tasks || 0 },
    { label: 'Стрик', value: props.summary?.streak_days || 0 }
  ]
})
</script>

<style scoped>
.card {
  min-height: 100%;
}
</style>
