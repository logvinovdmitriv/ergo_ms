<template>
  <Card>
    <h5 class="mb-3">Ближайшие дедлайны</h5>
    <ul class="list-group list-group-flush">
      <li v-for="d in deadlines" :key="d.id" class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <div>{{ d.title }}</div>
          <small class="text-muted">{{ d.course.name }}</small>
        </div>
        <span :class="statusClass(d.status)">{{ formatDate(d.due) }}</span>
      </li>
      <li v-if="!deadlines.length" class="list-group-item text-muted">Нет данных</li>
    </ul>
  </Card>
</template>

<script setup>
import Card from '../shared/Card.vue'
import { format } from 'date-fns'

const props = defineProps({ deadlines: { type: Array, default: () => [] } })

function statusClass(status) {
  return {
    'badge bg-danger': status === 'overdue',
    'badge bg-warning text-dark': status === 'risk',
    'badge bg-secondary': status === 'ok'
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return format(new Date(dateStr), 'dd.MM.yyyy')
}
</script>
