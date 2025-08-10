<template>
  <div class="container-fluid py-3">
    <div class="row mb-3 g-2 align-items-end">
      <div class="col-md-3">
        <label class="form-label">От</label>
        <input type="date" v-model="filters.from" class="form-control" />
      </div>
      <div class="col-md-3">
        <label class="form-label">До</label>
        <input type="date" v-model="filters.to" class="form-control" />
      </div>
      <div class="col-md-3">
        <label class="form-label">Курс</label>
        <select v-model="filters.course" class="form-select">
          <option value="">Все</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
    </div>

    <StatsSummary v-if="data" :summary="data.summary" :role="role" class="mb-4" />

    <div v-if="role === 'student' && data">
      <div class="row">
        <div class="col-lg-8">
          <GradeTrendChart :data="data.grade_trend" />
        </div>
        <div class="col-lg-4">
          <DeadlinesList :deadlines="data.upcoming_deadlines" />
        </div>
      </div>
      <AchievementsProgress class="mt-3" :achievements="data.achievements_progress" />
      <Recommendations class="mt-3" :items="data.recommendations" />
    </div>

    <div v-else-if="role === 'teacher' && data">
      <CoursesTable :courses="data.courses" class="mb-3" />
      <div class="row">
        <div class="col-lg-6">
          <GradeDistributionChart :distribution="data.grade_distribution" />
        </div>
        <div class="col-lg-6">
          <AtRiskList :students="data.at_risk_students" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { lmsApi } from '../js/lmsApi'
import { useUserRole } from '../composables/useUserRole'
import StatsSummary from './components/StatsSummary.vue'
import GradeTrendChart from './components/GradeTrendChart.vue'
import DeadlinesList from './components/DeadlinesList.vue'
import AchievementsProgress from './components/AchievementsProgress.vue'
import CoursesTable from './components/CoursesTable.vue'
import GradeDistributionChart from './components/GradeDistributionChart.vue'
import AtRiskList from './components/AtRiskList.vue'
import Recommendations from './components/Recommendations.vue'

const userRole = useUserRole()
const role = computed(() => (userRole.isTeacher.value || userRole.isAdmin.value) ? 'teacher' : 'student')

const filters = ref({ from: '', to: '', course: '' })
const courses = ref([])
const data = ref(null)

async function loadCourses() {
  const res = await lmsApi.getCourses()
  courses.value = res.data.results || res.data || []
}

async function loadData() {
  const params = { role: role.value }
  if (filters.value.from) params.from = filters.value.from
  if (filters.value.to) params.to = filters.value.to
  if (filters.value.course) params.course = filters.value.course
  const res = await lmsApi.get('/analytics/dashboard/', params)
  data.value = res.data
}

onMounted(async () => {
  await loadCourses()
  await loadData()
})

watch(filters, loadData, { deep: true })
</script>
