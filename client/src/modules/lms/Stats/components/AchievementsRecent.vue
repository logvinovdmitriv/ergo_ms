<template>
  <div class="mb-3">
    <h6 class="mb-2">Последние достижения</h6>
    <div class="d-flex overflow-auto">
      <div
        v-for="a in items"
        :key="a.id"
        class="me-3 text-center"
        style="cursor:pointer"
        @click="goBadge(a.id)"
      >
        <img v-if="a.icon" :src="a.icon" style="width:48px;height:48px" class="mb-1" />
        <div class="small">{{ a.title }}</div>
      </div>
      <div v-if="!items.length" class="text-muted">Нет данных</div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  items: { type: Array, default: () => [] },
  filters: { type: Object, default: () => ({}) }
})
const router = useRouter()
function goBadge(id) {
  router.push({ path: '/lms/badges', query: { tab: 'my', focus: id, ...props.filters } })
}
</script>
