<template>
  <Card>
    <h5 class="mb-3">Курсы</h5>
    <div class="table-responsive">
      <table class="table table-sm">
        <thead>
          <tr>
            <th>Курс</th>
            <th>Записано</th>
            <th>Завершённость %</th>
            <th>Ср. балл</th>
            <th>В срок %</th>
            <th>Просрочки</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in courses" :key="c.id">
            <td>{{ c.name }}</td>
            <td><span class="badge bg-primary">{{ c.enrolled }}</span></td>
            <td>{{ Number(c.completion_rate).toFixed(1) }}</td>
            <td>{{ c.avg_grade ?? '-' }}</td>
            <td>{{ Number(c.on_time_rate).toFixed(1) }}</td>
            <td><span class="badge bg-danger">{{ c.overdues }}</span></td>
          </tr>
          <tr v-if="!courses.length">
            <td colspan="6" class="text-muted">Нет данных</td>
          </tr>
        </tbody>
      </table>
    </div>
  </Card>
</template>

<script setup>
import Card from '../shared/Card.vue'
const props = defineProps({ courses: { type: Array, default: () => [] } })
</script>
