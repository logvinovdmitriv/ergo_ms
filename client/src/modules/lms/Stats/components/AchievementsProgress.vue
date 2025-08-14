<template>
  <div class="row g-3">
    <div v-for="a in achievements" :key="a.badge_id" class="col-12 col-md-6 col-lg-4">
      <Card>
        <div class="d-flex align-items-center mb-2">
          <img v-if="a.icon" :src="a.icon" class="me-2" style="width:24px;height:24px" />
          <strong>{{ a.title }}</strong>
          <span class="badge bg-secondary ms-auto">{{ a.category }}</span>
        </div>
        <div class="progress mb-1">
          <div class="progress-bar" role="progressbar" :style="{ width: `${a.progress}%` }"></div>
        </div>
        <small v-if="!a.unlocked" class="text-muted">Осталось {{ a.next_threshold - a.progress }}</small>
        <small v-else class="text-success">Получено</small>
      </Card>
    </div>
    <div v-if="!achievements.length" class="col-12">
      <Card><p class="text-muted mb-0">Нет данных</p></Card>
    </div>
  </div>
</template>

<script setup>
import Card from '../shared/Card.vue'
const props = defineProps({ achievements: { type: Array, default: () => [] } })
</script>
