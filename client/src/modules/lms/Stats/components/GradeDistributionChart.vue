<template>
  <Card>
    <h5 class="mb-3">Распределение оценок</h5>
    <div class="d-flex align-items-end" style="height:150px;">
      <div v-for="(count,label) in distribution" :key="label" class="flex-fill text-center">
        <div class="bg-primary mx-1" :style="{height: maxValue ? (count/maxValue*100)+'%' : '0%'}"></div>
        <small>{{ label }}</small>
      </div>
    </div>
  </Card>
</template>

<script setup>
import { computed } from 'vue'
import Card from '../shared/Card.vue'
const props = defineProps({ distribution: { type: Object, default: () => ({}) } })
const maxValue = computed(() => Math.max(...Object.values(props.distribution || {}), 0))
</script>

<style scoped>
.bg-primary {
  width: 100%;
}
</style>
