<template>
  <div class="org-stats orgs-scope">
    <div v-if="loading" class="text-center p-4">
      <div class="spinner-border" />
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
      <router-link
        :to="`/crm/organizations/${orgId}`"
        class="alert-link ms-2"
      >Назад к организации</router-link>
    </div>

    <div v-else>
      <!-- KPI CARDS -->
      <section class="mb-4">
        <div class="row g-3">
          <div
            class="col-sm-6 col-md-3"
            v-for="k in kpis"
            :key="k.label"
          >
            <div class="card text-center">
              <div class="card__body">
                <div class="h4 mb-0">{{ k.value }}</div>
                <small class="text-muted">{{ k.label }}</small>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- PROJECTS BLOCK -->
      <section class="mb-4">
        <h3>Проекты</h3>
        <div class="row">
          <div class="col-md-6">
            <h5 class="mt-3">Распределение по статусам</h5>
            <div class="list-group">
              <div
                v-for="(count, key) in projectStatusDist"
                :key="key"
                class="list-group-item"
              >
                <div class="d-flex justify-content-between">
                  <span>{{ statusLabel(key) }}</span>
                  <span>{{ count }}</span>
                </div>
                <div class="progress progress-sm">
                  <div
                    class="progress-bar"
                    :style="{ width: pct(count, projects.length) + '%' }"
                  ></div>
                </div>
              </div>
            </div>

            <h5 class="mt-3">Распределение по приоритетам</h5>
            <div class="list-group">
              <div
                v-for="(count, key) in projectPriorityDist"
                :key="key"
                class="list-group-item"
              >
                <div class="d-flex justify-content-between">
                  <span>{{ priorityLabel(key) }}</span>
                  <span>{{ count }}</span>
                </div>
                <div class="progress progress-sm">
                  <div
                    class="progress-bar"
                    :style="{ width: pct(count, projects.length) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <h5 class="mt-3">Топ‑5 активных проектов</h5>
            <div class="table-wrap">
              <table class="table table--sm">
                <thead>
                  <tr>
                    <th>Проект</th>
                    <th>Открыто</th>
                    <th>Выполнено</th>
                    <th>Прогресс</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in topProjects" :key="p.id">
                    <td>{{ p.name || '—' }}</td>
                    <td>{{ p.open }}</td>
                    <td>{{ p.done }}</td>
                    <td>
                      <div class="progress progress-sm mb-1">
                        <div
                          class="progress-bar"
                          :style="{ width: p.progress + '%' }"
                        ></div>
                      </div>
                      {{ p.progress }}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- TASKS BLOCK -->
      <section>
        <h3>Задачи</h3>
        <div class="row">
          <div class="col-md-6">
            <h5 class="mt-3">Распределение по статусам</h5>
            <div class="list-group">
              <div
                v-for="(count, key) in taskStatusDist"
                :key="key"
                class="list-group-item"
              >
                <div class="d-flex justify-content-between">
                  <span>{{ statusLabel(key) }}</span>
                  <span>{{ count }}</span>
                </div>
                <div class="progress progress-sm">
                  <div
                    class="progress-bar"
                    :style="{ width: pct(count, tasks.length) + '%' }"
                  ></div>
                </div>
              </div>
            </div>

            <h5 class="mt-3">Распределение по приоритетам</h5>
            <div class="list-group">
              <div
                v-for="(count, key) in taskPriorityDist"
                :key="key"
                class="list-group-item"
              >
                <div class="d-flex justify-content-between">
                  <span>{{ priorityLabel(key) }}</span>
                  <span>{{ count }}</span>
                </div>
                <div class="progress progress-sm">
                  <div
                    class="progress-bar"
                    :style="{ width: pct(count, tasks.length) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <h5 class="mt-3">Закрыто за последние 12 недель</h5>
            <div class="list-group">
              <div
                v-for="w in weeklyDone"
                :key="w.label"
                class="list-group-item"
              >
                <div class="d-flex justify-content-between">
                  <span>{{ w.label }}</span>
                  <span>{{ w.count }}</span>
                </div>
                <div class="progress progress-sm">
                  <div
                    class="progress-bar"
                    :style="{ width: pct(w.count, maxWeekly) + '%' }"
                  ></div>
                </div>
              </div>
            </div>

            <h5 class="mt-3">CFD (за 12 недель)</h5>
            <div class="table-wrap">
              <table class="table table--sm">
                <thead>
                  <tr>
                    <th>Неделя</th>
                    <th>Todo</th>
                    <th>In&nbsp;progress</th>
                    <th>Review</th>
                    <th>Done</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="w in cfd" :key="w.week">
                    <td>{{ w.week }}</td>
                    <td>{{ w.todo || 0 }}</td>
                    <td>{{ w.in_progress || 0 }}</td>
                    <td>{{ w.review || 0 }}</td>
                    <td>{{ w.done || 0 }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { startOfWeek, endOfWeek, subWeeks, format } from 'date-fns'
import projectManagementApi from '@/modules/crm/project-management/js/projectManagementApi.js'

const STATUS_LABELS = {
  todo: 'To do',
  in_progress: 'В работе',
  review: 'На проверке',
  done: 'Готово',
  cancelled: 'Отменено',
}

const PRIORITY_LABELS = {
  low: 'Низкий',
  medium: 'Средний',
  high: 'Высокий',
  urgent: 'Срочный',
}

export default {
  name: 'OrganizationStats',
  props: {
    orgId: { type: [String, Number], required: true },
  },
  data() {
    return {
      loading: true,
      error: null,
      projects: [],
      tasks: [],
      kpis: [],
      projectStatusDist: {},
      projectPriorityDist: {},
      taskStatusDist: {},
      taskPriorityDist: {},
      topProjects: [],
      weeklyDone: [],
      cfd: [],
    }
  },
  computed: {
    maxWeekly() {
      return Math.max(...this.weeklyDone.map(w => w.count), 1)
    },
  },
  methods: {
    pct(part, total) {
      if (!total) return 0
      return Math.round((part / total) * 100)
    },
    statusLabel(code) {
      return STATUS_LABELS[code] || code || '—'
    },
    priorityLabel(code) {
      return PRIORITY_LABELS[code] || code || '—'
    },
    weeksRange(n) {
      const weeks = []
      const now = new Date()
      for (let i = n - 1; i >= 0; i--) {
        const start = startOfWeek(subWeeks(now, i), { weekStartsOn: 1 })
        weeks.push(start)
      }
      return weeks
    },
    groupBy(list, key) {
      return list.reduce((acc, item) => {
        const val = item[key] || '—'
        acc[val] = (acc[val] || 0) + 1
        return acc
      }, {})
    },
    async loadData() {
      this.loading = true
      this.error = null
      try {
        const projRes = await projectManagementApi.getProjects({
          organization_id: this.orgId,
          page_size: 1000,
        })
        this.projects = projRes.data.results || projRes.data || []

        const tasksRes = await projectManagementApi.getTasks({
          organization_id: this.orgId,
          page_size: 1000,
        })
        this.tasks = tasksRes.data.results || tasksRes.data || []

        if (!this.tasks.length && this.projects.length) {
          for (const p of this.projects) {
            const res = await projectManagementApi.getTasks({
              project: p.id,
              page_size: 1000,
            })
            const t = res.data.results || res.data || []
            this.tasks.push(...t)
          }
        }

        this.computeStats()
      } catch (e) {
          console.error(e)
          this.error = 'Не удалось загрузить статистику'
      } finally {
        this.loading = false
      }
    },
    computeStats() {
      const projectsTotal = this.projects.length
      const doneProjects = this.projects.filter(p => p.status === 'done')
      const doneProjectsCount = doneProjects.length
      const doneProjectsPct = this.pct(doneProjectsCount, projectsTotal)

      const tasksTotal = this.tasks.length
      const doneTasks = this.tasks.filter(t => t.status === 'done')
      const doneTasksCount = doneTasks.length

      const tasksWithDue = this.tasks.filter(t => t.due_date)
      const doneOnTime = doneTasks.filter(
        t =>
          t.due_date &&
          t.completed_at &&
          new Date(t.completed_at) <= new Date(t.due_date)
      ).length
      const tasksOnTimePct = this.pct(doneOnTime, tasksWithDue.length)

      const overdueTasks = this.tasks.filter(
        t =>
          t.status !== 'done' &&
          t.due_date &&
          new Date(t.due_date) < new Date()
      ).length

      const avgTaskDuration = (() => {
        const completed = doneTasks.filter(t => t.created_at && t.completed_at)
        if (!completed.length) return 0
        const total = completed.reduce(
          (sum, t) => sum + (new Date(t.completed_at) - new Date(t.created_at)),
          0
        )
        return total / completed.length / 3600000
      })()

      const tasksByProject = {}
      this.tasks.forEach(t => {
        const pid = t.project
        ;(tasksByProject[pid] = tasksByProject[pid] || []).push(t)
      })
      const progressArr = this.projects.map(p => {
        const list = tasksByProject[p.id] || []
        const done = list.filter(t => t.status === 'done').length
        return list.length ? (done / list.length) * 100 : 0
      })
      const avgProjectProgress = progressArr.length
        ? Math.round(progressArr.reduce((a, b) => a + b, 0) / progressArr.length)
        : 0

      this.projectStatusDist = this.groupBy(this.projects, 'status')
      this.projectPriorityDist = this.groupBy(this.projects, 'priority')
      this.taskStatusDist = this.groupBy(this.tasks, 'status')
      this.taskPriorityDist = this.groupBy(this.tasks, 'priority')

      this.topProjects = this.projects
        .map(p => {
          const list = tasksByProject[p.id] || []
          const open = list.filter(t => t.status !== 'done').length
          const done = list.filter(t => t.status === 'done').length
          const progress = list.length
            ? Math.round((done / list.length) * 100)
            : 0
          return { id: p.id, name: p.name, open, done, progress }
        })
        .sort((a, b) => b.open - a.open)
        .slice(0, 5)

      this.weeklyDone = (() => {
        const weeks = this.weeksRange(12)
        return weeks.map(start => {
          const end = endOfWeek(start, { weekStartsOn: 1 })
          const label = format(start, 'dd.MM')
          const count = doneTasks.filter(t => {
            const completed = t.completed_at ? new Date(t.completed_at) : null
            return completed && completed >= start && completed <= end
          }).length
          return { label, count }
        })
      })()

      this.cfd = (() => {
        const weeks = this.weeksRange(12)
        return weeks.map(start => {
          const end = endOfWeek(start, { weekStartsOn: 1 })
          const row = { week: format(start, 'dd.MM'), todo: 0, in_progress: 0, review: 0, done: 0 }
          this.tasks.forEach(t => {
            const created = t.created_at ? new Date(t.created_at) : null
            if (created && created <= end) {
              const st = t.status || 'todo'
              if (row[st] === undefined) row[st] = 0
              row[st]++
            }
          })
          return row
        })
      })()

      this.kpis = [
        { label: 'Проекты (всего)', value: projectsTotal },
        {
          label: 'Проекты выполнены %',
          value: projectsTotal ? `${doneProjectsPct}%` : '—',
        },
        { label: 'Выполнено задач', value: doneTasksCount },
        { label: 'Задачи просрочены', value: overdueTasks },
        {
          label: 'В срок (%)',
          value: tasksWithDue.length ? `${tasksOnTimePct}%` : '—',
        },
        {
          label: 'Средний прогресс проектов (%)',
          value: progressArr.length ? `${avgProjectProgress}%` : '—',
        },
        {
          label: 'Среднее время выполнения задачи (ч)',
          value: doneTasksCount ? avgTaskDuration.toFixed(1) : '—',
        },
      ]
    },
  },
  mounted() {
    this.loadData()
  },
}
</script>

<style scoped>
.progress-sm {
  height: 6px;
}
</style>

