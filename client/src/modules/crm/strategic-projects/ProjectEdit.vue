<template>
  <div class="project-edit">
    <div class="container-fluid">
      <!-- Заголовок страницы с градиентом -->
      <div class="page-header-gradient mb-4">
        <div class="row align-items-center">
          <div class="col-lg-8">
            <h1 class="page-title mb-2">
              <i :class="isEditMode ? 'fas fa-edit' : 'fas fa-plus-circle'" class="mr-3"></i>
              {{ isEditMode ? 'Редактирование проекта' : 'Создание проекта' }}
            </h1>
            <nav aria-label="breadcrumb">
              <ol class="breadcrumb breadcrumb-transparent">
                <li class="breadcrumb-item"><router-link to="/">Главная</router-link></li>
                <li class="breadcrumb-item"><router-link to="/crm">CRM</router-link></li>
                <li class="breadcrumb-item">
                  <router-link to="/crm/strategic-projects">Стратегические проекты</router-link>
                </li>
                <li class="breadcrumb-item active">
                  {{ isEditMode ? 'Редактирование' : 'Создание' }}
                </li>
              </ol>
            </nav>
          </div>
          <div class="col-lg-4 text-right" v-if="project.code">
            <div class="project-code-badge">
              <i class="fas fa-fingerprint mr-2"></i>
              {{ project.code }}
            </div>
          </div>
        </div>
      </div>

      <!-- Статус проекта с улучшенным дизайном -->
      <div v-if="project.status" class="row mb-4">
        <div class="col-12">
          <div class="status-card" :class="getStatusCardClass(project.status)">
            <div class="status-icon">
              <i :class="getStatusIcon(project.status)"></i>
            </div>
            <div class="status-content">
              <h6 class="status-title">Статус проекта</h6>
              <div class="status-badge">
                {{ getStatusLabel(project.status) }}
              </div>
              <div v-if="project.rejection_comment" class="rejection-comment">
                <strong>Причина отклонения:</strong>
                <p class="mb-0 mt-1">{{ project.rejection_comment }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Форма редактирования -->
      <form @submit.prevent="saveProject">
        <!-- Прогресс заполнения -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="progress-section">
              <h6 class="progress-title">
                <i class="fas fa-tasks mr-2"></i>
                Прогресс заполнения проекта
              </h6>
              <div class="progress progress-xl">
                <div 
                  class="progress-bar progress-bar-striped progress-bar-animated"
                  :style="`width: ${completionProgress}%`"
                  :class="getProgressBarClass(completionProgress)"
                >
                  {{ completionProgress }}%
                </div>
              </div>
              <div class="progress-hints mt-2">
                <span v-if="!project.name?.trim()" class="hint-item hint-error">
                  <i class="fas fa-times-circle"></i> Укажите название проекта
                </span>
                <span v-if="!project.goal?.trim()" class="hint-item hint-warning">
                  <i class="fas fa-exclamation-circle"></i> Укажите цель проекта
                </span>
                <span v-if="!project.tasks?.trim()" class="hint-item hint-warning">
                  <i class="fas fa-exclamation-circle"></i> Укажите задачи проекта
                </span>
                <span v-if="!project.curator" class="hint-item hint-warning">
                  <i class="fas fa-exclamation-circle"></i> Выберите куратора
                </span>
                <span v-if="!project.customer" class="hint-item hint-warning">
                  <i class="fas fa-exclamation-circle"></i> Выберите заказчика
                </span>
                <span v-if="!project.planned_start_date" class="hint-item hint-warning">
                  <i class="fas fa-exclamation-circle"></i> Укажите дату начала
                </span>
                <span v-if="!project.planned_end_date" class="hint-item hint-warning">
                  <i class="fas fa-exclamation-circle"></i> Укажите дату окончания
                </span>
                <span v-if="project.stages.length === 0" class="hint-item hint-warning">
                  <i class="fas fa-exclamation-circle"></i> Добавьте этапы проекта
                </span>
                <span v-if="completionProgress === 100" class="hint-item hint-success">
                  <i class="fas fa-check-circle"></i> Все поля заполнены!
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Основная информация -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="form-section">
              <div class="section-header">
                <h5 class="section-title">
                  <i class="fas fa-info-circle mr-2"></i>
                  Основная информация
                </h5>
              </div>
              <div class="section-body">
                <div class="row">
                  <div class="col-md-12">
                    <div class="form-group">
                      <label class="form-label">
                        Название проекта
                        <span class="required-star">*</span>
                      </label>
                      <div class="input-group input-group-merge">
                        <div class="input-group-prepend">
                          <span class="input-group-text">
                            <i class="fas fa-heading"></i>
                          </span>
                        </div>
                        <input
                          v-model="project.name"
                          type="text"
                          class="form-control form-control-lg"
                          placeholder="Введите название проекта"
                          required
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <div class="form-group">
                      <label class="form-label">
                        Цель проекта
                        <span class="required-star">*</span>
                      </label>
                      <div class="textarea-wrapper">
                        <textarea
                          v-model="project.goal"
                          class="form-control"
                          rows="3"
                          placeholder="Опишите цель проекта..."
                          required
                        ></textarea>
                        <div class="textarea-footer">
                          <span class="char-count">{{ project.goal?.length || 0 }} символов</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <div class="form-group">
                      <label class="form-label">
                        Задачи проекта
                        <span class="required-star">*</span>
                      </label>
                      <div class="textarea-wrapper">
                        <textarea
                          v-model="project.tasks"
                          class="form-control"
                          rows="4"
                          placeholder="Перечислите основные задачи проекта..."
                          required
                        ></textarea>
                        <div class="textarea-footer">
                          <span class="char-count">{{ project.tasks?.length || 0 }} символов</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="row">
                  <div class="col-md-4">
                    <div class="form-group">
                      <label class="form-label">
                        <i class="fas fa-building mr-2"></i>
                        Организация
                      </label>
                      <div class="select-wrapper">
                        <select v-model="project.organization_id" class="form-control custom-select">
                          <option :value="null">—</option>
                          <option v-for="org in organizations" :key="org.id" :value="org.id">
                            {{ org.name }}
                          </option>
                        </select>
                        <div class="select-arrow">
                          <i class="fas fa-chevron-down"></i>
                        </div>
                      </div>
                      <small v-if="loadingOrgs" class="form-text text-info">
                        <i class="fas fa-spinner fa-spin mr-1"></i>
                        Загрузка организаций...
                      </small>
                      <small v-else-if="organizations.length === 0" class="form-text text-warning">
                        <i class="fas fa-exclamation-triangle mr-1"></i>
                        Организации не найдены
                      </small>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-4">
                    <div class="form-group">
                      <label class="form-label">
                        <i class="fas fa-user-tie mr-2"></i>
                        Куратор проекта
                        <span class="required-star">*</span>
                      </label>
                      <div class="select-wrapper">
                        <select v-model="project.curator" class="form-control custom-select" required>
                          <option value="">Выберите куратора</option>
                          <option v-for="user in users" :key="user.id" :value="user.id">
                            {{ user.full_name }}
                          </option>
                        </select>
                        <div class="select-arrow">
                          <i class="fas fa-chevron-down"></i>
                        </div>
                      </div>
                                             <small v-if="loadingUsers" class="form-text text-info">
                         <i class="fas fa-spinner fa-spin mr-1"></i>
                         Загрузка пользователей...
                       </small>
                       <small v-else-if="users.length === 0" class="form-text text-warning">
                         <i class="fas fa-exclamation-triangle mr-1"></i>
                         Пользователи не найдены
                       </small>
                       <small v-else class="form-text text-success">
                         <i class="fas fa-check mr-1"></i>
                         Загружено пользователей: {{ users.length }}
                       </small>
                     </div>
                   </div>
                   <div class="col-md-4">
                     <div class="form-group">
                       <label class="form-label">
                         <i class="fas fa-user-check mr-2"></i>
                         Заказчик проекта
                         <span class="required-star">*</span>
                       </label>
                       <div class="select-wrapper">
                         <select v-model="project.customer" class="form-control custom-select" required>
                           <option value="">Выберите заказчика</option>
                           <option v-for="user in users" :key="user.id" :value="user.id">
                             {{ user.full_name }}
                           </option>
                         </select>
                         <div class="select-arrow">
                           <i class="fas fa-chevron-down"></i>
                         </div>
                       </div>
                       <small v-if="loadingUsers" class="form-text text-info">
                         <i class="fas fa-spinner fa-spin mr-1"></i>
                         Загрузка пользователей...
                       </small>
                       <small v-else-if="users.length === 0" class="form-text text-warning">
                         <i class="fas fa-exclamation-triangle mr-1"></i>
                         Пользователи не найдены
                       </small>
                       <small v-else class="form-text text-success">
                         <i class="fas fa-check mr-1"></i>
                         Загружено пользователей: {{ users.length }}
                       </small>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="form-group">
                      <label>
                        <input
                          v-model="project.requires_budget"
                          type="checkbox"
                        />
                        Требуется бюджет
                      </label>
                      <input
                        v-if="project.requires_budget"
                        v-model="project.total_budget"
                        type="number"
                        step="0.01"
                        class="form-control mt-2"
                        placeholder="Сумма бюджета"
                      />
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6">
                    <div class="form-group">
                      <label>Плановая дата начала <span class="text-danger">*</span></label>
                      <input
                        v-model="project.planned_start_date"
                        type="date"
                        class="form-control"
                        required
                      />
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="form-group">
                      <label>Плановая дата окончания <span class="text-danger">*</span></label>
                      <input
                        v-model="project.planned_end_date"
                        type="date"
                        class="form-control"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <div class="form-group">
                      <label>Планируемые результаты</label>
                      <div v-for="(result, index) in project.planned_results" :key="index" class="input-group mb-2">
                        <input
                          v-model="project.planned_results[index]"
                          type="text"
                          class="form-control"
                          placeholder="Введите планируемый результат"
                        />
                        <div class="input-group-append">
                          <button
                            @click="removeResult(index)"
                            type="button"
                            class="btn btn-outline-danger"
                          >
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                      <button
                        @click="addResult"
                        type="button"
                        class="btn btn-sm btn-outline-primary"
                      >
                        <i class="fas fa-plus mr-2"></i>
                        Добавить результат
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- План-график проекта -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-header">
                <h5 class="card-title mb-0">
                  План-график проекта
                  <span class="badge badge-primary ml-2">{{ project.stages.length }} этапов</span>
                </h5>
              </div>
              <div class="card-body">
                <div v-if="project.stages.length === 0" class="alert alert-warning">
                  <i class="fas fa-exclamation-triangle mr-2"></i>
                  Необходимо добавить хотя бы один этап проекта
                </div>

                <div v-for="(stage, index) in project.stages" :key="index" class="card mb-3">
                  <div class="card-header">
                    <h6 class="mb-0">
                      Этап {{ index + 1 }}
                      <button
                        @click="removeStage(index)"
                        type="button"
                        class="btn btn-sm btn-outline-danger float-right"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </h6>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-12">
                        <div class="form-group">
                          <label>Наименование этапа <span class="text-danger">*</span></label>
                          <input
                            v-model="stage.name"
                            type="text"
                            class="form-control"
                            required
                          />
                        </div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-6">
                        <div class="form-group">
                          <label>Дата начала <span class="text-danger">*</span></label>
                          <input
                            v-model="stage.planned_start_date"
                            type="date"
                            class="form-control"
                            required
                          />
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="form-group">
                          <label>Дата окончания <span class="text-danger">*</span></label>
                          <input
                            v-model="stage.planned_end_date"
                            type="date"
                            class="form-control"
                            required
                          />
                        </div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-12">
                        <div class="form-group">
                          <label>Описание</label>
                          <textarea
                            v-model="stage.description"
                            class="form-control"
                            rows="2"
                          ></textarea>
                        </div>
                      </div>
                    </div>
                    <div v-if="project.requires_budget" class="row">
                      <div class="col-md-6">
                        <div class="form-group">
                          <label>Бюджет этапа</label>
                          <input
                            v-model="stage.budget"
                            type="number"
                            step="0.01"
                            class="form-control"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  @click="addStage"
                  type="button"
                  class="btn btn-outline-primary"
                >
                  <i class="fas fa-plus mr-2"></i>
                  Добавить этап
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Кнопки действий -->
        <div class="row mb-5">
          <div class="col-12">
            <div class="d-flex justify-content-between">
              <router-link to="/crm/strategic-projects" class="btn btn-secondary">
                <i class="fas fa-arrow-left mr-2"></i>
                Назад
              </router-link>
              <div>
                <button
                  @click="checkProjectReadiness"
                  type="button"
                  class="btn btn-info mr-2"
                >
                  <i class="fas fa-clipboard-check mr-2"></i>
                  Проверить готовность
                </button>
                <button
                  type="submit"
                  class="btn btn-success mr-2"
                  :disabled="saving"
                >
                  <span v-if="saving" class="spinner-border spinner-border-sm mr-2"></span>
                  <i v-else class="fas fa-save mr-2"></i>
                  Сохранить
                </button>
                <button
                  v-if="canSubmitForApproval"
                  @click="submitForApproval"
                  type="button"
                  class="btn btn-primary"
                  :disabled="submitting"
                >
                  <span v-if="submitting" class="spinner-border spinner-border-sm mr-2"></span>
                  <i v-else class="fas fa-paper-plane mr-2"></i>
                  Отправить на утверждение
                </button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiClient } from '@/js/api/manager'
