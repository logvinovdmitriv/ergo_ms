<template>
  <Card class="mb-3">
    <div class="d-flex align-items-center mb-2">
      <div class="me-4">
        <div class="text-muted small">Всего значков</div>
        <div class="h4 mb-0">{{ summary.total_badges || 0 }}</div>
      </div>
      <div class="me-4">
        <div class="text-muted small">Очки</div>
        <div class="h4 mb-0">{{ summary.total_points || 0 }}</div>
      </div>
      <button class="btn btn-sm btn-primary ms-auto" @click="goAll">Все достижения</button>
    </div>
    <div>
      <span
        v-for="cat in summary.by_category || []"
        :key="cat.code"
        class="badge bg-secondary me-2"
        style="cursor:pointer"
        @click="goCategory(cat.code)"
      >
        {{ cat.title }} ({{ cat.count }})
      </span>
      <span v-if="!(summary.by_category && summary.by_category.length)" class="text-muted">Нет данных</span>
    </div>
  </Card>
</template>

<script setup>
import Card from '../shared/Card.vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  summary: { type: Object, default: () => ({}) },
  filters: { type: Object, default: () => ({}) }
})

const router = useRouter()

function goAll() {
  router.push({ path: '/lms/badges', query: { tab: 'my', ...props.filters } })
}

function goCategory(code) {
  router.push({ path: '/lms/badges', query: { tab: 'my', category: code, ...props.filters } })
}
</script>
