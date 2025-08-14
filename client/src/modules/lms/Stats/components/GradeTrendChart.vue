<template>
  <Card>
    <h5 class="mb-3">Тренд оценок</h5>
    <canvas v-if="data.length" ref="canvas" height="120"></canvas>
    <p v-else class="text-muted mb-0">Нет данных</p>
  </Card>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { Chart } from 'chart.js/auto'
import Card from '../shared/Card.vue'

const props = defineProps({ data: { type: Array, default: () => [] } })
const canvas = ref(null)
let chart

function render() {
  if (!canvas.value) return
  if (chart) chart.destroy()
  const labels = props.data.map(d => d.date)
  const values = props.data.map(d => d.avg_grade)
  chart = new Chart(canvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{ label: 'Средний балл', data: values, fill: false, tension: 0.3 }]
    },
    options: {
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  })
}

onMounted(render)
watch(() => props.data, render)
</script>
