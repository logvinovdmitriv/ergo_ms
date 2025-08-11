<template>
  <div class="container-fluid py-3">
    <div class="d-flex justify-content-end mb-3">
      <RouterLink
        :to="{ name: 'LMSBadges', query: { category: route.query.category } }"
        class="btn btn-outline-primary"
      >
        К достижениям
      </RouterLink>
    </div>
    <div v-if="overview" class="row mb-4">
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h4 class="mb-1">{{ overview.cards.topics_completed }}</h4>
            <p class="text-muted mb-0">Пройдено тем</p>
          </div>
        </div>
      </div>
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h4 class="mb-1">{{ overview.cards.tasks_available }}</h4>
            <p class="text-muted mb-0">Доступно заданий</p>
          </div>
        </div>
      </div>
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h4 class="mb-1">{{ overview.cards.overall_progress_percent }}%</h4>
            <p class="text-muted mb-0">Прогресс</p>
          </div>
        </div>
      </div>
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h4 class="mb-1">{{ overview.cards.active_categories_count }}</h4>
            <p class="text-muted mb-0">Категорий</p>
          </div>
        </div>
      </div>
    </div>
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
      <AchievementsSummary :summary="data.achievements.summary" :filters="filters" />
      <AchievementsRecent :items="data.achievements.recent" :filters="filters" />
      <AchievementsNext :items="data.achievements.next" :filters="filters" />
      <div class="row">
        <div class="col-lg-8">
          <GradeTrendChart :data="data.grade_trend" />
        </div>
        <div class="col-lg-4">
          <DeadlinesList :deadlines="data.upcoming_deadlines" />
        </div>
      </div>
      <Recommendations class="mt-3" :items="data.recommendations" />
    </div>

    <div v-else-if="role === 'teacher' && data">
      <AchievementsTeacherBoard :data="data.achievements_teacher" :filters="filters" class="mb-3" />
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

    <div v-if="overview && overview.teacher_block" class="card mt-4 mb-4">
      <div class="card-header">
        <h6 class="mb-0">Мои курсы (преподаватель)</h6>
      </div>
      <div class="card-body">
        <p class="mb-1">Созданные курсы: {{ overview.teacher_block.created_courses }}</p>
        <p class="mb-1">Активных студентов: {{ overview.teacher_block.active_students }}</p>
        <p class="mb-0">Средний прогресс студентов: {{ overview.teacher_block.avg_students_progress_percent }}%</p>
      </div>
    </div>
  </div>
  <RoleSwitcher />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import RoleSwitcher from '../components/RoleSwitcher.vue'
import { lmsApi } from '../js/lmsApi'
import { getOverview } from '../api/lmsStatsApi'
import { useUserRole } from '../composables/useUserRole'
import StatsSummary from './components/StatsSummary.vue'
import GradeTrendChart from './components/GradeTrendChart.vue'
import DeadlinesList from './components/DeadlinesList.vue'
import AchievementsSummary from './components/AchievementsSummary.vue'
import AchievementsRecent from './components/AchievementsRecent.vue'
import AchievementsNext from './components/AchievementsNext.vue'
import AchievementsTeacherBoard from './components/AchievementsTeacherBoard.vue'
import CoursesTable from './components/CoursesTable.vue'
import GradeDistributionChart from './components/GradeDistributionChart.vue'
import AtRiskList from './components/AtRiskList.vue'
import Recommendations from './components/Recommendations.vue'

const userRole = useUserRole()
const role = computed(() => (userRole.isTeacher.value || userRole.isAdmin.value) ? 'teacher' : 'student')

const route = useRoute()
const filters = ref({ from: '', to: '', course: '' })
const courses = ref([])
const data = ref(null)
const overview = ref(null)

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
  try {
    const params = {}
    if (route.query.category) params.category = route.query.category
    const res = await getOverview(params)
    overview.value = res.data
  } catch (e) {
    console.error('Ошибка загрузки обзора', e)
  }
})

watch(filters, loadData, { deep: true })
</script>
