<template>
  <div class="mb-3">
    <h6 class="mb-2">Ближайшие к получению</h6>
    <div class="row g-2">
      <div v-for="a in items" :key="a.badge_id" class="col-md-4">
        <Card class="h-100" style="cursor:pointer" @click="goBadge(a)">
          <div class="d-flex align-items-center mb-2">
            <img v-if="a.icon" :src="a.icon" class="me-2" style="width:24px;height:24px" />
            <strong class="flex-grow-1">{{ a.title }}</strong>
          </div>
          <div class="progress mb-1">
            <div class="progress-bar" role="progressbar" :style="{ width: `${a.percent || 0}%` }"></div>
          </div>
          <small class="text-muted">{{ a.current || 0 }}/{{ a.threshold || 0 }}</small>
        </Card>
      </div>
      <div v-if="!items.length" class="col-12">
        <Card><p class="text-muted mb-0">Нет данных</p></Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import Card from '../shared/Card.vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  items: { type: Array, default: () => [] },
  filters: { type: Object, default: () => ({}) }
})
const router = useRouter()
function goBadge(a) {
  router.push({ path: '/lms/badges', query: { tab: 'my', category: a.category, focus: a.badge_id, ...props.filters } })
}
</script>
