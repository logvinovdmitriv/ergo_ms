<template>
  <div class="tasks-list">
    <div class="pm-page-header d-flex justify-content-between align-items-center" v-if="!managementMode">
      <h2 class="d-flex align-items-center">Задачи</h2>
      <div class="d-flex gap-2">
        <button type="button" class="btn btn-outline-primary d-inline-flex align-items-center gap-2" v-if="filters.project" @click="openProjectTree" aria-label="Открыть дерево проекта">
          <GitBranch :size="16" />
          <span>Дерево проекта</span>
        </button>
        <button type="button" class="btn btn-outline-secondary" v-if="filters.project" @click="openProjectList" aria-label="Список задач проекта">
          Список задач проекта
        </button>
        <button type="button" class="btn btn-primary d-inline-flex align-items-center gap-2" @click="createTask" aria-label="Создать задачу">
          <Plus :size="16" />
          <span>Создать задачу</span>
        </button>
      </div>
    </div>
    <!-- В режиме управления заголовок и кнопка создания показываются в родительском компоненте -->

    <!-- Фильтры и поиск -->
    <div class="pm-filters-card">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <div class="small text-muted">Фильтры</div>
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="resetFilters" aria-label="Сбросить фильтры">Сбросить</button>
        </div>
        <div class="row g-3">
          <div class="col-lg-2 col-md-3">
            <label class="form-label">Поиск</label>
            <input type="text" class="form-control" v-model="filters.search" @input="debouncedSearch" 
                   placeholder="Поиск по названию...">
          </div>
          <div class="col-lg-2 col-md-3">
            <label class="form-label">Статус</label>
            <select class="form-select" v-model="filters.status" @change="loadTasks" :disabled="loadingStatuses">
              <option value="">Все статусы</option>
              <option v-if="loadingStatuses">Загрузка...</option>
              <option v-else v-for="status in taskStatuses" :key="status.id" :value="status.code">
                {{ status.name }}
              </option>
            </select>
          </div>
          <div class="col-lg-2 col-md-3">
            <label class="form-label">Приоритет</label>
            <select class="form-select" v-model="filters.priority" @change="loadTasks" :disabled="loadingStatuses">
              <option value="">Все приоритеты</option>
              <option v-if="loadingStatuses">Загрузка...</option>
              <option v-else v-for="priority in taskPriorities" :key="priority.id" :value="priority.code">
                {{ priority.name }}
              </option>
            </select>
          </div>
          <div class="col-lg-2 col-md-3">
            <label class="form-label">Проект</label>
            <select class="form-select" v-model="filters.project" @change="loadTasks">
              <option value="">Все проекты</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.name }}
              </option>
            </select>
          </div>
          <div class="col-lg-2 col-md-3">
            <label class="form-label">Исполнитель</label>
            <select class="form-select" v-model="filters.assignee" @change="onAssigneeChange">
              <option value="">Все исполнители</option>
              <option v-for="user in users" :key="user.id" :value="user.id">
                {{ user.full_name || user.username }}
              </option>
            </select>
          </div>
          <div class="col-lg-2 col-md-3">
            <label class="form-label">Сортировка</label>
            <select class="form-select" v-model="filters.ordering" @change="loadTasks">
              <option value="-created_at">По дате создания ↓</option>
              <option value="created_at">По дате создания ↑</option>
              <option value="due_date">По сроку ↑</option>
              <option value="-due_date">По сроку ↓</option>
              <option value="priority">По приоритету ↑</option>
              <option value="-priority">По приоритету ↓</option>
              <option value="assignee">По исполнителю ↑</option>
              <option value="-assignee">По исполнителю ↓</option>
            </select>
          </div>
          <div class="col-lg-2 col-md-3">
            <label class="form-label">Размер страницы</label>
            <select class="form-select" v-model.number="filters.page_size" @change="onPageSizeChange">
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
          <div class="col-lg-2 col-md-3">
            <label class="form-label">Иерархия</label>
            <select class="form-select" v-model="filters.parent_filter" @change="loadTasks">
              <option value="">Все задачи</option>
              <option value="root">Только корневые</option>
              <option value="subtasks">Только подзадачи</option>
            </select>
          </div>
        </div>
        <div class="row g-3 mt-2">
          <div class="col-12 d-flex align-items-center">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="filters.my_tasks" @change="onMyTasksChange" id="myTasksFilter">
              <label class="form-check-label" for="myTasksFilter">
                Показать только мои задачи
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Переключатель вида -->
    <div class="d-flex justify-content-end align-items-center mb-3">
      <div class="btn-group" role="group" aria-label="Переключатель представления">
        <button type="button" class="btn btn-outline-secondary" :class="{ active: !showTree }" @click="toggleView(false)">Список</button>
        <button type="button" class="btn btn-outline-secondary" :class="{ active: showTree }" @click="toggleView(true)">Дерево</button>
      </div>
    </div>

    <!-- Список задач -->
    <div v-if="loading" class="text-center py-5">
      <div class="tasks-table-wrapper" v-if="!showTree">
        <div class="table-responsive">
          <table class="table table-hover tasks-table mb-0">
            <thead>
              <tr>
                <th>Задача</th>
                <th>Проект</th>
                <th>Иерархия</th>
                <th>Исполнитель</th>
                <th>Статус</th>
                <th>Приоритет</th>
                <th>Срок</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="i in 5" :key="`sk-${i}`" class="task-row">
                <td colspan="8">
                  <div class="placeholder-glow">
                    <span class="placeholder col-8"></span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else class="text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="text-muted mt-3">Загружаем дерево...</p>
      </div>
    </div>

    <div v-else-if="tasks.length === 0" class="empty-state">
      <div class="text-center">
        <h4 class="text-muted mb-3">Задач не найдено</h4>
        <p class="text-muted mb-4">Попробуйте изменить фильтры или создайте новую задачу</p>
        <button type="button" class="btn btn-primary btn-lg rounded-pill d-inline-flex align-items-center gap-2" @click="createTask">
          <Plus :size="18" />
          <span>Создать задачу</span>
        </button>
      </div>
    </div>

    <div v-else>
      <!-- Дерево -->
      <div v-if="showTree" class="task-tree-container">
        <div class="alert alert-light border mb-2" v-if="!filters.project">
          Для отображения дерева выберите проект в фильтре
        </div>
        <ProjectTasksTree v-else :project="currentProjectForTree" :tasks="tasks" />
      </div>

      <!-- Таблица -->
      <div v-else>
        <div class="d-flex justify-content-end gap-2 mb-2">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click="expandAllRows">Развернуть все</button>
          <button type="button" class="btn btn-outline-secondary btn-sm" @click="collapseAllRows">Свернуть все</button>
        </div>
      <!-- Табличный вид -->
      <div class="tasks-table-wrapper">
        <div class="table-responsive">
          <table class="table table-hover tasks-table mb-0">
            <thead>
              <tr>
                <th>Задача</th>
                <th>Проект</th>
                <th>Иерархия</th>
                <th>Исполнитель</th>
                <th>Статус</th>
                <th>Приоритет</th>
                <th>Срок</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in visibleRows" :key="row.task?.id" class="task-row">
                <td class="task-cell-main">
                  <div class="task-info">
                    <div class="d-flex align-items-center gap-2">
                       <button type="button" v-if="filters.project" class="btn btn-sm btn-outline-secondary d-inline-flex align-items-center justify-content-center" @click.stop="toggleExpandRow(row)" :aria-label="expandedRows.has(row.task.id) ? 'Свернуть' : 'Развернуть'" :aria-expanded="expandedRows.has(row.task.id)">
                        <ChevronDown v-if="expandedRows.has(row.task.id)" :size="16" />
                        <ChevronRight v-else :size="16" />
                      </button>
                      <h6 class="task-title mb-1" @click="viewTask(row.task)" :style="{ marginLeft: (filters.project ? (row.level * 16) : 0) + 'px' }">{{ row.task.title || 'Без названия' }}</h6>
                    </div>
                    <p class="task-description mb-0" v-if="row.task.description">
                      {{ truncateText(row.task.description, 80) }}
                    </p>
                    <div class="task-badges mt-2" v-if="row.task.attachment_count">
                      <span class="badge bg-light text-dark" v-if="row.task.attachment_count">
                        {{ row.task.attachment_count }}
                      </span>
                    </div>
                  </div>
                </td>
                <td class="project-cell">
                  <div class="project-info" v-if="row.task.project">
                    <div class="project-badge" 
                         :style="{ backgroundColor: row.task.project.color || '#007bff' }" 
                         :title="row.task.project.name">
                      <span class="project-name">{{ row.task.project.name }}</span>
                    </div>
                  </div>
                  <div v-else class="project-empty">
                    <span class="text-muted">
                      Без проекта
                    </span>
                  </div>
                </td>
                <td class="hierarchy-cell">
                  <div class="hierarchy-info" v-if="row.task.parent">
                    <span class="badge bg-info text-white">
                      Подзадача
                    </span>
                    <div class="parent-task-title mt-1" :title="row.task.parent_title || (row.task.parent && row.task.parent.title)">
                      {{ truncateText(row.task.parent_title || (row.task.parent && row.task.parent.title) || '', 30) }}
                    </div>
                  </div>
                  <div v-else-if="row.task.subtasks_count > 0">
                    <span class="badge bg-success text-white">
                      {{ row.task.subtasks_count }} подзадач
                    </span>
                  </div>
                  <span class="text-muted" v-else>
                    Корневая
                  </span>
                </td>
                <td>
                  <template v-if="row.task.assignee">
                    <div class="assignee-info">
                    <img :src="getAvatarUrl(row.task.assignee)" 
                         :alt="row.task.assignee.full_name || row.task.assignee.username"
                         class="assignee-avatar">
                    <span class="assignee-name">{{ row.task.assignee.full_name || `${row.task.assignee.first_name} ${row.task.assignee.last_name}`.trim() || row.task.assignee.username }}</span>
                    </div>
                  </template>
                  <div v-if="row.task.assignee_roles && row.task.assignee_roles.length" class="mt-1 d-flex flex-wrap gap-1">
                    <span v-for="link in row.task.assignee_roles" :key="link.user?.id + '-' + link.role" class="badge rounded-pill bg-light text-dark">
                      {{ link.user?.full_name || link.user?.username }} — {{ roleText(link.role) }}
                    </span>
                  </div>
                  <span class="text-muted" v-if="!row.task.assignee && !(row.task.assignee_roles && row.task.assignee_roles.length)">Не назначен</span>
                </td>
                <td>
                  <span class="badge rounded-pill" :class="getStatusClass(row.task.status)">
                    {{ getStatusText(row.task.status) }}
                  </span>
                </td>
                <td>
                  <span class="badge rounded-pill" :class="getPriorityClass(row.task.priority)">
                    {{ getPriorityText(row.task.priority) }}
                  </span>
                </td>
                <td>
                  <span :class="getDueDateClass(row.task.due_date, row.task.status)">
                    {{ formatDate(row.task.due_date) }}
                  </span>
                </td>
                <td @click.stop class="actions-cell">
                  <div class="action-buttons">
                    <button class="btn btn-edit-icon" @click="createSubTask(row.task)" title="Добавить подзадачу">
                      <Plus />
                    </button>
                    <button class="btn btn-edit-icon" @click="editTask(row.task)" title="Редактировать">
                      <Edit />
                    </button>
                    <button type="button" class="btn btn-edit-icon" @click="focusTaskInProjectTree(row.task)" title="Показать в дереве" aria-label="Показать в дереве">
                      <GitBranch :size="16" />
                    </button>
                    <button class="btn btn-delete-icon" @click="deleteTask(row.task)" title="Удалить">
                      <Trash2 />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      </div>
    </div>

    <!-- Пагинация -->
    <nav v-if="pagination.total_pages > 1" class="mt-5">
      <ul class="pagination pagination-modern justify-content-center">
        <li class="page-item" :class="{ disabled: !pagination.previous }">
          <button class="page-link d-inline-flex align-items-center justify-content-center" @click="changePage(pagination.current_page - 1)" 
                  :disabled="!pagination.previous">
            <ChevronLeft :size="16" />
          </button>
        </li>
        
        <li class="page-item" 
            v-for="page in getPageNumbers()" 
            :key="page"
            :class="{ active: page === pagination.current_page }">
          <button class="page-link" @click="changePage(page)">{{ page }}</button>
        </li>
        
        <li class="page-item" :class="{ disabled: !pagination.next }">
          <button class="page-link d-inline-flex align-items-center justify-content-center" @click="changePage(pagination.current_page + 1)" 
                  :disabled="!pagination.next">
            <ChevronRight :size="16" />
          </button>
        </li>
      </ul>
    </nav>

    <!-- Модальное окно создания/редактирования задачи -->
    <div class="modal fade" id="taskModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0">
          <div class="modal-header border-bottom">
            <h5 class="modal-title">{{ isEditing ? 'Редактировать задачу' : 'Создать задачу' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <form @submit.prevent="submitTask">
              <div class="mb-3">
                <label class="form-label fw-bold d-flex align-items-center gap-2">
                  <FileText :size="16" /> Название задачи <span class="text-danger">*</span>
                </label>
                  <input type="text" class="form-control" v-model="currentTask.title" required placeholder="Короткое и понятное название" autofocus>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold d-flex align-items-center gap-2">
                  <Briefcase :size="16" /> Проект <span class="text-danger">*</span>
                </label>
                <template v-if="projects.length">
                  <div class="d-flex gap-2">
                    <select class="form-select" v-model="currentTask.project_id" required @change="onProjectChange">
                      <option value="">Выберите проект</option>
                      <option v-for="project in projects" :key="project.id" :value="project.id">{{ project.name }}</option>
                    </select>
                    <button type="button" class="btn btn-outline-primary" @click="openQuickProjectModal">
                      <Plus :size="16" /> Проект
                    </button>
                  </div>
                  <small class="text-muted">Выберите проект или создайте новый</small>
                </template>
                <template v-else>
                  <div class="alert alert-light border d-grid gap-2">
                    <span class="mb-1">Проектов пока нет</span>
                    <div class="d-flex flex-column flex-sm-row gap-2">
                      <button type="button" class="btn btn-primary" @click="openQuickProjectModal"><Plus :size="16" /> Создать проект</button>
                      <button type="button" class="btn btn-outline-secondary" @click="openQuickTeamModal"><Users :size="16" /> Команду</button>
                      <button type="button" class="btn btn-outline-secondary" @click="openQuickOrganizationModal"><Home :size="16" /> Организацию</button>
                    </div>
                  </div>
                </template>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold d-flex align-items-center gap-2"><GitBranch :size="16" /> Родительская задача</label>
                <template v-if="currentTask.project_id">
                  <select class="form-select" v-model="currentTask.parent_id">
                    <option value="">Без родительской задачи</option>
                    <option v-for="task in availableParentTasks" :key="task.id" :value="task.id">{{ task.title }}</option>
                  </select>
                  <small class="text-muted d-block mt-1" v-if="!availableParentTasks.length">В проекте пока нет задач для выбора</small>
                </template>
                <template v-else>
                  <div class="alert alert-light border">Сначала выберите проект</div>
                </template>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold d-flex align-items-center gap-2"><Users :size="16" /> Исполнители</label>
                <div v-if="(currentTask.assignee_ids||[]).length" class="mb-2 d-flex flex-wrap gap-2">
                  <span v-for="uid in currentTask.assignee_ids" :key="`chip-${uid}`" class="assignee-chip">
                    {{ (usersFiltered.find(u => u.id === uid) || {}).full_name || (usersFiltered.find(u => u.id === uid) || {}).username }}
                  </span>
                </div>
                <template v-if="usersFiltered.length">
                  <input class="form-control mb-2" type="text" v-model="assigneesSearch" placeholder="Поиск по логину/ФИО" @input="filterUsers" />
                  <div class="border rounded p-2" style="max-height: 220px; overflow: auto;">
                    <div class="form-check" v-for="user in usersFiltered" :key="`cb-${user.id}`">
                      <input class="form-check-input" type="checkbox" :id="`assignee-${user.id}`" :value="user.id" v-model="currentTask.assignee_ids">
                      <label class="form-check-label" :for="`assignee-${user.id}`">
                        {{ user.full_name || `${user.first_name} ${user.last_name}`.trim() || user.username }}
                      </label>
                    </div>
                  </div>
                  <div class="mt-2">
                    <label class="form-label">Основной исполнитель</label>
                    <select class="form-select" v-model="currentTask.assignee_id" :disabled="!(currentTask.assignee_ids && currentTask.assignee_ids.length)">
                      <option value="">Не назначен</option>
                      <option v-for="uid in currentTask.assignee_ids" :key="`main-${uid}`" :value="uid">
                        {{ (usersFiltered.find(u => u.id === uid) || {}).full_name || (usersFiltered.find(u => u.id === uid) || {}).username }}
                      </option>
                    </select>
                    <small class="text-muted">Необязательно. Используйте, если есть ведущий исполнитель</small>
                  </div>
                  
                </template>
                <template v-else>
                  <div class="alert alert-light border d-grid">
                    <span class="mb-2">В проекте пока нет участников</span>
                    <small class="text-muted">Вы можете добавить пользователей ниже через поиск</small>
                  </div>
                </template>
              </div>

              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-bold d-flex align-items-center gap-2"><ListTodo :size="16" /> Статус</label>
                  <select class="form-select" v-model="currentTask.status" :disabled="loadingStatuses">
                    <option v-if="loadingStatuses">Загрузка...</option>
                    <option v-else v-for="status in taskStatuses" :key="status.id" :value="status.code">{{ status.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold d-flex align-items-center gap-2"><Flag :size="16" /> Приоритет</label>
                  <select class="form-select" v-model="currentTask.priority" :disabled="loadingStatuses">
                    <option v-if="loadingStatuses">Загрузка...</option>
                    <option v-else v-for="priority in taskPriorities" :key="priority.id" :value="priority.code">{{ priority.name }}</option>
                  </select>
                </div>
              </div>

              <div class="row g-3 mt-1">
                <div class="col-md-6">
                  <label class="form-label fw-bold d-flex align-items-center gap-2"><Calendar :size="16" /> Дата начала</label>
                  <input type="datetime-local" class="form-control" v-model="currentTask.start_date">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold d-flex align-items-center gap-2"><Calendar :size="16" /> Срок выполнения</label>
                  <input type="datetime-local" class="form-control" v-model="currentTask.due_date">
                </div>
              </div>

              <div class="mt-3">
                <label class="form-label fw-bold d-flex align-items-center gap-2"><Clock :size="16" /> Оценка времени (часы)</label>
                <input type="number" class="form-control" step="0.5" v-model="currentTask.estimated_hours" placeholder="Сколько часов потребуется">
              </div>

              <div class="mt-3">
                <label class="form-label fw-bold d-flex align-items-center gap-2"><FileText :size="16" /> Описание</label>
                <textarea class="form-control" rows="3" v-model="currentTask.description" placeholder="Коротко опишите задачу"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer border-top">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Отменить</button>
            <button type="button" class="btn btn-primary" @click="submitTask" 
                    :disabled="!canSubmitTask">
              {{ isEditing ? 'Сохранить' : 'Создать задачу' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно просмотра задачи -->
    <div class="modal fade" id="taskViewModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content border-0">
          <div class="modal-header bg-light border-bottom">
            <div class="d-flex align-items-center gap-3 w-100">
              
              <div class="flex-grow-1 overflow-hidden">
                <h5 class="modal-title mb-0 text-truncate" :title="selectedTask.title">{{ selectedTask.title }}</h5>
              </div>
            </div>
            <button type="button" class="btn-close flex-shrink-0 ms-3" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <div class="task-view-content">
              <!-- Статус и приоритет -->
              <div class="mb-4 d-flex gap-3">
                <span class="badge rounded-pill px-3 py-2" :class="getStatusClass(selectedTask.status)">
                  {{ getStatusText(selectedTask.status) }}
                </span>
                <span class="badge rounded-pill px-3 py-2" :class="getPriorityClass(selectedTask.priority)">
                  {{ getPriorityText(selectedTask.priority) }}
                </span>
              </div>

              <!-- Описание -->
              <div class="description-section mb-4 p-3 bg-light rounded" v-if="selectedTask.description">
                <h6 class="text-uppercase text-muted small mb-2">Описание</h6>
                <p class="mb-0 text-dark">{{ selectedTask.description }}</p>
              </div>

              <!-- Основная информация в карточках -->
              <div class="row g-3 mb-4">
                <!-- Проект -->
                <div class="col-md-6">
                  <div class="info-card h-100 p-3 border rounded">
                    <div class="d-flex align-items-center mb-2">
                      <div class="icon-sm bg-primary bg-opacity-10 p-2 rounded me-2">
                        
                      </div>
                      <h6 class="mb-0 text-muted small">Проект</h6>
                    </div>
                    <div class="fw-bold text-dark">
                      {{ selectedTask.project?.name || 'Без проекта' }}
                    </div>
                    <div class="project-color-bar mt-2" v-if="selectedTask.project" 
                         :style="{ backgroundColor: selectedTask.project.color || '#007bff' }">
                    </div>
                  </div>
                </div>

                <!-- Исполнитель -->
                <div class="col-md-6">
                  <div class="info-card h-100 p-3 border rounded">
                    <div class="d-flex align-items-center mb-2">
                      <div class="icon-sm bg-success bg-opacity-10 p-2 rounded me-2">
                        
                      </div>
                      <h6 class="mb-0 text-muted small">Исполнитель</h6>
                    </div>
                    <div class="d-flex align-items-center" v-if="selectedTask.assignee">
                      <img :src="getAvatarUrl(selectedTask.assignee)" 
                           :alt="selectedTask.assignee.full_name || selectedTask.assignee.username"
                           class="rounded-circle me-2"
                           style="width: 32px; height: 32px; object-fit: cover;">
                      <div class="fw-bold text-dark">
                        {{ selectedTask.assignee?.full_name || 'Не назначен' }}
                      </div>
                    </div>
                    <div v-else class="fw-bold text-muted">
                      Не назначен
                    </div>
                  </div>
                </div>
              </div>

              <!-- Даты и время -->
              <div class="row g-3 mb-4">
                <!-- Сроки -->
                <div class="col-md-6">
                  <div class="info-card h-100 p-3 border rounded">
                    <div class="d-flex align-items-center mb-2">
                      <div class="icon-sm bg-warning bg-opacity-10 p-2 rounded me-2">
                        
                      </div>
                      <h6 class="mb-0 text-muted small">Сроки</h6>
                    </div>
                    <div v-if="selectedTask.due_date">
                      <div class="mb-1">
                        <small class="text-muted">Срок выполнения:</small>
                      </div>
                      <div class="fw-bold" :class="getDueDateClass(selectedTask.due_date, selectedTask.status)">
                        {{ formatDateTime(selectedTask.due_date) }}
                      </div>
                    </div>
                    <div v-else class="fw-bold text-muted">
                      Срок не установлен
                    </div>
                  </div>
                </div>

                <!-- Время -->
                <div class="col-md-6" v-if="selectedTask.estimated_hours || selectedTask.actual_hours">
                  <div class="info-card h-100 p-3 border rounded">
                    <div class="d-flex align-items-center mb-2">
                      <div class="icon-sm bg-info bg-opacity-10 p-2 rounded me-2">
                        
                      </div>
                      <h6 class="mb-0 text-muted small">
                        <i class="fas fa-hourglass-half me-1"></i>ВРЕМЯ
                      </h6>
                    </div>
                    <div class="d-flex justify-content-around">
                      <div v-if="selectedTask.estimated_hours" class="text-center">
                        <div class="fw-bold text-info">
                        {{ selectedTask.estimated_hours }}ч
                        </div>
                        <small class="text-muted">Оценка</small>
                      </div>
                      <div v-if="selectedTask.actual_hours" class="text-center">
                        <div class="fw-bold text-success">
                        {{ selectedTask.actual_hours }}ч
                        </div>
                        <small class="text-muted">Потрачено</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Метаинформация -->
              <div class="meta-info p-3 bg-light rounded">
                <div class="row g-3">
                  <div class="col-6">
                    <small class="text-muted d-block mb-1">Создана</small>
                    <div class="small">
                      {{ formatDateTime(selectedTask.created_at) }}
                      <span v-if="selectedTask.creator" class="text-muted">
                        ({{ selectedTask.creator.full_name }})
                      </span>
                    </div>
                  </div>
                  <div class="col-6" v-if="selectedTask.updated_at">
                    <small class="text-muted d-block mb-1">Обновлена</small>
                    <div class="small">{{ formatDateTime(selectedTask.updated_at) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer bg-light border-top">
            <button type="button" class="btn btn-secondary d-inline-flex align-items-center gap-2" data-bs-dismiss="modal">
              <X :size="16" />
              <span>Закрыть</span>
            </button>
            <button v-if="selectedTask && selectedTask.id && selectedTask.project" @click="focusTaskInProjectTree(selectedTask)" class="btn btn-outline-primary">
              <GitBranch :size="16" /> Показать в дереве
            </button>
            <button v-if="selectedTask && selectedTask.id" @click="editTaskFromView" class="btn btn-primary d-inline-flex align-items-center gap-2">
              <Edit :size="16" />
              <span>Редактировать</span>
            </button>
            <button v-if="selectedTask && selectedTask.id" @click="deleteTask(selectedTask)" class="btn btn-danger d-inline-flex align-items-center gap-2">
              <Trash2 :size="16" />
              <span>Удалить</span>
            </button>
            <button v-if="selectedTask.project" 
                    @click="goToProject"
                    class="btn btn-primary d-inline-flex align-items-center gap-2">
              <FolderOpen :size="16" />
              <span>Перейти к проекту</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Быстрое создание проекта -->
  <div class="modal fade" id="quickProjectModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Быстрое создание проекта</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Название проекта <span class="text-danger">*</span></label>
            <input v-model="quickProject.name" type="text" class="form-control" placeholder="Введите название" autofocus />
          </div>
          <div class="mb-3">
            <label class="form-label">Команда <span class="text-danger">*</span></label>
            <template v-if="quickTeams.length">
              <select v-model="quickProject.team_id" class="form-select">
                <option value="">Выберите команду</option>
                <option v-for="t in quickTeams" :key="t.id" :value="t.id">{{ t.name }}</option>
              </select>
            </template>
            <template v-else>
              <div class="alert alert-light border d-grid gap-2">
                <span class="mb-1">Команды отсутствуют</span>
                <button class="btn btn-outline-secondary w-100" type="button" @click="openQuickTeamModal">Создать команду</button>
                <button class="btn btn-outline-secondary w-100" type="button" @click="openQuickOrganizationModal">Создать организацию</button>
              </div>
            </template>
          </div>
          <div class="mb-3">
            <label class="form-label">Описание</label>
            <textarea v-model="quickProject.description" class="form-control" rows="3" placeholder="Краткое описание"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-light" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" :disabled="!quickProject.name || !quickProject.team_id || loadingQuickProject" @click="createQuickProject">
            <i v-if="loadingQuickProject" class="fas fa-spinner fa-spin me-2"></i>
            Создать
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Быстрое создание команды -->
  <div class="modal fade" id="quickTeamModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Быстрое создание команды</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Название команды <span class="text-danger">*</span></label>
            <input v-model="quickTeam.name" type="text" class="form-control" placeholder="Введите название" autofocus />
          </div>
          <div class="mb-3">
            <label class="form-label">Организация <span class="text-danger">*</span></label>
            <template v-if="quickOrganizations.length">
              <select v-model="quickTeam.organization_id" class="form-select">
                <option value="">Выберите организацию</option>
                <option v-for="o in quickOrganizations" :key="o.id" :value="o.id">{{ o.name }}</option>
              </select>
            </template>
            <template v-else>
              <div class="alert alert-light border d-grid gap-2">
                <span class="mb-1">Организации отсутствуют</span>
                <button class="btn btn-primary w-100" type="button" @click="openQuickOrganizationModal">Создать организацию</button>
              </div>
            </template>
          </div>
          <div class="mb-3">
            <label class="form-label">Описание</label>
            <textarea v-model="quickTeam.description" class="form-control" rows="3" placeholder="Краткое описание"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-light" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" :disabled="!quickTeam.name || !quickTeam.organization_id || loadingQuickTeam" @click="createQuickTeam">
            <i v-if="loadingQuickTeam" class="fas fa-spinner fa-spin me-2"></i>
            Создать
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Быстрое создание организации -->
  <div class="modal fade" id="quickOrganizationModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Быстрое создание организации</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Название организации <span class="text-danger">*</span></label>
            <input v-model="quickOrganization.name" type="text" class="form-control" placeholder="Введите название" autofocus />
          </div>
          <div class="mb-3">
            <label class="form-label">Описание</label>
            <textarea v-model="quickOrganization.description" class="form-control" rows="3" placeholder="Краткое описание"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-light" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" :disabled="!quickOrganization.name || loadingQuickOrganization" @click="createQuickOrganization">
            <i v-if="loadingQuickOrganization" class="fas fa-spinner fa-spin me-2"></i>
            Создать
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap'
import { Edit, Trash2, Plus, FileText, Briefcase, Users, GitBranch, Search, UserPlus, ListTodo, Flag, Calendar, Clock, Home, List, ChevronLeft, ChevronRight, ChevronDown, Paperclip, Folder, FolderOpen, CornerDownRight, Circle, AlignLeft, ClipboardCheck, Hourglass, Timer, PlusCircle, X } from 'lucide-vue-next'
import projectManagementApi from '@/modules/crm/project-management/js/projectManagementApi.js'
import { useNotifications } from '@/modules/lms/composables/useNotifications'
import { getAvatarUrl } from '@/modules/cms/js/avatarUtils.js'
import organizationApi from '@/modules/crm/organizations/js/organizationApi.js'
import ProjectTasksTree from './ProjectTasksTree.vue'

export default {
  name: 'TasksList',
  components: {
    Edit,
    Trash2,
    Plus,
    FileText,
    Briefcase,
    Users,
    GitBranch,
    Search,
    UserPlus,
    ListTodo,
    Flag,
    Calendar,
    Clock,
    Home,
    List,
    ChevronLeft,
    ChevronRight,
    ChevronDown,
    Paperclip,
    Folder,
    FolderOpen,
    CornerDownRight,
    Circle,
    AlignLeft,
    ClipboardCheck,
    Hourglass,
    Timer,
    PlusCircle,
    X,
    ProjectTasksTree
  },
  props: {
    managementMode: {
      type: Boolean,
      default: false
    },
    initialFilters: {
      type: Object,
      default: null
    }
  },
  setup() {
    const { showSuccess, showError, showConfirmDialog, closeConfirmDialog } = useNotifications()
    return { showSuccess, showError, showConfirmDialog, closeConfirmDialog }
  },
  data() {
    return {
      tasks: [],
      visibleRows: [],
      expandedRows: new Set(),
      childrenMap: new Map(),
      projects: [],
      users: [],
      usersFiltered: [],
      
      loading: false,
      showTree: false,
      filters: {
        search: '',
        status: '',
        priority: '',
        project: '',
        assignee: '', // Добавляем фильтр по исполнителю
        ordering: '-created_at',
        my_tasks: false, // По умолчанию false, чтобы не конфликтовать с другими фильтрами
        parent_filter: '' // Фильтр по иерархии задач
      },
      pagination: {
        current_page: 1,
        total_pages: 1,
        previous: null,
        next: null,
        count: 0
      },
      currentTask: {
        title: '',
        description: '',
        project_id: '',
        assignee_id: '',
        assignee_ids: [],
        status: 'todo',
        priority: 'medium',
        start_date: '',
        due_date: '',
        estimated_hours: null,
        parent_id: null
      },
      selectedTask: {},
      isEditing: false,
      searchTimeout: null,
      loadCancel: null,
      // Динамические данные для статусов и приоритетов
      taskStatuses: [],
      taskPriorities: [],
      loadingStatuses: false,
      // Доступные родительские задачи для выбранного проекта
      availableParentTasks: [],
      assigneesSearch: '',
      currentProjectMeta: null,
      // Данные для быстрых модалок
      quickTeams: [],
      quickOrganizations: [],
      quickProject: { name: '', description: '', team_id: '' },
      quickTeam: { name: '', description: '', organization_id: '' },
      quickOrganization: { name: '', description: '' },
      loadingQuickProject: false,
      loadingQuickTeam: false,
      loadingQuickOrganization: false
    }
  },
  
  async mounted() {
    await this.loadProjects()
    await this.loadUsers()
    await this.loadStatusesAndPriorities()
    // Применяем стартовые фильтры и роут-параметры, затем грузим задачи
    this.applyInitialFilters()
    this.applyRouteFilters(this.$route?.query || {})
    await this.loadTasks()
    
    // Доп. обработка URL для авто-создания задачи
    this.handleUrlParams()
  },
  
  computed: {
    debouncedSearch() {
      return () => {
        clearTimeout(this.searchTimeout)
        this.searchTimeout = setTimeout(() => {
          this.pagination.current_page = 1
          this.loadTasks()
        }, 500)
      }
    },
    canSubmitTask() {
      return Boolean(this.currentTask.title && this.currentTask.project_id)
    },
    currentProjectForTree() {
      const pid = this.filters.project ? Number(this.filters.project) : null
      if (!pid) return null
      const fromList = (this.projects || []).find(p => Number(p.id) === pid)
      if (fromList) return fromList
      const fromTasks = (this.tasks || []).map(t => t.project).find(p => p && Number(p.id) === pid)
      return fromTasks || { id: pid, name: '' }
    }
  },
  
  methods: {
    // Применение входных фильтров из пропса
    applyInitialFilters() {
      if (!this.initialFilters || typeof this.initialFilters !== 'object') return
      const f = this.normalizeFilters(this.initialFilters)
      this.filters = { ...this.filters, ...f }
      this.pagination.current_page = 1
    },
    // Применение фильтров из route.query
    applyRouteFilters(query) {
      if (!query || typeof query !== 'object') return
      const map = {
        project: (v) => (v != null ? String(v) : ''),
        projectFilter: (v) => (v != null ? String(v) : ''),
        my_tasks: (v) => ['1', 'true', 'True', true].includes(v),
        status: (v) => (v || ''),
        priority: (v) => (v || ''),
        assignee: (v) => (v ? String(v) : ''),
        ordering: (v) => (v || ''),
        parent_filter: (v) => (v || ''),
        search: (v) => (v || ''),
        view: (v) => (v || '')
      }
      const next = { ...this.filters }
      Object.keys(map).forEach(k => {
        if (Object.prototype.hasOwnProperty.call(query, k)) {
          const val = map[k](query[k])
          if (k === 'project' || k === 'projectFilter') next.project = val
          else if (k === 'view') this.showTree = (val === 'tree') && Boolean(next.project)
          else next[k] = val
        }
      })
      this.filters = next
      this.pagination.current_page = 1
    },
    normalizeFilters(obj) {
      const out = {}
      if ('project' in obj) out.project = obj.project != null ? String(obj.project) : ''
      if ('my_tasks' in obj) out.my_tasks = Boolean(obj.my_tasks)
      if ('status' in obj) out.status = obj.status || ''
      if ('priority' in obj) out.priority = obj.priority || ''
      if ('assignee' in obj) out.assignee = obj.assignee ? String(obj.assignee) : ''
      if ('ordering' in obj) out.ordering = obj.ordering || ''
      if ('parent_filter' in obj) out.parent_filter = obj.parent_filter || ''
      if ('search' in obj) out.search = obj.search || ''
      if ('view' in obj) this.showTree = obj.view === 'tree'
      return out
    },
    // Публичный метод для установки фильтра проекта извне
    setProjectFilter(projectId) {
      this.filters.project = projectId ? String(projectId) : ''
      this.pagination.current_page = 1
      this.loadTasks()
    },
    async loadProjects() {
      try {
        const response = await projectManagementApi.getProjects({ my_projects: true })
        this.projects = Array.isArray(response.data.results) ? response.data.results : 
                        Array.isArray(response.data) ? response.data : []
      } catch (error) {
        console.error('Ошибка загрузки проектов:', error)
        this.projects = []
      }
    },
    
    async loadUsers() {
      try {
        const response = await projectManagementApi.getUsers()
        this.users = Array.isArray(response.data.results) ? response.data.results : 
                     Array.isArray(response.data) ? response.data : []
        this.usersFiltered = this.users
      } catch (error) {
        console.error('Ошибка загрузки пользователей:', error)
        this.users = []
        this.usersFiltered = []
      }
    },
    
    filterUsers() {
      const q = (this.assigneesSearch || '').toLowerCase().trim()
      if (!q) {
        this.usersFiltered = this.users
        return
      }
      this.usersFiltered = this.users.filter(u => {
        const login = (u.username || '').toLowerCase()
        const full = (u.full_name || `${u.first_name || ''} ${u.last_name || ''}`.trim()).toLowerCase()
        return login.includes(q) || full.includes(q)
      })
    },
    
    async loadTasks() {
      this.loading = true
      try {
        // отменяем предыдущий незавершенный запрос
        if (this.loadCancel) {
          this.loadCancel('cancelled by new request')
          this.loadCancel = null
        }
        const rawParams = {
          page: this.pagination.current_page,
          page_size: this.filters.page_size || 20,
          ...this.filters
        }
        // Переносим project -> project_id
        const params = { ...rawParams }
        if (params.project) {
          params.project_id = params.project
          delete params.project
        }
        // Убираем пустые и ложные значения; my_tasks передаем только если true
        Object.keys(params).forEach(key => {
          const val = params[key]
          const keep = key === 'my_tasks' ? Boolean(val) : Boolean(val || val === 0)
          if (!keep) delete params[key]
        })
        
        // создаем cancel token
        const source = projectManagementApi.client.CancelToken ? projectManagementApi.client.CancelToken.source() : null
        if (source) this.loadCancel = source.cancel
        const response = await projectManagementApi.client.get('/crm/tasks/', { params, cancelToken: source ? source.token : undefined })
        
        if (response.data.results) {
          this.tasks = this.uniqueById(response.data.results)
          this.pagination = {
            current_page: response.data.current_page || 1,
            total_pages: response.data.total_pages || 1,
            previous: response.data.previous,
            next: response.data.next,
            count: response.data.count || 0
          }
        } else {
          this.tasks = Array.isArray(response.data) ? this.uniqueById(response.data) : []
        }
        // Мгновенно показываем список
        this.rebuildVisibleRows()
        // Фоново подгружаем роли исполнителей, не блокируя UI
        this.enrichAssigneeRolesInBatches(this.tasks, 8)
      } catch (error) {
        if (error && error.message === 'cancelled by new request') return
        console.error('Ошибка загрузки задач:', error)
        this.tasks = []
      } finally {
        this.loading = false
        this.loadCancel = null
      }
    },

    rebuildVisibleRows() {
      if (this.filters.project) {
        const byParent = {}
        this.tasks.forEach(t => {
          const pid = t.parent || t.parent_id || null
          if (!byParent[pid]) byParent[pid] = []
          byParent[pid].push(t)
        })
        const rows = []
        const seen = new Set()
        const build = (parentId, level) => {
          const list = byParent[parentId] || []
          list.forEach(t => {
            if (!t || seen.has(t.id)) return
            seen.add(t.id)
            rows.push({ task: t, level })
            if (this.expandedRows.has(t.id)) {
              const localChildren = this.childrenMap.get(t.id) || []
              localChildren.forEach(c => {
                if (!c || seen.has(c.id)) return
                seen.add(c.id)
                rows.push({ task: c, level: level + 1 })
                if (this.expandedRows.has(c.id)) build(c.id, level + 2)
              })
              build(t.id, level + 1)
            }
          })
        }
        build(null, 0)
        this.visibleRows = rows
      } else {
        const seen = new Set()
        this.visibleRows = (this.tasks || []).filter(t => t && !seen.has(t.id) && seen.add(t.id)).map(t => ({ task: t, level: 0 }))
      }
    },

    uniqueById(list) {
      const seen = new Set()
      const out = []
      ;(Array.isArray(list) ? list : []).forEach(it => {
        if (it && !seen.has(it.id)) { seen.add(it.id); out.push(it) }
      })
      return out
    },

    async toggleExpandRow(row) {
      const task = row?.task
      if (!task) return
      if (this.expandedRows.has(task.id)) {
        this.expandedRows.delete(task.id)
        this.rebuildVisibleRows()
        return
      }
      if (!this.childrenMap.has(task.id)) {
        try {
          const res = await projectManagementApi.client.get('/crm/tasks/project_tree/', {
            params: { project_id: task.project?.id || task.project_id, root_id: task.id, depth: 1 }
          })
          const tree = res.data?.tree || []
          const children = Array.isArray(tree) ? tree : []
          this.childrenMap.set(task.id, children)
        } catch (e) {
          this.childrenMap.set(task.id, [])
        }
      }
      this.expandedRows.add(task.id)
      this.rebuildVisibleRows()
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.pagination.total_pages) {
        this.pagination.current_page = page
        this.pushRouteQuery()
        this.loadTasks()
      }
    },
    onPageSizeChange() {
      this.pagination.current_page = 1
      this.pushRouteQuery()
      this.loadTasks()
    },
    
    onAssigneeChange() {
      // Когда выбран конкретный исполнитель, сбрасываем "Мои задачи"
      if (this.filters.assignee) {
        this.filters.my_tasks = false
      }
      this.pagination.current_page = 1  // Сбрасываем на первую страницу
      this.pushRouteQuery()
      this.loadTasks()
    },
    
    onMyTasksChange() {
      // Когда включен "Мои задачи", сбрасываем фильтр по исполнителю
      if (this.filters.my_tasks) {
        this.filters.assignee = ''
      }
      this.pagination.current_page = 1  // Сбрасываем на первую страницу
      this.pushRouteQuery()
      this.loadTasks()
    },
    
    async onProjectChange() {
      // При изменении проекта сбрасываем родительскую задачу и загружаем доступные родительские задачи
      this.currentTask.parent_id = null
      this.loadAvailableParentTasks()
      // Фильтруем список пользователей по команде проекта
      try {
        if (!this.currentTask.project_id) {
          this.usersFiltered = this.users
          return
        }
        const projectResp = await projectManagementApi.getProject(this.currentTask.project_id)
        const project = projectResp.data
        this.currentProjectMeta = project
        const teamUserIds = new Set()
        if (project?.owner?.id) teamUserIds.add(project.owner.id)
        if (project?.manager?.id) teamUserIds.add(project.manager.id)
        if (Array.isArray(project?.memberships)) {
          project.memberships.forEach(m => m?.user?.id && teamUserIds.add(m.user.id))
        }
        // если команда пуста — показываем всех, иначе фильтруем
        this.usersFiltered = teamUserIds.size ? this.users.filter(u => teamUserIds.has(u.id)) : this.users
        // Пересекаем выбранных исполнителей с доступными из команды
        const allowedIds = new Set(this.usersFiltered.map(u => u.id))
        this.currentTask.assignee_ids = (this.currentTask.assignee_ids || []).filter(id => allowedIds.has(id))
        if (this.currentTask.assignee_id && !allowedIds.has(this.currentTask.assignee_id)) {
          this.currentTask.assignee_id = ''
        }
      } catch (e) {
        console.error('Ошибка загрузки проекта для фильтрации пользователей', e)
        this.usersFiltered = this.users
      }
    },
    
    async loadAvailableParentTasks() {
      if (!this.currentTask.project_id) {
        this.availableParentTasks = []
        return
      }
      try {
        // Загружаем ВСЕ задачи проекта (любой глубины) для выбора родителя
        const response = await projectManagementApi.getTasks({ project_id: this.currentTask.project_id })
        const list = response.data.results || response.data || []
        // Исключаем текущую задачу при редактировании, чтобы избежать цикла
        const excludeId = this.currentTask?.id
        this.availableParentTasks = Array.isArray(list)
          ? list.filter(t => !excludeId || t.id !== excludeId)
          : []
      } catch (error) {
        console.error('Ошибка загрузки доступных родительских задач:', error)
        this.availableParentTasks = []
      }
    },

    async loadStatusesAndPriorities() {
      try {
        this.loadingStatuses = true
        const [statusesResponse, prioritiesResponse] = await Promise.all([
          projectManagementApi.getTaskStatuses(),
          projectManagementApi.getTaskPriorities()
        ])
        
        // Обрабатываем ответ - может быть массив или объект с results
        this.taskStatuses = Array.isArray(statusesResponse.data) ? 
          statusesResponse.data.filter(s => s.is_active) : 
          (statusesResponse.data.results || []).filter(s => s.is_active)
          
        this.taskPriorities = Array.isArray(prioritiesResponse.data) ? 
          prioritiesResponse.data.filter(p => p.is_active) : 
          (prioritiesResponse.data.results || []).filter(p => p.is_active)
          
        console.log(`Загружено статусов задач: ${this.taskStatuses.length}, приоритетов: ${this.taskPriorities.length}`)
        console.log('Статусы задач:', this.taskStatuses.map(s => s.name))
        console.log('Приоритеты задач:', this.taskPriorities.map(p => p.name))
        
        // Устанавливаем значения по умолчанию если есть
        const defaultStatus = this.taskStatuses.find(s => s.is_default)
        const defaultPriority = this.taskPriorities.find(p => p.is_default)
        
        if (defaultStatus && !this.isEditing) {
          this.currentTask.status = defaultStatus.code
        }
        if (defaultPriority && !this.isEditing) {
          this.currentTask.priority = defaultPriority.code
        }
      } catch (error) {
        console.error('Ошибка загрузки статусов и приоритетов:', error)
        // Fallback к жестко заданным значениям
        this.taskStatuses = [
          { id: 1, name: 'К выполнению', code: 'todo' },
          { id: 2, name: 'В работе', code: 'in_progress' },
          { id: 3, name: 'На проверке', code: 'review' },
          { id: 4, name: 'Выполнено', code: 'done' },
          { id: 5, name: 'Отменено', code: 'cancelled' }
        ]
        this.taskPriorities = [
          { id: 1, name: 'Низкий', code: 'low' },
          { id: 2, name: 'Средний', code: 'medium' },
          { id: 3, name: 'Высокий', code: 'high' },
          { id: 4, name: 'Срочный', code: 'urgent' }
        ]
      } finally {
        this.loadingStatuses = false
      }
    },
    
    getPageNumbers() {
      const pages = []
      const current = this.pagination.current_page
      const total = this.pagination.total_pages
      
      for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
        pages.push(i)
      }
      
      return pages
    },

    // Публичный метод для обновления статусов и приоритетов
    async refreshStatusesAndPriorities() {
      await this.loadStatusesAndPriorities()
      console.log('Статусы и приоритеты задач обновлены:', this.taskStatuses.length, this.taskPriorities.length)
    },
    
    async createTask(parentTask = null) {
      this.isEditing = false

      // Обновляем статусы и приоритеты перед созданием задачи
      console.log('Обновляем статусы перед созданием задачи...')
      await this.refreshStatusesAndPriorities()

      // Устанавливаем значения по умолчанию из загруженных данных
      const defaultStatus = this.taskStatuses.find(s => s.is_default) || this.taskStatuses[0]
      const defaultPriority = this.taskPriorities.find(p => p.is_default) || this.taskPriorities[0]

      this.currentTask = {
        title: '',
        description: '',
        project_id: parentTask?.project?.id || '',
        assignee_id: '',
        assignee_ids: [],
        status: defaultStatus ? defaultStatus.code : 'todo',
        priority: defaultPriority ? defaultPriority.code : 'medium',
        start_date: '',
        due_date: '',
        estimated_hours: null,
        parent_id: parentTask ? parentTask.id : null
      }
      
      // Если указан проект, подгружаем связанные данные
      if (this.currentTask.project_id) {
        await this.loadAvailableParentTasks()
        await this.onProjectChange()
      }
 
      const modal = new Modal(document.getElementById('taskModal'))
      modal.show()
    },

    createSubTask(task) {
      this.createTask(task)
    },
    
    editTask(task) {
      this.isEditing = true
      this.currentTask = {
        id: task.id,
        title: task.title,
        description: task.description,
        project_id: task.project?.id,
        assignee_id: task.assignee?.id,
        status: task.status,
        priority: task.priority,
        start_date: task.start_date ? this.formatDateTimeLocal(new Date(task.start_date)) : '',
        due_date: task.due_date ? this.formatDateTimeLocal(new Date(task.due_date)) : '',
        estimated_hours: task.estimated_hours,
        parent_id: task.parent || null
      }
      
      // Загружаем доступные родительские задачи для редактирования
      if (this.currentTask.project_id) {
        this.loadAvailableParentTasks()
      }
      
      const modal = new Modal(document.getElementById('taskModal'))
      modal.show()
    },
    
    editTaskFromView() {
      this.editTask(this.selectedTask)
      
      // Закрываем модальное окно просмотра
      const viewModal = Modal.getInstance(document.getElementById('taskViewModal'))
      if (viewModal) viewModal.hide()
    },
    
    viewTask(task) {
      this.selectedTask = task
      const modal = new Modal(document.getElementById('taskViewModal'))
      modal.show()
    },

    async enrichAssigneeRolesInBatches(tasks, concurrency = 6) {
      try {
        const queue = (tasks || []).filter(t => t && t.id)
        let index = 0
        const runWorker = async () => {
          while (index < queue.length) {
            const cur = queue[index++]
            try {
              const res = await projectManagementApi.getTaskAssignees(cur.id)
              cur.assignee_roles = Array.isArray(res.data) ? res.data : []
            } catch (_) {
              cur.assignee_roles = []
            }
            // Обновляем видимые строки партиями, чтобы UI был отзывчивым
            if (index % 5 === 0) this.rebuildVisibleRows()
          }
        }
        const workers = Array.from({ length: Math.max(1, concurrency) }, runWorker)
        await Promise.allSettled(workers)
        this.rebuildVisibleRows()
      } catch (e) {
        console.error('Ошибка подгрузки ролей исполнителей', e)
      }
    },

    // Быстрые модалки
    async openQuickProjectModal() {
      await Promise.all([this.loadQuickTeams(), this.loadQuickOrganizations()])
      const modal = new Modal(document.getElementById('quickProjectModal'))
      modal.show()
    },
    async openQuickTeamModal() {
      await this.loadQuickOrganizations()
      const modal = new Modal(document.getElementById('quickTeamModal'))
      modal.show()
    },
    openQuickOrganizationModal() {
      const modal = new Modal(document.getElementById('quickOrganizationModal'))
      modal.show()
    },
    async loadQuickTeams() {
      try {
        const res = await projectManagementApi.getTeams({ my_teams: true })
        this.quickTeams = res.data.results || res.data || []
      } catch {
        this.quickTeams = []
      }
    },
    async loadQuickOrganizations() {
      try {
        const res = await organizationApi.getOrganizations()
        this.quickOrganizations = res.data.results || res.data || []
      } catch {
        this.quickOrganizations = []
      }
    },
    async createQuickProject() {
      this.loadingQuickProject = true
      try {
        const payload = {
          name: this.quickProject.name,
          description: this.quickProject.description || '',
          team_id: this.quickProject.team_id,
          status: 'planning',
          priority: 'medium',
          color: '#007bff'
        }
        const res = await projectManagementApi.createProject(payload)
        // Обновляем список проектов и подставляем выбранный
        await this.loadProjects()
        this.currentTask.project_id = res.data?.id
        await this.onProjectChange()
        this.showSuccess('Проект создан')
        const modal = Modal.getInstance(document.getElementById('quickProjectModal'))
        if (modal) modal.hide()
      } catch (e) {
        console.error('Ошибка создания проекта', e)
        this.showError('Ошибка создания проекта')
      } finally {
        this.loadingQuickProject = false
      }
    },
    async createQuickTeam() {
      this.loadingQuickTeam = true
      try {
        const res = await projectManagementApi.createTeam({
          name: this.quickTeam.name,
          description: this.quickTeam.description || '',
          organization_id: this.quickTeam.organization_id
        })
        // Обновляем команды для модалки проекта
        await this.loadQuickTeams()
        this.quickProject.team_id = res.data?.id
        this.showSuccess('Команда создана')
        const modal = Modal.getInstance(document.getElementById('quickTeamModal'))
        if (modal) modal.hide()
      } catch (e) {
        console.error('Ошибка создания команды', e)
        this.showError('Ошибка создания команды')
      } finally {
        this.loadingQuickTeam = false
      }
    },
    async createQuickOrganization() {
      this.loadingQuickOrganization = true
      try {
        const res = await organizationApi.createOrganization({
          name: this.quickOrganization.name,
          description: this.quickOrganization.description || ''
        })
        // Обновляем организации для модалки команды
        await this.loadQuickOrganizations()
        this.quickTeam.organization_id = res.data?.id
        this.showSuccess('Организация создана')
        const modal = Modal.getInstance(document.getElementById('quickOrganizationModal'))
        if (modal) modal.hide()
      } catch (e) {
        console.error('Ошибка создания организации', e)
        this.showError('Ошибка создания организации')
      } finally {
        this.loadingQuickOrganization = false
      }
    },
    
    async submitTask() {
      try {
        // Клиентская проверка дублей в текущем проекте и ветке родителя
        const title = (this.currentTask.title || '').trim()
        if (title && this.currentTask.project_id) {
          try {
            const resp = await projectManagementApi.getTasks({ project_id: this.currentTask.project_id })
            const list = resp.data.results || resp.data || []
            const parentId = this.currentTask.parent_id || null
            const norm = (s) => (s || '').toString().trim().replace(/\s+/g,' ').toLowerCase()
            const target = norm(title)
            const isDuplicate = list.some(t => {
              const sameBranch = (parentId ? (t.parent === parentId || t.parent_id === parentId) : (!t.parent && !t.parent_id))
              if (!sameBranch) return false
              return norm(t.title) === target && (!this.isEditing || t.id !== this.currentTask.id)
            })
            if (isDuplicate) {
              this.showError('Задача с таким названием уже существует в этом проекте/ветке')
              return
            }
          } catch (_) {}
        }
        // Гарантируем, что все выбранные исполнители состоят в команде проекта
        if (!this.isEditing && this.currentTask?.project_id && Array.isArray(this.currentTask?.assignee_ids) && this.currentTask.assignee_ids.length) {
          try {
            const projectResp = await projectManagementApi.getProject(this.currentTask.project_id)
            const project = projectResp.data
            const teamUserIds = new Set()
            if (project?.owner?.id) teamUserIds.add(project.owner.id)
            if (project?.manager?.id) teamUserIds.add(project.manager.id)
            if (Array.isArray(project?.memberships)) {
              project.memberships.forEach(m => m?.user?.id && teamUserIds.add(m.user.id))
            }
            // Добавляем отсутствующих пользователей в команду и проект
            for (const uid of this.currentTask.assignee_ids) {
              if (!teamUserIds.has(uid)) {
                if (project?.team?.id) {
                  await projectManagementApi.addTeamMember(project.team.id, { user_id: uid, role: 'member' })
                }
                await projectManagementApi.addProjectMember(this.currentTask.project_id, { user_id: uid, role: 'member' })
                teamUserIds.add(uid)
              }
            }
          } catch (e) {
            // Если не удалось синхронизировать — продолжим, сервер вернёт понятную ошибку
          }
        }
        // Подготавливаем данные задачи, конвертируя пустые строки в null
        const taskData = {
          ...this.currentTask,
          project_id: this.currentTask.project_id || null,
          assignee_id: this.currentTask.assignee_id || null,
          assignee_ids: this.currentTask.assignee_ids || [],
          start_date: this.currentTask.start_date ? this.formatDateForAPI(this.currentTask.start_date) : null,
          due_date: this.currentTask.due_date ? this.formatDateForAPI(this.currentTask.due_date) : null,
          estimated_hours: this.currentTask.estimated_hours || null,
          parent_id: this.currentTask.parent_id || null
        }
        
        // organization_id не отправляем — на сервере берётся из выбранного проекта
        
        if (this.isEditing) {
          await projectManagementApi.updateTask(taskData.id, taskData)
        } else {
          await projectManagementApi.createTask(taskData)
        }
        
        // Закрываем модальное окно
        const modal = Modal.getInstance(document.getElementById('taskModal'))
        if (modal) modal.hide()
        
        // Перезагружаем список
        this.loadTasks()
        
        this.showSuccess(this.isEditing ? 'Задача обновлена' : 'Задача создана')
      } catch (error) {
        console.error('Ошибка сохранения задачи:', error)
        console.error('Детали ошибки:', error.response?.data)
        
        // Показываем детали ошибки
        let errorMessage = 'Ошибка сохранения задачи'
        
        if (error.response?.data) {
          if (typeof error.response.data === 'object') {
            const errors = []
            for (const [field, messages] of Object.entries(error.response.data)) {
              if (Array.isArray(messages)) {
                errors.push(`${field}: ${messages.join(', ')}`)
              } else {
                errors.push(`${field}: ${messages}`)
              }
            }
            if (errors.length > 0) {
              errorMessage += ':\n' + errors.join('\n')
            }
          } else {
            errorMessage += ': ' + error.response.data
          }
        }
        
        this.showError(errorMessage)
      }
    },
    
    deleteTask(task) {
      this.currentTask = task
      this.confirmDeleteTask()
    },
    
    async confirmDeleteTask() {
      const confirmed = await this.showConfirmDialog({
        title: 'Удаление задачи',
        message: `Вы уверены, что хотите удалить задачу "${this.currentTask.title}"?`,
        confirmText: 'Удалить',
        cancelText: 'Отмена',
        variant: 'danger'
      })
      
      if (confirmed) {
        try {
          await projectManagementApi.deleteTask(this.currentTask.id)
          
          // Закрываем модальное окно если открыто
          const modal = Modal.getInstance(document.getElementById('taskModal'))
          if (modal) modal.hide()
          
          this.closeConfirmDialog()
          
          // Перезагружаем список
          this.loadTasks()
          
          this.showSuccess('Задача удалена')
        } catch (error) {
          console.error('Ошибка удаления задачи:', error)
          this.closeConfirmDialog()
          this.showError('Ошибка удаления задачи')
        }
      }
    },
    
    getStatusClass(status) {
      const classes = {
        'todo': 'bg-secondary',
        'in_progress': 'bg-info',
        'review': 'bg-warning text-dark',
        'done': 'bg-success',
        'cancelled': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },
    
    getStatusText(status) {
      const statusObj = this.taskStatuses.find(s => s.code === status)
      return statusObj ? statusObj.name : status
    },
    
    getPriorityClass(priority) {
      const classes = {
        'low': 'bg-light text-dark',
        'medium': 'bg-primary',
        'high': 'bg-warning text-dark',
        'urgent': 'bg-danger'
      }
      return classes[priority] || 'bg-light text-dark'
    },
    
    getPriorityText(priority) {
      const priorityObj = this.taskPriorities.find(p => p.code === priority)
      return priorityObj ? priorityObj.name : priority
    },
    
    getDueDateClass(dueDate, status) {
      if (!dueDate) return 'text-muted'
      if (status === 'done') return 'text-muted'
      
      const now = new Date()
      const due = new Date(dueDate)
      
      if (due < now) return 'text-danger fw-bold'
      if (due - now < 24 * 60 * 60 * 1000) return 'text-warning fw-bold'
      return 'text-muted'
    },
    
    formatDate(date) {
      if (!date) return 'Не указан'
      return new Date(date).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    },
    
    formatDateTime(date) {
      if (!date) return 'Не указана'
      return new Date(date).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    formatDateTimeLocal(date) {
      if (!date) return ''
      return new Date(date).toISOString().slice(0, 16)
    },
    formatDateForAPI(dateString) {
      if (!dateString) return null
      // Если уже ISO со временем — нормализуем секунды и таймзону
      if (dateString.includes('T')) {
        let s = dateString
        // Добавим секунды если их нет (YYYY-MM-DDTHH:MM)
        if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(s)) {
          s += ':00'
        }
        // Если нет таймзоны — преобразуем в локальную ISO с оффсетом
        if (!s.includes('Z') && !/[+-]\d{2}:?\d{2}$/.test(s)) {
          const d = new Date(s)
          const offsetMinutes = d.getTimezoneOffset()
          const offsetHours = Math.floor(Math.abs(offsetMinutes) / 60)
          const offsetMins = Math.abs(offsetMinutes % 60)
          const sign = offsetMinutes <= 0 ? '+' : '-'
          const tz = `${sign}${String(offsetHours).padStart(2, '0')}:${String(offsetMins).padStart(2, '0')}`
          return s + tz
        }
        return s
      }
      // Иначе считаем локальной датой и конвертируем в ISO
      const d = new Date(dateString)
      return d.toISOString()
    },
    
    truncateText(text, maxLength) {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    },
    
    getAvatarUrl(user) {
      // Используем локальную утилиту для генерации аватаров
      return getAvatarUrl(user, 32)
    },

    roleText(role) {
      const map = { member: 'Участник', lead: 'Ведущий', observer: 'Наблюдатель' }
      return map[role] || role
    },

    // Обработка URL параметров (только сценарий автосоздания)
    handleUrlParams() {
      const query = this.$route.query
      
      // Автоматическое создание задачи, если есть соответствующие параметры
      if (query.create === 'task') {
        // Небольшая задержка для завершения инициализации
        setTimeout(() => {
          this.createTask()
          
          // Если указан проект, предустанавливаем его
          if (query.project && this.projects.length > 0) {
            this.currentTask.project_id = query.project
          }
        }, 500)
      }
    },

    goToProject() {
      if (this.selectedTask.project) {
        // Закрываем модальное окно перед переходом
        const modal = Modal.getInstance(document.getElementById('taskViewModal'))
        if (modal) {
          modal.hide()
        }
        
        // Делаем переход после небольшой задержки, чтобы модальное окно успело закрыться
        setTimeout(() => {
          this.$router.push(`/crm/project-management/project/${this.selectedTask.project.id}`)
        }, 300)
      }
    },
    focusTaskInProjectTree(task) {
      if (!task?.project?.id || !task?.id) return
      const projectId = task.project.id
      // переходим на страницу проекта с параметром, чтобы автофокусить задачу в дереве
      this.$router.push({
        path: `/crm/project-management/project/${projectId}`,
        query: { focusTaskId: task.id }
      })
    },
    openProjectTree() {
      const pid = this.filters.project
      if (!pid) return
      this.$router.push({ path: `/crm/project-management/project/${pid}` })
    },
    openProjectList() {
      const pid = this.filters.project
      if (!pid) return
      // остаёмся на этой странице — кнопка служит подсказкой; если пришли из дерева, URL-параметр projectFilter уже учитывается
    },
    toggleView(val) {
      this.showTree = Boolean(val)
      this.pushRouteQuery()
    },
    expandAllRows() {
      if (!this.filters.project) return
      ;(this.tasks || []).forEach(t => t && this.expandedRows.add(t.id))
      this.rebuildVisibleRows()
    },
    collapseAllRows() {
      this.expandedRows.clear()
      this.rebuildVisibleRows()
    },
    resetFilters() {
      this.filters = {
        search: '',
        status: '',
        priority: '',
        project: this.filters.project || '',
        assignee: '',
        ordering: '-created_at',
        my_tasks: false,
        parent_filter: '',
        page_size: this.filters.page_size || 20
      }
      this.pagination.current_page = 1
      this.pushRouteQuery()
      this.loadTasks()
    },
    pushRouteQuery() {
      try {
        const q = { ...this.$route.query }
        if (this.filters.project) q.project = this.filters.project; else delete q.project
        q.my_tasks = this.filters.my_tasks ? '1' : undefined
        q.status = this.filters.status || undefined
        q.priority = this.filters.priority || undefined
        q.assignee = this.filters.assignee || undefined
        q.ordering = this.filters.ordering || undefined
        q.parent_filter = this.filters.parent_filter || undefined
        q.search = this.filters.search || undefined
        q.view = this.showTree ? 'tree' : undefined
        q.page = this.pagination.current_page > 1 ? String(this.pagination.current_page) : undefined
        q.page_size = this.filters.page_size && this.filters.page_size !== 20 ? String(this.filters.page_size) : undefined
        this.$router.replace({ query: q })
      } catch {}
    }
  }
}
</script>

<style scoped lang="scss">
@import './project-management.scss';

.tasks-list {
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

.tasks-table-wrapper {
  @include pm-card;
  padding: 0;
  overflow: hidden;
  
  .table-responsive {
    overflow-x: auto;
    overflow-y: visible;
  }
}

.tasks-table {
  margin-bottom: 0;
  table-layout: fixed;
  thead th { position: sticky; top: 0; z-index: 1; }
  
  thead {
    background: var(--bs-light);
    
    th {
      border-top: none;
      border-bottom: 2px solid var(--bs-border-color);
      font-weight: $font-weight-bold;
      font-size: 0.75rem;
      color: var(--bs-secondary-color);
      padding: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      
      &:first-child {
        width: 20%;
      }
      &:nth-child(2) {
        width: 15%;
        min-width: 120px;
      }
      &:nth-child(3) {
        width: 15%;
        min-width: 120px;
      }
      &:nth-child(4) {
        width: 12%;
      }
      &:nth-child(5) {
        width: 10%;
      }
      &:nth-child(6) {
        width: 12%;
      }
      &:nth-child(7) {
        width: 16%;
      }
      &:last-child {
        width: 10%;
        text-align: center;
      }
    }
  }
  
  .task-row {
    cursor: pointer;
    transition: all $pm-transition;
    
    &:hover {
      background-color: var(--bs-light);
    }
    
    td {
      vertical-align: middle;
      padding: 0.75rem;
      border-bottom: 1px solid var(--bs-gray-200);
      overflow: hidden;
      word-wrap: break-word;
      
      &.task-cell-main {
        white-space: normal;
      }
      
      &.project-cell,
      &.hierarchy-cell,
      &.actions-cell {
        white-space: nowrap;
        text-overflow: ellipsis;
      }
    }
  }
  
  .task-cell-main {
    .task-title {
      font-size: $font-size-usual;
      font-weight: $font-weight-bold;
      color: var(--bs-heading-color);
      margin-bottom: 0.25rem;
    }
    
    .task-description {
      font-size: $font-size-small;
      color: var(--bs-secondary-color);
      line-height: 1.5;
      margin-bottom: 0;
    }
    .task-meta-inline {
      font-size: 0.75rem;
      color: var(--bs-secondary-color);
      display: flex;
      gap: 8px;
      align-items: center;
    }
    
    .task-badges {
      display: flex;
      gap: 0.25rem;
      margin-top: 0.5rem;
      
      .badge {
        font-size: 0.65rem;
        padding: 0.2rem 0.4rem;
      }
    }
  }
  
  .project-cell {
    .project-info {
      .project-badge {
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        padding: 0.35rem 0.65rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
        max-width: 100%;
        border: none;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        
        .project-name {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          display: inline-block;
          max-width: 140px;
        }
        
        &:hover {
          transform: translateY(-1px);
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        }
        
        i {
          margin-right: 0.3rem;
          font-size: 0.7rem;
        }
      }
    }
    
    .project-empty {
      font-size: 0.875rem;
      font-style: italic;
      color: var(--bs-secondary);
    }
  }
  
  .hierarchy-cell {
    .hierarchy-info {
      text-align: center;
      
      .badge {
        font-size: 0.65rem;
        padding: 0.25rem 0.5rem;
        margin-bottom: 0.25rem;
      }
      
      .parent-task-title {
        font-size: 0.75rem;
        color: var(--bs-secondary);
        margin-top: 0.25rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100px;
        display: block;
      }
    }
    
    .text-muted {
      font-size: 0.75rem;
      text-align: center;
      display: block;
      
      i {
        font-size: 0.6rem;
      }
    }
  }
  
  .assignee-info {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    max-width: 100%;
    
    .assignee-avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid var(--bs-gray-200);
      flex-shrink: 0;
    }
    
    .assignee-name {
      font-size: 0.8rem;
      color: var(--bs-heading-color);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
    }
  }
}

.badge {
  @include pm-badge;
}

.btn {
  @include pm-button;
}

// Чипы выбранных исполнителей
.assignee-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background: var(--bs-gray-200);
  color: var(--bs-heading-color);
  border-radius: 999px;
  font-size: 0.75rem;
}
[data-bs-theme='dark'] .assignee-chip {
  background: rgba(255,255,255,0.12);
  color: #e9ecf1;
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

// Модальные окна
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

// Модальное окно просмотра
.info-section {
  margin-bottom: 1.5rem;
  
  h6 {
    font-size: $font-size-micro;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1rem;
  }
  
  .info-list {
    .info-item {
      display: flex;
      align-items: center;
      margin-bottom: 0.75rem;
      
      i {
        width: 20px;
        text-align: center;
      }
    }
  }
}

.time-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--bs-light);
  border-radius: $radius-small;
  
  i {
    font-size: 2rem;
  }
  
  .time-value {
    font-size: 1.5rem;
    font-weight: $font-weight-bold;
    color: var(--bs-heading-color);
  }
  
  .time-label {
    font-size: $font-size-small;
    color: var(--bs-secondary-color);
  }
}

// Новые стили для улучшенного модального окна
.task-view-content {
  .icon-wrapper {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .icon-sm {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .info-card {
    transition: all 0.2s ease;
    border-color: var(--bs-gray-300) !important;
    
    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      transform: translateY(-1px);
    }
  }
  
  .project-color-bar {
    height: 3px;
    border-radius: 2px;
    width: 100%;
  }
  
  .description-section {
    background-color: var(--bs-gray-100) !important;
    border: 1px solid var(--bs-gray-200);
  }
  
  .meta-info {
    background-color: var(--bs-gray-100) !important;
    border: 1px solid var(--bs-gray-200);
    
    small {
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
  }
}

.time-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--bs-light);
  border-radius: $radius-small;
  
  i {
    font-size: 2rem;
  }
  
  .time-value {
    font-size: 1.5rem;
    font-weight: $font-weight-bold;
    color: var(--bs-heading-color);
  }
  
  .time-label {
    font-size: $font-size-small;
    color: var(--bs-secondary-color);
  }
}

// Классы для сроков
.text-danger {
  &.fw-bold {
    font-weight: $font-weight-bold !important;
  }
}

// Стили для кнопок действий
.actions-cell {
  .action-buttons {
    display: flex;
    gap: 0.25rem;
    justify-content: center;
    
    .btn-action {
      padding: 0.375rem 0.5rem;
      border-radius: 6px;
      font-size: 0.875rem;
      transition: all 0.2s ease;
      border-width: 1px;
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
      }
      
      i {
        font-size: 0.85rem;
      }
    }
    
    .btn-primary {
      &:hover {
        opacity: 0.9;
        transform: translateY(-1px);
      }
    }
    
    .btn-danger {
      &:hover {
        opacity: 0.9;
        transform: translateY(-1px);
      }
    }
  }
}

// Адаптивность
@media (max-width: 768px) {
  .tasks-list {
    padding: 1rem;
  }
  
  .pm-page-header {
    flex-direction: column;
    gap: 1rem;
    
    h2 {
      font-size: $font-size-h2;
    }
  }
  
  .tasks-table-wrapper {
    overflow-x: auto;
    
    .tasks-table {
      min-width: 800px;
    }
  }
}
</style> 