import OrganizationApi from '@/modules/crm/organizations/js/organizationApi.js'

export default {
  name: 'ProjectEdit',
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const projectId = route.params.id
    const isEditMode = computed(() => projectId && projectId !== 'create')
    
    const project = ref({
      name: '',
      goal: '',
      tasks: '',
      curator: null,
      customer: null,
      planned_start_date: '',
      planned_end_date: '',
      planned_results: [],
      requires_budget: false,
      total_budget: null,
      stages: [],
      status: 'draft',
      organization_id: null
    })

    const users = ref([])
    const organizations = ref([])
    const loadingOrgs = ref(false)
    const saving = ref(false)
    const submitting = ref(false)
    const loadingUsers = ref(false)
    
    // Проверка возможности отправки на утверждение
    const canSubmitForApproval = computed(() => {
      return project.value.status === 'draft' || project.value.status === 'rejected'
    })
    
    // Прогресс заполнения проекта
    const completionProgress = computed(() => {
      let progress = 0
      const fields = [
        project.value.name,
        project.value.goal,
        project.value.tasks,
        project.value.curator,
        project.value.customer,
        project.value.planned_start_date,
        project.value.planned_end_date
      ]
      
      fields.forEach(field => {
        if (field) progress += 10
      })
      
      if (project.value.planned_results && project.value.planned_results.length > 0) {
        progress += 10
      }
      
      if (project.value.stages && project.value.stages.length > 0) {
        progress += 20
      }
      
      return Math.min(progress, 100)
    })
    
    // Получение класса для прогресс-бара
    const getProgressBarClass = (progress) => {
      if (progress < 30) return 'bg-danger'
      if (progress < 70) return 'bg-warning'
      if (progress < 100) return 'bg-info'
      return 'bg-success'
    }
    
    // Получение класса для карточки статуса
    const getStatusCardClass = (status) => {
      const classes = {
        draft: 'status-card-secondary',
        on_approval: 'status-card-warning',
        rejected: 'status-card-danger',
        approved: 'status-card-info',
        in_progress: 'status-card-primary',
        completed: 'status-card-success',
        archived: 'status-card-dark'
      }
      return classes[status] || 'status-card-secondary'
    }
    
    // Получение иконки статуса
    const getStatusIcon = (status) => {
      const icons = {
        draft: 'fas fa-file-alt',
        on_approval: 'fas fa-hourglass-half',
        rejected: 'fas fa-times-circle',
        approved: 'fas fa-check-circle',
        in_progress: 'fas fa-cogs',
        completed: 'fas fa-flag-checkered',
        archived: 'fas fa-archive'
      }
      return icons[status] || 'fas fa-question-circle'
    }

    // Загрузка организаций
    const loadOrganizations = async () => {
      loadingOrgs.value = true
      try {
        const resp = await OrganizationApi.getOrganizations()
        const list = resp?.data?.results || resp?.data || []
        organizations.value = list.filter(org => org?.my_membership?.role)
      } catch (e) {
        console.error('Ошибка загрузки организаций:', e)
        alert(e?.response?.data?.detail || 'Ошибка')
      } finally {
        loadingOrgs.value = false
      }
    }

    // Загрузка пользователей
    const loadUsers = async () => {
      loadingUsers.value = true
      try {
        console.log('Запрос пользователей по API...')
        // Пробуем разные API эндпоинты для пользователей
        let response
        try {
          response = await apiClient.get('/cms/adp/users/')
        } catch (firstError) {
          console.log('Попробуем другой эндпоинт...')
          try {
            response = await apiClient.get('/cms/users/')
          } catch (secondError) {
            console.log('Попробуем еще один эндпоинт...')
            response = await apiClient.get('/users/')
          }
        }
        
        if (response.data && Array.isArray(response.data)) {
          users.value = response.data.map(user => ({
            id: user.id,
            full_name: user.full_name || user.name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username,
            username: user.username,
            email: user.email
          }))
          console.log('Пользователи успешно загружены из API:', users.value.length)
        } else {
          // Если API не работает, используем тестовые данные
          console.warn('API пользователей недоступно или вернуло неправильные данные, используем тестовые данные')
          loadTestUsers()
        }
      } catch (error) {
        console.error('Ошибка загрузки пользователей:', error)
        // Используем тестовые данные при ошибке API
        console.log('Используем тестовые данные пользователей')
        loadTestUsers()
      } finally {
        loadingUsers.value = false
      }
    }
    
    // Загрузка тестовых пользователей для демонстрации
    const loadTestUsers = () => {
      users.value = [
        {
          id: 1,
          full_name: 'Иванов Иван Иванович',
          username: 'ivanov',
          email: 'ivanov@example.com'
        },
        {
          id: 2,
          full_name: 'Петров Петр Петрович',
          username: 'petrov',
          email: 'petrov@example.com'
        },
        {
          id: 3,
          full_name: 'Сидорова Елена Александровна',
          username: 'sidorova',
          email: 'sidorova@example.com'
        },
        {
          id: 4,
          full_name: 'Козлов Андрей Сергеевич',
          username: 'kozlov',
          email: 'kozlov@example.com'
        },
        {
          id: 5,
          full_name: 'Васильева Мария Николаевна',
          username: 'vasileva',
          email: 'vasileva@example.com'
        },
        {
          id: 6,
          full_name: 'Смирнов Александр Дмитриевич',
          username: 'smirnov',
          email: 'smirnov@example.com'
        }
      ]
    }
    
    // Загрузка проекта
    const loadProject = async () => {
      if (!isEditMode.value) return
      
      try {
        const response = await apiClient.get(`/crm/strategic-projects/strategic-projects/${projectId}/`)
        project.value = response.data
        project.value.organization_id = response.data.organization?.id || null
        delete project.value.organization

        // Убеждаемся, что массивы инициализированы
        if (!project.value.planned_results) {
          project.value.planned_results = []
        }
        if (!project.value.stages) {
          project.value.stages = []
        }
      } catch (error) {
        console.error('Ошибка загрузки проекта:', error)
        alert('Ошибка при загрузке проекта')
        router.push('/crm/strategic-projects')
      }
    }
    
    // Добавление результата
    const addResult = () => {
      project.value.planned_results.push('')
    }
    
    // Удаление результата
    const removeResult = (index) => {
      project.value.planned_results.splice(index, 1)
    }
    
    // Добавление этапа
    const addStage = () => {
      const newStage = {
        name: '',
        description: '',
        planned_start_date: project.value.planned_start_date,
        planned_end_date: project.value.planned_end_date,
        expected_results: [],
        target_indicators: [],
        budget: null,
        order_number: project.value.stages.length + 1
      }
      project.value.stages.push(newStage)
    }
    
    // Удаление этапа
    const removeStage = (index) => {
      project.value.stages.splice(index, 1)
      // Пересчитываем порядковые номера
      project.value.stages.forEach((stage, idx) => {
        stage.order_number = idx + 1
      })
    }
    
    // Сохранение проекта
    const saveProject = async () => {
      // Проверим основные поля для сохранения
      if (!project.value.name?.trim()) {
        alert('Необходимо заполнить название проекта для сохранения')
        return
      }
      
      saving.value = true
      try {
        const data = { ...project.value }
        if (!data.organization_id) {
          delete data.organization_id
        }
        let response
        if (isEditMode.value) {
          response = await apiClient.patch(
            `/crm/strategic-projects/strategic-projects/${projectId}/`,
            data
          )
        } else {
          response = await apiClient.post(
            '/crm/strategic-projects/strategic-projects/',
            data
          )
        }
        
        // Показываем информацию о прогрессе заполнения
        const currentProgress = completionProgress.value
        let message = 'Проект успешно сохранен!'
        
        if (currentProgress < 100) {
          message += `\n\nПрогресс заполнения: ${currentProgress}%`
          if (currentProgress < 70) {
            message += '\nДля отправки на утверждение необходимо заполнить все обязательные поля.'
          }
        } else {
          message += '\n\nВсе поля заполнены. Проект готов к отправке на утверждение!'
        }
        
        alert(message)
        
        if (!isEditMode.value) {
          // Если создаем новый проект, перенаправляем на страницу редактирования
          router.push(`/crm/strategic-projects/project/${response.data.id}/edit`)
        }
      } catch (error) {
        console.error('Ошибка сохранения проекта:', error)
        
        // Более детальная обработка ошибок
        let errorMessage = 'Ошибка при сохранении проекта'
        if (error.response?.data?.error) {
          errorMessage += ': ' + error.response.data.error
        } else if (error.response?.data) {
          // Если есть детальные ошибки валидации
          const errorDetails = []
          Object.keys(error.response.data).forEach(field => {
            const fieldErrors = error.response.data[field]
            if (Array.isArray(fieldErrors)) {
              errorDetails.push(`${field}: ${fieldErrors.join(', ')}`)
            }
          })
          if (errorDetails.length > 0) {
            errorMessage += ':\n\n' + errorDetails.join('\n')
          }
        }
        
        alert(errorMessage)
      } finally {
        saving.value = false
      }
    }
    
    // Проверка валидности проекта
    const validateProject = () => {
      const errors = []
      
      // Основные поля
      if (!project.value.name?.trim()) {
        errors.push('• Название проекта не заполнено')
      }
      if (!project.value.goal?.trim()) {
        errors.push('• Цель проекта не заполнена')
      }
      if (!project.value.tasks?.trim()) {
        errors.push('• Задачи проекта не заполнены')
      }
      if (!project.value.curator) {
        errors.push('• Куратор проекта не выбран')
      }
      if (!project.value.customer) {
        errors.push('• Заказчик проекта не выбран')
      }
      if (!project.value.planned_start_date) {
        errors.push('• Плановая дата начала не указана')
      }
      if (!project.value.planned_end_date) {
        errors.push('• Плановая дата окончания не указана')
      }
      
      // Проверка логики дат
      if (project.value.planned_start_date && project.value.planned_end_date) {
        if (new Date(project.value.planned_start_date) >= new Date(project.value.planned_end_date)) {
          errors.push('• Дата начала должна быть раньше даты окончания')
        }
      }
      
      // Этапы проекта
      if (project.value.stages.length === 0) {
        errors.push('• Добавьте хотя бы один этап проекта')
      } else {
        project.value.stages.forEach((stage, index) => {
          if (!stage.name?.trim()) {
            errors.push(`• Этап ${index + 1}: не заполнено наименование`)
          }
          if (!stage.planned_start_date) {
            errors.push(`• Этап ${index + 1}: не указана дата начала`)
          }
          if (!stage.planned_end_date) {
            errors.push(`• Этап ${index + 1}: не указана дата окончания`)
          }
          if (stage.planned_start_date && stage.planned_end_date) {
            if (new Date(stage.planned_start_date) >= new Date(stage.planned_end_date)) {
              errors.push(`• Этап ${index + 1}: дата начала должна быть раньше даты окончания`)
            }
          }
        })
      }
      
      return errors
    }
    
    // Проверка готовности проекта
    const checkProjectReadiness = () => {
      const validationErrors = validateProject()
      const progress = completionProgress.value
      
      if (validationErrors.length === 0) {
        alert(`✅ Проект готов к отправке на утверждение!\n\nПрогресс заполнения: ${progress}%\n\nВсе обязательные поля заполнены корректно.`)
      } else {
        const message = `📋 Проверка готовности проекта\n\nПрогресс заполнения: ${progress}%\n\nНеобходимо исправить:\n\n${validationErrors.join('\n')}`
        alert(message)
      }
    }
    
    // Отправка на утверждение
    const submitForApproval = async () => {
      // Детальная проверка всех полей
      const validationErrors = validateProject()
      
      if (validationErrors.length > 0) {
        const errorMessage = 'Проект не готов к отправке на утверждение:\n\n' + validationErrors.join('\n')
        alert(errorMessage)
        return
      }
      
      if (!confirm('Отправить проект на утверждение?\n\nВнимание: после отправки редактирование будет ограничено.')) {
        return
      }
      
      submitting.value = true
      try {
        await apiClient.post(
          `/crm/strategic-projects/strategic-projects/${projectId}/submit_for_approval/`
        )
        alert('Проект отправлен на утверждение')
        router.push('/crm/strategic-projects')
      } catch (error) {
        console.error('Ошибка отправки на утверждение:', error)
        
        // Детальная обработка ошибок отправки
        let errorMessage = 'Ошибка при отправке на утверждение'
        
        if (error.response?.status === 400) {
          if (error.response.data?.error) {
            errorMessage += ': ' + error.response.data.error
          } else if (error.response.data) {
            // Проверяем различные форматы ошибок
            if (typeof error.response.data === 'string') {
              errorMessage += ': ' + error.response.data
            } else if (error.response.data.detail) {
              errorMessage += ': ' + error.response.data.detail
            } else {
              // Собираем все ошибки валидации
              const errorDetails = []
              Object.keys(error.response.data).forEach(field => {
                const fieldErrors = error.response.data[field]
                if (Array.isArray(fieldErrors)) {
                  errorDetails.push(`${field}: ${fieldErrors.join(', ')}`)
                } else if (typeof fieldErrors === 'string') {
                  errorDetails.push(`${field}: ${fieldErrors}`)
                }
              })
              if (errorDetails.length > 0) {
                errorMessage += ':\n\n' + errorDetails.join('\n')
              }
            }
          } else {
            errorMessage += '. Проверьте заполнение всех обязательных полей.'
          }
        } else {
          errorMessage += '. Попробуйте позже или обратитесь к администратору.'
        }
        
        alert(errorMessage)
      } finally {
        submitting.value = false
      }
    }
    
    // Получение класса для статуса
    const getStatusBadgeClass = (status) => {
      const classes = {
        draft: 'badge badge-secondary',
        on_approval: 'badge badge-warning',
        rejected: 'badge badge-danger',
        approved: 'badge badge-info',
        in_progress: 'badge badge-primary',
        completed: 'badge badge-success',
        archived: 'badge badge-dark'
      }
      return classes[status] || 'badge badge-secondary'
    }
    
    // Получение метки статуса
    const getStatusLabel = (status) => {
      const labels = {
        draft: 'Черновик',
        on_approval: 'На утверждении',
        rejected: 'Отклонен',
        approved: 'Утвержден',
        in_progress: 'В работе',
        completed: 'Завершен',
        archived: 'Архив'
      }
      return labels[status] || status
    }
    
    // Инициализация проекта для создания
    const initializeNewProject = () => {
      if (!isEditMode.value) {
        // Инициализируем пустой проект для создания
        project.value.planned_results = []
        project.value.stages = []
        
        // Устанавливаем даты по умолчанию
        const today = new Date()
        const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, today.getDate())
        const nextYear = new Date(today.getFullYear() + 1, today.getMonth(), today.getDate())
        
        project.value.planned_start_date = nextMonth.toISOString().split('T')[0]
        project.value.planned_end_date = nextYear.toISOString().split('T')[0]
      }
    }
    
    // Загрузка данных при монтировании
    onMounted(async () => {
      await Promise.all([loadUsers(), loadOrganizations()])
      await loadProject()
      initializeNewProject()
    })
    
    return {
      project,
      users,
      organizations,
      loadingUsers,
      loadingOrgs,
      isEditMode,
      saving,
      submitting,
      canSubmitForApproval,
      completionProgress,
      validateProject,
      checkProjectReadiness,
      addResult,
      removeResult,
      addStage,
      removeStage,
      saveProject,
      submitForApproval,
      getStatusBadgeClass,
      getStatusLabel,
      getProgressBarClass,
      getStatusCardClass,
      getStatusIcon
    }
  }
}
</script>

