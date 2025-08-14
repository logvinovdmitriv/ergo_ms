<template>
  <div class="projects-list">
    <div class="pm-page-header" v-if="!managementMode">
      <h2><i class="fas fa-folder-open me-2"></i>Мои проекты</h2>
    </div>
    <!-- В режиме управления заголовок и кнопка создания показываются в родительском компоненте -->

    <!-- Фильтры и поиск -->
    <div class="pm-filters-card">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label"><i class="fas fa-search me-1"></i>Поиск</label>
            <input type="text" class="form-control" v-model="filters.search" @input="debouncedSearch"
                   placeholder="Поиск по названию...">
          </div>
          <div class="col-md-2">
            <label class="form-label">Статус</label>
            <select class="form-select" v-model="filters.status" @change="loadProjects" :disabled="loadingStatuses">
              <option value="">Все статусы</option>
              <option v-if="loadingStatuses">Загрузка...</option>
              <option v-else v-for="status in projectStatuses" :key="status.id" :value="status.code">
                {{ status.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Приоритет</label>
            <select class="form-select" v-model="filters.priority" @change="loadProjects" :disabled="loadingStatuses">
              <option value="">Все приоритеты</option>
              <option v-if="loadingStatuses">Загрузка...</option>
              <option v-else v-for="priority in projectPriorities" :key="priority.id" :value="priority.code">
                {{ priority.name }}
              </option>
            </select>
          </div>
          <div class="col-md-5">
            <label class="form-label">Сортировка</label>
            <select class="form-select" v-model="filters.ordering" @change="loadProjects">
              <option value="-created_at">По дате создания ↓</option>
              <option value="created_at">По дате создания ↑</option>
              <option value="name">По названию ↑</option>
              <option value="-name">По названию ↓</option>
              <option value="start_date">По дате начала ↑</option>
              <option value="-start_date">По дате начала ↓</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Список проектов -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="text-muted mt-3">Загружаем проекты...</p>
    </div>

    <div v-else-if="projects.length === 0" class="empty-state">
      <div class="text-center">
        <i class="fas fa-folder-open fa-5x text-muted mb-4"></i>
        <h4 class="text-muted mb-3">Проекты не найдены</h4>
        <p class="text-muted mb-4" v-if="!managementMode">Попробуйте изменить фильтры</p>
        <p class="text-muted mb-4" v-else>Попробуйте изменить фильтры или создайте новый проект</p>
        <button v-if="managementMode" class="btn btn-primary btn-lg rounded-pill" @click="createProject">
          <i class="fas fa-plus me-2"></i>Создать проект
        </button>
      </div>
    </div>

    <div v-else>
      <BulkActionsBar
        entity="project"
        :visible="selectedItems.length > 0"
        :selectedCount="selectedItems.length"
        :loading="isBulkActionLoading"
        :statuses="projectStatuses"
        :loadingDictionaries="loadingStatuses"
        @change-status="bulkChangeStatus"
        @delete-selected="confirmBulkDelete"
        @clear-selection="clearSelection"
      />
      <div class="form-check mb-2">
        <input class="form-check-input" type="checkbox" :checked="areAllSelected" @change="toggleSelectAll" id="selectAllProjects">
        <label class="form-check-label" for="selectAllProjects">Выбрать все</label>
      </div>

      <div class="row g-4">
        <div class="col-md-6 col-lg-4" v-for="project in projects" :key="project?.id">
          <div class="project-card h-100 pm-fade-in position-relative" v-if="project">
            <div class="form-check position-absolute top-0 start-0 m-2">
              <input class="form-check-input" type="checkbox" v-model="selectedItems" :value="project.id" @click.stop>
            </div>

            <div class="project-header" :style="{ borderColor: project.color }">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <span class="badge rounded-pill" :class="getStatusClass(project.status)">
                  {{ getStatusText(project.status) }}
                </span>
                <span class="badge rounded-pill" :class="getPriorityClass(project.priority)">
                  {{ getPriorityText(project.priority) }}
                </span>
              </div>
              <h5 class="project-title mb-0">{{ project.name || 'Без названия' }}</h5>
            </div>

            <div class="project-body">
              <p class="project-description">{{ project.description || 'Нет описания' }}</p>

              <!-- Прогресс -->
              <div class="progress-section">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="text-muted small">Прогресс выполнения</span>
                  <span class="progress-value">{{ project.progress || 0 }}%</span>
                </div>
                <div class="pm-progress">
                  <div class="progress-bar"
                       :style="{ width: (project.progress || 0) + '%' }"
                       :class="getProgressClass(project.progress || 0)">
                  </div>
                </div>
              </div>

              <!-- Статистика -->
              <div class="project-stats">
                <div class="stat-item">
                  <i class="fas fa-tasks text-primary"></i>
                  <div class="stat-content">
                    <div class="stat-value">{{ project.task_count || 0 }}</div>
                    <div class="stat-label">Задач</div>
                  </div>
                </div>
                <div class="stat-item">
                  <i class="fas fa-check-circle text-success"></i>
                  <div class="stat-content">
                    <div class="stat-value">{{ project.completed_task_count || 0 }}</div>
                    <div class="stat-label">Готово</div>
                  </div>
                </div>
                <div class="stat-item">
                  <i class="fas fa-clock text-warning"></i>
                  <div class="stat-content">
                    <div class="stat-value">{{ (project.task_count || 0) - (project.completed_task_count || 0) }}</div>
                    <div class="stat-label">В работе</div>
                  </div>
                </div>
              </div>

              <!-- Команда -->
              <div class="team-section" v-if="project.memberships && project.memberships.length > 0">
                <p class="text-muted small mb-2">Команда проекта:</p>
                <div class="team-avatars">
                  <img v-for="member in project.memberships.slice(0, 4)"
                       :key="member.user?.id"
                       :src="getAvatarUrl(member.user)"
                       :alt="member.user?.full_name"
                       class="pm-avatar"
                       :title="member.user?.full_name" />
                  <span v-if="project.memberships.length > 4" class="avatar-more">
                    +{{ project.memberships.length - 4 }}
                  </span>
                </div>
              </div>

              <!-- Даты -->
              <div class="project-dates" v-if="project.start_date || project.end_date">
                <i class="fas fa-calendar-alt text-muted me-2"></i>
                <small class="text-muted">{{ formatDateRange(project.start_date, project.end_date) }}</small>
              </div>
            </div>

            <div class="project-footer">
              <router-link :to="{ path: `/crm/project-management/project/${project.id}`, query: getProjectLinkQuery() }"
                           class="btn btn-open-project">
                <i class="fas fa-eye me-2"></i>Открыть проект
              </router-link>
              <div v-if="managementMode" class="project-actions">
                <button class="btn btn-edit-icon" @click="editProject(project)" title="Редактировать проект">
                  <Edit />
                </button>
                <button class="btn btn-delete-icon" @click="deleteProject(project)" title="Удалить проект">
                  <Trash2 />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div> <!-- ⬅️ закрываем .row g-4 -->
    </div> <!-- ⬅️ закрываем v-else -->

    <!-- Пагинация -->
    <nav v-if="pagination.total_pages > 1" class="mt-5">
      <ul class="pagination pagination-modern justify-content-center">
        <li class="page-item" :class="{ disabled: !pagination.previous }">
          <button class="page-link" @click="changePage(pagination.current_page - 1)"
                  :disabled="!pagination.previous">
            <i class="fas fa-chevron-left"></i>
          </button>
        </li>

        <li class="page-item"
            v-for="page in getPageNumbers()"
            :key="page"
            :class="{ active: page === pagination.current_page }">
          <button class="page-link" @click="changePage(page)">{{ page }}</button>
        </li>

        <li class="page-item" :class="{ disabled: !pagination.next }">
          <button class="page-link" @click="changePage(pagination.current_page + 1)"
                  :disabled="!pagination.next">
            <i class="fas fa-chevron-right"></i>
          </button>
        </li>
      </ul>
    </nav>

    <!-- Модальное окно создания/редактирования проекта (только в режиме управления) -->
    <div v-if="managementMode" class="modal fade" id="projectModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content border-0">
          <div class="modal-header border-bottom">
            <h5 class="modal-title">
              <i class="fas fa-folder me-2"></i>
              {{ isEditing ? 'Редактировать проект' : 'Создать проект' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <form @submit.prevent="submitProject">
              <div class="mb-4">
                <label class="form-label fw-bold">Название проекта <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentProject.name" required
                       placeholder="Введите название проекта">
              </div>
              <div class="mb-4">
                <label class="form-label fw-bold">Описание</label>
                <textarea class="form-control" rows="3" v-model="currentProject.description"
                          placeholder="Опишите цели и задачи проекта"></textarea>
              </div>
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label fw-bold">Дата начала</label>
                  <input type="date" class="form-control" v-model="currentProject.start_date">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Дата окончания</label>
                  <input type="date" class="form-control" v-model="currentProject.end_date">
                </div>
              </div>
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label fw-bold">Статус</label>
                  <select class="form-select" v-model="currentProject.status" :disabled="loadingStatuses">
                    <option v-if="loadingStatuses">Загрузка...</option>
                    <option v-else v-for="status in projectStatuses" :key="status.id" :value="status.code">
                      {{ status.name }}
                    </option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Приоритет</label>
                  <select class="form-select" v-model="currentProject.priority" :disabled="loadingStatuses">
                    <option v-if="loadingStatuses">Загрузка...</option>
                    <option v-else v-for="priority in projectPriorities" :key="priority.id" :value="priority.code">
                      {{ priority.name }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label fw-bold">Организация</label>
                  <select class="form-select"
                          v-model="currentProject.organization_id"
                          :disabled="loadingOrganizations">
                    <option :value="null">—</option>
                    <option v-if="loadingOrganizations">Загрузка...</option>
                    <option v-else v-for="org in organizations" :key="org.id" :value="org.id">
                      {{ org.name }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="mb-4">
                <label class="form-label fw-bold">Цвет проекта</label>
                <div class="d-flex align-items-center gap-2">
                  <input type="color" class="form-control form-control-color" v-model="currentProject.color">
                  <span class="text-muted">Выберите цвет для визуального выделения</span>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer border-top">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Отменить</button>
            <button type="button" class="btn btn-primary" @click="submitProject" :disabled="!currentProject.name">
              <i class="fas fa-save me-2"></i>{{ isEditing ? 'Сохранить' : 'Создать' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap'
import Dropdown from 'bootstrap/js/dist/dropdown'
import { Edit, Trash2 } from 'lucide-vue-next'
import projectManagementApi from '@/modules/crm/project-management/js/projectManagementApi.js'
import { useNotifications } from '@/modules/lms/composables/useNotifications'
import { getAvatarUrl } from '@/modules/cms/js/avatarUtils.js'
import OrganizationApi from '@/modules/crm/organizations/js/organizationApi.js'
import BulkActionsBar from './components/BulkActionsBar.vue'

export default {
  name: 'ProjectsList',
  components: {
    Edit,
    Trash2,
    BulkActionsBar
  },
  props: {
    managementMode: { type: Boolean, default: false }
  },
  setup() {
    const { showSuccess, showError, showConfirmDialog, closeConfirmDialog } = useNotifications()
    return { showSuccess, showError, showConfirmDialog, closeConfirmDialog }
  },
  data() {
    return {
      projects: [],
      loading: false,
      filters: { search: '', status: '', priority: '', ordering: '-created_at' },
      pagination: { current_page: 1, total_pages: 1, previous: null, next: null, count: 0 },
      currentProject: {
        name: '', description: '', start_date: '', end_date: '',
        status: 'planning', priority: 'medium', color: '#007bff', organization_id: null
      },
      isEditing: false,
      searchTimeout: null,
      projectStatuses: [],
      projectPriorities: [],
      loadingStatuses: false,
      organizations: [],
      loadingOrganizations: false,
      selectedItems: [],
      isBulkActionLoading: false
    }
  },
  async mounted() {
    this.loadProjects()
    this.loadStatusesAndPriorities()
  },
  computed: {
    debouncedSearch() {
      return () => {
        clearTimeout(this.searchTimeout)
        this.searchTimeout = setTimeout(() => {
          this.pagination.current_page = 1
          this.loadProjects()
        }, 500)
      }
    },
    areAllSelected() {
      return this.projects.length > 0 && this.selectedItems.length === this.projects.length
    }
  },
  methods: {
    toggleSelectAll(e) { this.selectedItems = e.target.checked ? this.projects.map(p => p.id) : [] },
    clearSelection() { this.selectedItems = [] },

    async confirmBulkDelete() {
      if (!this.selectedItems.length) return
      if (!confirm('Удалить выбранные проекты?')) return
      this.isBulkActionLoading = true
      try {
        await projectManagementApi.bulkDeleteProjects(this.selectedItems)
        this.showSuccess('Проекты удалены')
        await this.loadProjects()
        this.clearSelection()
      } catch (e) {
        console.error('Ошибка массового удаления проектов:', e)
        this.showError('Не удалось удалить проекты')
      } finally { this.isBulkActionLoading = false }
    },

    async bulkChangeStatus(status) {
      if (!this.selectedItems.length) return
      this.isBulkActionLoading = true
      try {
        await projectManagementApi.bulkUpdateProjects({ ids: this.selectedItems, status })
        this.showSuccess('Статус проектов обновлен')
        await this.loadProjects()
        this.clearSelection()
      } catch (e) {
        console.error('Ошибка массового обновления проектов:', e)
        this.showError('Не удалось обновить проекты')
      } finally { this.isBulkActionLoading = false }
    },

    async loadProjects() {
      this.loading = true
      try {
        const params = { page: this.pagination.current_page, page_size: 12, ...this.filters }
        Object.keys(params).forEach(k => { if (params[k] === '' || params[k] === false) delete params[k] })
        const res = await projectManagementApi.getProjects(params)
        if (res.data.results) {
          this.projects = res.data.results
          this.pagination = {
            current_page: res.data.current_page || 1,
            total_pages: res.data.total_pages || 1,
            previous: res.data.previous, next: res.data.next,
            count: res.data.count || 0
          }
        } else {
          this.projects = Array.isArray(res.data) ? res.data : []
        }
        this.selectedItems = []
      } catch (e) {
        console.error('Ошибка загрузки проектов:', e)
        this.projects = []
      } finally { this.loading = false }
    },

    async loadStatusesAndPriorities() {
      try {
        this.loadingStatuses = true
        const [st, pr] = await Promise.all([
          projectManagementApi.getProjectStatuses(),
          projectManagementApi.getProjectPriorities()
        ])
        this.projectStatuses = Array.isArray(st.data)
          ? st.data.filter(s => s.is_active)
          : (st.data.results || []).filter(s => s.is_active)
        this.projectPriorities = Array.isArray(pr.data)
          ? pr.data.filter(p => p.is_active)
          : (pr.data.results || []).filter(p => p.is_active)

        const defS = this.projectStatuses.find(s => s.is_default)
        const defP = this.projectPriorities.find(p => p.is_default)
        if (defS && !this.isEditing) this.currentProject.status = defS.code
        if (defP && !this.isEditing) this.currentProject.priority = defP.code
      } catch (e) {
        console.error('Ошибка загрузки статусов и приоритетов:', e)
        this.projectStatuses = [
          { id: 1, name: 'Планирование', code: 'planning' },
          { id: 2, name: 'Активный', code: 'active' },
          { id: 3, name: 'Приостановлен', code: 'on_hold' },
          { id: 4, name: 'Завершен', code: 'completed' },
          { id: 5, name: 'Отменен', code: 'cancelled' }
        ]
        this.projectPriorities = [
          { id: 1, name: 'Низкий', code: 'low' },
          { id: 2, name: 'Средний', code: 'medium' },
          { id: 3, name: 'Высокий', code: 'high' },
          { id: 4, name: 'Срочный', code: 'urgent' }
        ]
      } finally { this.loadingStatuses = false }
    },

    async loadOrganizations() {
      this.loadingOrganizations = true
      try {
        const res = await OrganizationApi.getMyOrganizations()
        const data = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
        this.organizations = data
      } catch (e) {
        console.error('Ошибка загрузки организаций:', e)
        alert(e?.response?.data?.detail || 'Ошибка')
        this.organizations = []
      } finally { this.loadingOrganizations = false }
    },

    changePage(page) {
      if (page >= 1 && page <= this.pagination.total_pages) {
        this.pagination.current_page = page
        this.loadProjects()
      }
    },

    async refreshStatusesAndPriorities() { await this.loadStatusesAndPriorities() },

    getPageNumbers() {
      const pages = []
      for (let i = Math.max(1, this.pagination.current_page - 2);
           i <= Math.min(this.pagination.total_pages, this.pagination.current_page + 2); i++) pages.push(i)
      return pages
    },

    async createProject() {
      this.isEditing = false
      await this.refreshStatusesAndPriorities()
      await this.loadOrganizations()
      const defS = this.projectStatuses.find(s => s.is_default) || this.projectStatuses[0]
      const defP = this.projectPriorities.find(p => p.is_default) || this.projectPriorities[0]
      this.currentProject = {
        name: '', description: '', start_date: '', end_date: '',
        status: defS ? defS.code : 'planning',
        priority: defP ? defP.code : 'medium',
        color: '#007bff', organization_id: null
      }
      const modal = new Modal(document.getElementById('projectModal'))
      modal.show()
    },

    async editProject(project) {
      this.isEditing = true
      await this.loadOrganizations()
      this.currentProject = {
        id: project.id,
        name: project.name,
        description: project.description,
        start_date: project.start_date,
        end_date: project.end_date,
        status: project.status,
        priority: project.priority,
        color: project.color,
        organization_id: project.organization?.id ?? null
      }
      const modal = new Modal(document.getElementById('projectModal'))
      modal.show()
    },

    async submitProject() {
      try {
        const payload = {
          ...this.currentProject,
          start_date: this.currentProject.start_date || null,
          end_date: this.currentProject.end_date || null,
          organization_id: this.currentProject.organization_id ?? null
        }
        if (this.isEditing) await projectManagementApi.updateProject(payload.id, payload)
        else await projectManagementApi.createProject(payload)

        Modal.getInstance(document.getElementById('projectModal')).hide()
        this.loadProjects()
        this.showSuccess(this.isEditing ? 'Проект обновлен' : 'Проект создан')
      } catch (e) {
        console.error('Ошибка сохранения проекта:', e)
        this.showError('Ошибка сохранения проекта')
      }
    },

    deleteProject(project) { this.currentProject = project; this.confirmDeleteProject() },

    async confirmDeleteProject() {
      const confirmed = await this.showConfirmDialog({
        title: 'Удаление проекта',
        message: `Вы уверены, что хотите удалить проект "${this.currentProject.name}"?`,
        confirmText: 'Удалить', cancelText: 'Отмена', variant: 'danger'
      })
      if (!confirmed) return
      try {
        await projectManagementApi.deleteProject(this.currentProject.id)
        const modal = Modal.getInstance(document.getElementById('projectModal'))
        if (modal) modal.hide()
        this.closeConfirmDialog()
        this.loadProjects()
        this.showSuccess('Проект удален')
      } catch (e) {
        console.error('Ошибка удаления проекта:', e)
        this.closeConfirmDialog()
        this.showError('Ошибка удаления проекта')
      }
    },

    getStatusClass(s) {
      const map = { planning: 'bg-secondary', active: 'bg-success', on_hold: 'bg-warning text-dark', completed: 'bg-primary', cancelled: 'bg-danger' }
      return map[s] || 'bg-secondary'
    },
    getStatusText(s) { return (this.projectStatuses.find(x => x.code === s) || {}).name || s },
    getPriorityClass(p) {
      const map = { low: 'bg-light text-dark', medium: 'bg-info', high: 'bg-warning text-dark', urgent: 'bg-danger' }
      return map[p] || 'bg-light text-dark'
    },
    getPriorityText(p) { return (this.projectPriorities.find(x => x.code === p) || {}).name || p },
    getProgressClass(p) { if (p >= 80) return 'bg-success'; if (p >= 50) return 'bg-warning'; return 'bg-danger' },

    formatDateRange(start, end) {
      const fmt = d => (d ? new Date(d).toLocaleDateString('ru-RU') : null)
      const s = fmt(start), e = fmt(end)
      if (s && e) return `${s} - ${e}`
      if (s) return `с ${s}`
      if (e) return `до ${e}`
      return 'Даты не указаны'
    },

    getAvatarUrl(user) { return getAvatarUrl(user, 32) },

    getProjectLinkQuery() { return this.managementMode ? { from: 'management' } : {} }
  }
}
</script>

<style scoped lang="scss">
@import './project-management.scss';

.projects-list {
  padding: 20px;
  min-height: 100vh;
  background: var(--bs-gray-100);
}

.empty-state {
  padding: 4rem 2rem;
  background: white;
  border-radius: $radius-usual;
  box-shadow: $pm-card-shadow;
  margin-top: 2rem;
}

.project-card {
  @include pm-card;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;

  .project-header {
    padding: 1.5rem;
    background: var(--bs-light);
    border-left: 4px solid;

    .project-title {
      font-size: $font-size-h3;
      font-weight: $font-weight-bold;
      color: var(--bs-heading-color);
      margin-bottom: 0;
    }
  }

  .project-body {
    padding: 1.5rem;
    flex: 1;
    display: flex;
    flex-direction: column;

    .project-description {
      font-size: $font-size-small;
      color: var(--bs-secondary-color);
      margin-bottom: 1.5rem;
      line-height: 1.6;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .progress-section {
      margin-bottom: 1.5rem;

      .progress-value {
        font-weight: $font-weight-bold;
        color: var(--bs-primary);
      }

      // Дополнительные стили для прогресс-бара
      .pm-progress {
        height: 6px;
        background: #e9ecef;
        border-radius: 3px;
        overflow: hidden;
        position: relative;

        .progress-bar {
          height: 100%;
          transition: width 0.3s ease;
          border-radius: 3px;
          position: relative;

          &.bg-success {
            background-color: #28a745 !important;
          }

          &.bg-warning {
            background-color: #ffc107 !important;
          }

          &.bg-danger {
            background-color: #dc3545 !important;
          }

          // Если класс не установлен, используем primary цвет
          &:not(.bg-success):not(.bg-warning):not(.bg-danger) {
            background-color: #007bff !important;
          }
        }
      }
    }

    .project-stats {
      display: flex;
      justify-content: space-around;
      padding: 1rem 0;
      margin-bottom: 1.5rem;
      border-top: 1px solid var(--bs-border-color);
      border-bottom: 1px solid var(--bs-border-color);

      .stat-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;

        i {
          font-size: 1.25rem;
        }

        .stat-content {
          text-align: left;

          .stat-value {
            font-size: 1.25rem;
            font-weight: $font-weight-bold;
            line-height: 1;
          }

          .stat-label {
            font-size: $font-size-micro;
            color: var(--bs-secondary-color);
          }
        }
      }
    }

    .team-section {
      margin-bottom: 1rem;

      .team-avatars {
        display: flex;
        align-items: center;

        .avatar-more {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          background: var(--bs-light);
          border-radius: 50%;
          font-size: $font-size-micro;
          font-weight: $font-weight-bold;
          color: var(--bs-secondary-color);
          margin-left: -8px;
          border: 2px solid var(--bs-card-bg);
        }
      }
    }

    .project-dates {
      margin-top: auto;
      font-size: $font-size-small;
      color: var(--bs-secondary-color);
    }
  }

  .project-footer {
    padding: 1rem 1.5rem;
    background: var(--bs-gray-100);
    border-top: 1px solid var(--bs-border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;

    .project-actions {
      display: flex;
      gap: 0.5rem;
    }

    // Кнопка "Открыть проект" - прямоугольная с закругленными концами
    .btn-open-project {
      display: inline-flex;
      align-items: center;
      padding: 0.5rem 1rem;
      background: #dc3545;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 0.875rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.3s ease;
      box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);

      &:hover {
        background: #c82333;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.4);
        text-decoration: none;
      }

      &:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
      }

      i {
        color: white;
        transition: transform 0.3s ease;
      }

      &:hover i {
        transform: translateX(2px);
      }
    }
  }
}

.badge {
  @include pm-badge;
}

.btn {
  @include pm-button;
}

// Пагинация
.pagination-modern {
  .page-item {
    margin: 0 2px;

    &:first-child .page-link {
      border-radius: $radius-small 0 0 $radius-small;
    }

    &:last-child .page-link {
      border-radius: 0 $radius-small $radius-small 0;
    }
  }

  .page-link {
    border: none;
    background: white;
    color: var(--bs-secondary-color);
    padding: 0.5rem 1rem;
    font-weight: $font-weight-bold;
    box-shadow: $pm-card-shadow;
    transition: all $pm-transition;

    &:hover {
      background: var(--bs-primary);
      color: white;
      transform: translateY(-2px);
      box-shadow: $pm-card-hover-shadow;
    }

    &:focus {
      box-shadow: 0 0 0 0.2rem rgba($primary, 0.25);
    }
  }

  .page-item.active .page-link {
    background: var(--bs-primary);
    color: white;
  }

  .page-item.disabled .page-link {
    background: var(--bs-gray-200);
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// Модальное окно
.modal-content {
  border-radius: $radius-usual;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.modal-header {
  background: var(--bs-light);
  padding: 1.5rem;

  .modal-title {
    font-size: $font-size-h3;
    font-weight: $font-weight-bold;
    color: var(--bs-heading-color);
  }
}

.form-label {
  color: var(--bs-secondary-color);
  font-size: $font-size-small;
  margin-bottom: 0.5rem;
}

.form-control,
.form-select {
  border-radius: $radius-small;
  border-color: var(--bs-border-color);

  &:focus {
    border-color: var(--bs-primary);
    box-shadow: 0 0 0 0.2rem rgba($primary, 0.25);
  }
}

.form-control-color {
  width: 50px;
  height: 38px;
  cursor: pointer;
  border-radius: $radius-small;
}

// Адаптивность
@media (max-width: 768px) {
  .projects-list {
    padding: 1rem;
  }

  .pm-page-header {
    flex-direction: column;
    gap: 1rem;

    h2 {
      font-size: $font-size-h2;
    }
  }

  .project-card {
    .project-stats {
      .stat-item {
        flex-direction: column;
        text-align: center;

        .stat-content {
          text-align: center;
        }
      }
    }
  }
}
</style>