<template>
  <Card v-if="items.length">
    <h5 class="mb-3">Рекомендации</h5>
    <ul class="list-group list-group-flush">
      <li v-for="r in items" :key="r.course_id" class="list-group-item">
        <div class="fw-bold">{{ r.title }}</div>
        <small class="text-muted">{{ r.reason }}</small>
      </li>
    </ul>
  </Card>
</template>

<script setup>
import Card from '../shared/Card.vue'
const props = defineProps({ items: { type: Array, default: () => [] } })
</script>