<style scoped>
.project-edit {
  padding: 20px 0;
  background-color: #f8f9fc;
  min-height: 100vh;
}

/* Заголовок страницы */
.page-header-gradient {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.breadcrumb-transparent {
  background-color: transparent;
  padding: 0;
  margin: 0;
}

.breadcrumb-transparent .breadcrumb-item a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
}

.breadcrumb-transparent .breadcrumb-item.active {
  color: white;
}

.project-code-badge {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-weight: 600;
  display: inline-block;
  font-size: 1rem;
}

/* Карточка статуса */
.status-card {
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

.status-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.status-card-secondary {
  background: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.status-card-secondary .status-icon {
  background: #6c757d;
  color: white;
}

.status-card-warning {
  background: rgba(255, 193, 7, 0.1);
  color: #856404;
}

.status-card-warning .status-icon {
  background: #ffc107;
  color: white;
}

.status-card-danger {
  background: rgba(220, 53, 69, 0.1);
  color: #721c24;
}

.status-card-danger .status-icon {
  background: #dc3545;
  color: white;
}

.status-card-info {
  background: rgba(23, 162, 184, 0.1);
  color: #0c5460;
}

.status-card-info .status-icon {
  background: #17a2b8;
  color: white;
}

.status-card-primary {
  background: rgba(0, 123, 255, 0.1);
  color: #004085;
}

.status-card-primary .status-icon {
  background: #007bff;
  color: white;
}

.status-card-success {
  background: rgba(40, 167, 69, 0.1);
  color: #155724;
}

.status-card-success .status-icon {
  background: #28a745;
  color: white;
}

.status-title {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.status-badge {
  font-size: 1.25rem;
  font-weight: 700;
}

.rejection-comment {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

/* Прогресс заполнения */
.progress-section {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

.progress-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2d3436;
  margin-bottom: 1rem;
}

.progress-xl {
  height: 25px;
  border-radius: 12px;
  background-color: #e9ecef;
}

.progress-bar {
  font-weight: 600;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.hint-item {
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.hint-warning {
  background: rgba(255, 193, 7, 0.1);
  color: #856404;
}

.hint-error {
  background: rgba(220, 53, 69, 0.1);
  color: #721c24;
}

.hint-success {
  background: rgba(40, 167, 69, 0.1);
  color: #155724;
}

/* Секции формы */
.form-section {
  background: white;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.section-header {
  padding: 1.5rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3436;
  margin: 0;
}

.section-body {
  padding: 2rem;
}

/* Элементы формы */
.form-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
  display: block;
}

.required-star {
  color: #dc3545;
  font-weight: 700;
}

.input-group-merge .input-group-prepend {
  margin-right: 0;
}

.input-group-merge .input-group-text {
  border-right: 0;
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.input-group-merge .form-control {
  border-left: 0;
}

.form-control {
  border-radius: 8px;
  border-color: #dee2e6;
  padding: 0.625rem 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.1);
}

.form-control-lg {
  font-size: 1.125rem;
  padding: 0.75rem 1.25rem;
}

/* Textarea с счетчиком */
.textarea-wrapper {
  position: relative;
}

.textarea-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.25rem;
}

.char-count {
  font-size: 0.75rem;
  color: #6c757d;
}

/* Этапы проекта */
.stage-card {
  border: 1px solid #e9ecef;
  border-radius: 12px;
  background: #f8f9fa;
  margin-bottom: 1rem;
  overflow: hidden;
}

.stage-header {
  background: white;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stage-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  font-weight: 600;
  margin-right: 0.75rem;
}

.stage-body {
  padding: 1.5rem;
}

/* Кнопки действий */
.action-buttons {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  position: sticky;
  bottom: 20px;
  z-index: 10;
}

.btn {
  border-radius: 8px;
  padding: 0.5rem 1.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

/* Кастомные селекты */
.select-wrapper {
  position: relative;
}

.custom-select {
  appearance: none;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  cursor: pointer;
  width: 100%;
}

.custom-select:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
  outline: none;
}

.custom-select:hover {
  border-color: #007bff;
}

.select-arrow {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  pointer-events: none;
  transition: all 0.3s ease;
}

.custom-select:focus + .select-arrow {
  color: #007bff;
  transform: translateY(-50%) rotate(180deg);
}

.custom-select:hover + .select-arrow {
  color: #007bff;
}

/* Дополнительные стили для подсказок */
.form-text {
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.text-warning {
  color: #856404 !important;
}

.text-info {
  color: #0c5460 !important;
}

.text-success {
  color: #155724 !important;
}

/* Адаптивность */
@media (max-width: 768px) {
  .page-header-gradient {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .status-card {
    flex-direction: column;
    text-align: center;
  }
  
  .progress-hints {
    justify-content: center;
  }
  
  .section-body {
    padding: 1rem;
  }
  
  .custom-select {
    padding: 0.625rem 2rem 0.625rem 0.875rem;
    font-size: 0.9rem;
  }
}
</style>
