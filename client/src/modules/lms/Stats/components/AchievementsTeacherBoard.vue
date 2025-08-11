<template>
  <div class="mb-3">
    <h6 class="mb-2">Достижения</h6>
    <div class="mb-3">
      <strong>Выдано по категориям</strong>
      <div v-for="c in data.awarded_by_category || []" :key="c.category" class="mb-1">
        <div class="d-flex align-items-center mb-1">
          <span class="me-2">{{ c.title || c.category }}</span>
          <span class="ms-auto text-muted">{{ c.count }}</span>
        </div>
        <div class="progress" style="height:6px;">
          <div class="progress-bar" :style="{ width: `${c.count || 0}%` }"></div>
        </div>
      </div>
      <p v-if="!(data.awarded_by_category && data.awarded_by_category.length)" class="text-muted">Нет данных</p>
    </div>

    <div class="mb-3">
      <strong>Лидерборд</strong>
      <table class="table table-sm mb-0">
        <tbody>
          <tr v-for="u in data.leaderboard || []" :key="u.user_id" style="cursor:pointer" @click="goUser(u.user_id)">
            <td>{{ u.full_name }}</td>
            <td class="text-end">{{ u.points }}</td>
          </tr>
          <tr v-if="!(data.leaderboard && data.leaderboard.length)"><td class="text-center text-muted" colspan="2">Нет данных</td></tr>
        </tbody>
      </table>
    </div>

    <div>
      <strong>Почти заработали</strong>
      <ul class="list-unstyled mb-0">
        <li v-for="a in data.almost_earned || []" :key="a.user_id" style="cursor:pointer" @click="goUserBadge(a)">
          {{ a.full_name }} - {{ a.badge.title }}
        </li>
        <li v-if="!(data.almost_earned && data.almost_earned.length)" class="text-muted">Нет данных</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
  filters: { type: Object, default: () => ({}) }
})
const router = useRouter()
function goUser(id) {
  router.push({ path: '/lms/badges', query: { tab: 'user', user: id, ...props.filters } })
}
function goUserBadge(a) {
  router.push({ path: '/lms/badges', query: { tab: 'user', user: a.user_id, focus: a.badge.id, ...props.filters } })
}
</script>
