<template>
  <Card>
    <h5 class="mb-3">Студенты в зоне риска</h5>
    <ul class="list-group list-group-flush">
      <li v-for="s in students" :key="s.user_id" class="list-group-item">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <div>{{ s.full_name }}</div>
            <small class="text-muted">{{ s.course.name }}</small>
          </div>
          <div class="text-end">
            <span class="badge bg-danger me-2">{{ s.overdues }}</span>
            <small class="text-muted">{{ formatDate(s.last_activity) }}</small>
          </div>
        </div>
      </li>
      <li v-if="!students.length" class="list-group-item text-muted">Нет данных</li>
    </ul>
  </Card>
</template>

<script setup>
import Card from '../shared/Card.vue'
import { format } from 'date-fns'
const props = defineProps({ students: { type: Array, default: () => [] } })
function formatDate(d) {
  if (!d) return ''
  return format(new Date(d), 'dd.MM.yyyy')
}
</script>
