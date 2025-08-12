<template>
  <div class="project-detail-page">
    <!-- Заголовок страницы -->
    <div class="page-header">
      <div class="header-content">
        <nav aria-label="breadcrumb" class="breadcrumb-nav">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/crm/project-management" class="breadcrumb-link">
                <Home :size="16" />
                <span>Управление проектами</span>
              </router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link :to="getBackRoute()" class="breadcrumb-link">
                {{ getBackRouteTitle() }}
              </router-link>
            </li>
            <li class="breadcrumb-item active">
              {{ project?.name || 'Загрузка...' }}
            </li>
          </ol>
        </nav>
        
        <div class="project-title-section">
          <div class="project-icon" v-if="project" :style="{ backgroundColor: project.color }">
            <ListTodo :size="24" color="white" />
          </div>
          <div class="project-title">
            <h1>{{ project?.name || 'Загрузка проекта...' }}</h1>
            <div class="project-meta-badges" v-if="project">
              <span class="badge status-badge" :class="getStatusClass(project.status)">
                {{ getStatusText(project.status) }}
              </span>
              <span class="badge priority-badge" :class="getPriorityClass(project.priority)">
                {{ getPriorityText(project.priority) }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="header-actions" v-if="project">
        <button class="btn btn-outline-primary" @click="editProject" title="Редактировать проект">
          <Edit :size="16" />
          <span>Редактировать</span>
        </button>
        <button class="btn btn-primary" @click="createTask" title="Добавить задачу">
          <Plus :size="16" />
          <span>Добавить задачу</span>
        </button>
      </div>
    </div>

    <!-- Состояние загрузки -->
    <div v-if="loading" class="loading-state">
      <div class="d-flex flex-column align-items-center justify-content-center py-5">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="text-muted">Загружаем данные проекта...</p>
      </div>
    </div>

    <!-- Состояние ошибки -->
    <div v-else-if="error" class="error-state">
      <AlertTriangle :size="48" class="error-icon" />
      <h3>Ошибка загрузки</h3>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="loadProject">Попробовать снова</button>
    </div>

    <!-- Основной контент -->
    <div v-else-if="project" class="project-content">
      <!-- Информационная секция -->
      <div class="info-section">
        <div class="info-grid">
          <!-- Основная информация о проекте -->
          <div class="info-card main-info">
            <div class="card-header">
              <Info :size="20" />
              <h3>Информация о проекте</h3>
            </div>
            <div class="card-body">
              <div class="description-section">
                <p class="description">{{ project.description || 'Описание отсутствует' }}</p>
              </div>
              
              <div class="meta-grid">
                <div class="meta-item">
                  <div class="meta-icon">
                    <Calendar :size="16" />
                  </div>
                  <div class="meta-content">
                    <span class="meta-label">Дата начала</span>
                    <span class="meta-value">{{ formatDate(project.start_date) || 'Не указана' }}</span>
                  </div>
                </div>
                
                <div class="meta-item">
                  <div class="meta-icon">
                    <Clock :size="16" />
                  </div>
                  <div class="meta-content">
                    <span class="meta-label">Дата окончания</span>
                    <span class="meta-value">{{ formatDate(project.end_date) || 'Не указана' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Статистика проекта -->
          <div class="info-card stats-card">
            <div class="card-header">
              <PieChart :size="20" />
              <h3>Статистика</h3>
            </div>
            <div class="card-body">
              <!-- Прогресс -->
              <div class="progress-section">
                <div class="progress-header">
                  <span>Общий прогресс</span>
                  <span class="progress-value">{{ project.progress || 0 }}%</span>
                </div>
                <div class="progress-bar-container">
                  <div class="progress-bar" 
                       :style="{ width: (project.progress || 0) + '%' }"
                       :class="getProgressClass(project.progress || 0)">
                  </div>
                </div>
              </div>
              
              <!-- Статистика задач -->
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-icon">
                    <ListTodo :size="20" />
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ project.task_count || 0 }}</div>
                    <div class="stat-label">Всего задач</div>
                  </div>
                </div>
                
                <div class="stat-item">
                  <div class="stat-icon completed">
                    <CheckCircle :size="20" />
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ project.completed_task_count || 0 }}</div>
                    <div class="stat-label">Выполнено</div>
                  </div>
                </div>
                
                <div class="stat-item">
                  <div class="stat-icon in-progress">
                    <Clock :size="20" />
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ (project.task_count || 0) - (project.completed_task_count || 0) }}</div>
                    <div class="stat-label">В работе</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Команда проекта -->
          <div class="info-card team-card" v-if="project">
            <div class="card-header">
              <Users :size="20" />
              <h3>Команда проекта</h3>
              <button class="btn btn-outline-primary btn-sm" @click="openTeamModal" title="Управление командой">
                <UserPlus :size="16" />
                <span>Добавить участника</span>
              </button>
            </div>
            <div class="card-body">

              
              <div class="team-members">
                <!-- Все участники команды проекта -->
                <div class="team-member" 
                     v-for="member in allProjectMembers" 
                     :key="`team-member-${member.type}-${member.id}`">
                  <img :src="getAvatarUrl(member.user)" 
                       :alt="getUserDisplayName(member.user)"
                       class="member-avatar">
                  <div class="member-info">
                    <div class="member-name">{{ getUserDisplayName(member.user) }}</div>
                    <div class="member-role" :class="member.roleClass">
                      {{ member.roleText }}
                      <span v-if="member.badges.length > 0" class="member-badges ms-2">
                        <span v-for="badge in member.badges" 
                              :key="badge.text" 
                              :class="badge.class"
                              class="badge me-1">
                          {{ badge.text }}
                        </span>
                      </span>
                    </div>
                  </div>
                  <div class="member-actions">
                    <button class="btn btn-delete-icon" 
                            v-if="member.canRemove"
                            @click="removeMember(member.originalMember)" 
                            title="Исключить из команды">
                      <UserMinus :size="14" />
                    </button>
                    <span v-else class="text-muted small d-inline-flex align-items-center" title="Нельзя исключить">
                      <Lock :size="14" />
                    </span>
                  </div>
                </div>
                
                <!-- Пустое состояние -->
                <div v-if="allProjectMembers.length === 0" 
                     class="empty-team">
                  <Users :size="32" class="empty-icon" />
                  <p>В команде проекта пока нет участников</p>
                  <button class="btn btn-primary btn-sm" @click="openTeamModal">
                    <UserPlus :size="16" />
                    <span>Добавить первого участника</span>
                  </button>
                </div>
              </div>
              
            </div>
          </div>
        </div>
      </div>

      <!-- Секция задач -->
      <div class="tasks-section">
        <div class="section-header">
          <div class="section-title">
            <ListTodo :size="24" />
            <h2>Задачи проекта</h2>
          </div>
          <div class="section-actions">
            <button class="btn btn-outline-primary" @click="toggleTaskView">
              <GitBranch :size="16" v-if="!showTaskTree" />
              <ListTodo :size="16" v-else />
              <span>{{ showTaskTree ? 'Список' : 'Дерево' }}</span>
            </button>
          <button class="btn btn-outline-secondary" @click="goToTasksList">
            <ListTodo :size="16" />
            <span>Список задач (общий)</span>
          </button>
            <button class="btn btn-outline-secondary" v-if="!showTaskTree" @click="focusTaskInTree()">
              <GitBranch :size="16" />
              <span>Показать выбранную задачу в дереве</span>
            </button>
            <button class="btn btn-primary" @click="createTask">
              <Plus :size="16" />
              <span>Добавить задачу</span>
            </button>
          </div>
        </div>
        
        <div class="tasks-content">
          <!-- Пустое состояние -->
          <div v-if="tasks.length === 0" class="empty-state">
            <ListTodo :size="64" class="empty-icon" />
            <h3>В проекте пока нет задач</h3>
            <p>Создайте первую задачу для начала работы</p>
            <button class="btn btn-primary btn-lg" @click="createTask">
              <Plus :size="20" />
              <span>Создать первую задачу</span>
            </button>
          </div>
          
          <!-- Таблица задач или дерево -->
          <div v-else>
            <div v-if="showTaskTree" class="task-tree-container">
              <ProjectTasksTree ref="tree" :project="project" :tasks="tasks" />
            </div>
            <div v-else class="tasks-table-container">
              <div class="table-responsive">
                <table class="tasks-table">
                  <thead>
                    <tr>
                      <th>Задача</th>
                      <th>Исполнитель</th>
                      <th>Статус</th>
                      <th>Приоритет</th>
                      <th>Срок</th>
                      <th>Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="task in tasks" :key="task.id" class="task-row">
                      <td class="task-cell">
                        <div class="task-info">
                          <h4 class="task-title">{{ task.title }}</h4>
                          <p class="task-description" v-if="task.description">
                            {{ truncateText(task.description, 100) }}
                          </p>
                        </div>
                      </td>
                      <td class="assignee-cell">
                        <div class="assignee-info" v-if="task.assignee">
                          <img :src="getAvatarUrl(task.assignee)"
                               :alt="getUserDisplayName(task.assignee)"
                               class="assignee-avatar">
                          <span class="assignee-name">{{ getUserDisplayName(task.assignee) }}</span>
                        </div>
                        <span v-else class="no-assignee">Не назначен</span>
                       <div v-if="task.assignee_roles && task.assignee_roles.length" class="mt-1 d-flex flex-wrap gap-1">
                         <span v-for="link in task.assignee_roles" :key="link.user?.id + '-' + link.role" class="badge rounded-pill bg-light text-dark">
                           {{ getUserDisplayName(link.user) }} — {{ getRoleText(link.role) }}
                         </span>
                       </div>
                      </td>
                      <td class="status-cell">
                        <span class="badge status-badge" :class="getTaskStatusClass(task.status)">
                          {{ getTaskStatusText(task.status) }}
                        </span>
                      </td>
                      <td class="priority-cell">
                        <span class="badge priority-badge" :class="getPriorityClass(task.priority)">
                          {{ getPriorityText(task.priority) }}
                        </span>
                      </td>
                      <td class="due-date-cell">
                        <span :class="getDueDateClass(task.due_date, task.status)">
                          <Clock :size="14" />
                          {{ formatDate(task.due_date) || '-' }}
                        </span>
                      </td>
                      <td class="actions-cell">
                        <div class="action-buttons">
                          <button class="btn btn-edit-icon" @click="createSubTask(task)" title="Добавить подзадачу">
                            <Plus :size="14" />
                          </button>
                          <button class="btn btn-edit-icon" @click="editTask(task)" title="Редактировать">
                            <Edit :size="14" />
                          </button>
                          <button class="btn btn-delete-icon" @click="deleteTask(task)" title="Удалить">
                            <Trash2 :size="14" />
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
      </div>
    </div>

    <!-- Модальные окна остаются без изменений -->
    <!-- Модальное окно редактирования проекта -->
    <div class="modal fade" id="projectModal" tabindex="-1" aria-labelledby="projectModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="projectModalLabel">Редактировать проект</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitProject">
              <div class="mb-3">
                <label class="form-label">Название проекта *</label>
                <input type="text" class="form-control" v-model="currentProject.name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Описание</label>
                <textarea class="form-control" rows="3" v-model="currentProject.description"></textarea>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Дата начала</label>
                    <input type="date" class="form-control" v-model="currentProject.start_date">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Дата окончания</label>
                    <input type="date" class="form-control" v-model="currentProject.end_date">
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Статус</label>
                    <select class="form-select" v-model="currentProject.status" :disabled="loadingStatuses">
                      <option v-if="loadingStatuses">Загрузка...</option>
                      <option v-else v-for="status in projectStatuses" :key="status.id" :value="status.code">
                        {{ status.name }}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Приоритет</label>
                    <select class="form-select" v-model="currentProject.priority" :disabled="loadingStatuses">
                      <option v-if="loadingStatuses">Загрузка...</option>
                      <option v-else v-for="priority in projectPriorities" :key="priority.id" :value="priority.code">
                        {{ priority.name }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Цвет проекта</label>
                <input type="color" class="form-control form-control-color" v-model="currentProject.color">
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отменить</button>
            <button type="button" class="btn btn-primary" @click="submitProject" :disabled="!currentProject.name">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования задачи -->
    <div class="modal fade" id="taskModal" tabindex="-1" aria-labelledby="taskModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="taskModalLabel">
              {{ isEditingTask ? 'Редактировать задачу' : 'Создать задачу' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitTask">
              <div class="mb-3">
                <label class="form-label fw-bold d-flex align-items-center gap-2"><FileText :size="16" /> Название задачи <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentTask.title" required placeholder="Короткое и понятное название">
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold d-flex align-items-center gap-2"><GitBranch :size="16" /> Родительская задача</label>
                <select class="form-select" v-model="currentTask.parent_id">
                  <option value="">Без родительской задачи</option>
                  <option v-for="task in availableParentTasks" :key="task.id" :value="task.id">
                    {{ task.title }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold d-flex align-items-center gap-2"><Users :size="16" /> Исполнители</label>
                <div v-if="(currentTask.assignee_ids||[]).length" class="mb-2 d-flex flex-wrap gap-2">
                  <span v-for="uid in currentTask.assignee_ids" :key="`chip-${uid}`" class="assignee-chip">
                    {{ getUserDisplayName(availableUsers.find(u => u.id === uid)) }}
                  </span>
                </div>
                <input class="form-control mb-2" type="text" v-model="assigneesSearch" placeholder="Поиск по логину/ФИО" @input="filterAvailableUsers" />
                <div class="border rounded p-2" style="max-height: 220px; overflow: auto;">
                  <div class="form-check" v-for="user in filteredAvailableUsers" :key="`cb-${user.id}`">
                    <input class="form-check-input" type="checkbox" :id="`assignee-${user.id}`" :value="user.id" v-model="currentTask.assignee_ids">
                    <label class="form-check-label" :for="`assignee-${user.id}`">{{ getUserDisplayName(user) }}</label>
                  </div>
                </div>
                <div class="mt-2">
                  <label class="form-label">Основной исполнитель</label>
                  <select class="form-select" v-model="currentTask.assignee_id" :disabled="!(currentTask.assignee_ids && currentTask.assignee_ids.length)">
                    <option value="">Не назначен</option>
                    <option v-for="uid in currentTask.assignee_ids" :key="`main-${uid}`" :value="uid">
                      {{ getUserDisplayName(availableUsers.find(u => u.id === uid)) }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label fw-bold d-flex align-items-center gap-2"><ListTodo :size="16" /> Статус</label>
                  <select class="form-select" v-model="currentTask.status" :disabled="loadingStatuses">
                    <option v-if="loadingStatuses">Загрузка...</option>
                    <option v-else v-for="status in taskStatuses" :key="status.id" :value="status.code">
                      {{ status.name }}
                    </option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-bold d-flex align-items-center gap-2"><Flag :size="16" /> Приоритет</label>
                  <select class="form-select" v-model="currentTask.priority" :disabled="loadingStatuses">
                    <option v-if="loadingStatuses">Загрузка...</option>
                    <option v-else v-for="priority in taskPriorities" :key="priority.id" :value="priority.code">
                      {{ priority.name }}
                    </option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-bold d-flex align-items-center gap-2"><Clock :size="16" /> Оценка, ч</label>
                  <input type="number" class="form-control" step="0.5" v-model="currentTask.estimated_hours">
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
                <label class="form-label fw-bold d-flex align-items-center gap-2"><FileText :size="16" /> Описание</label>
                <textarea class="form-control" rows="3" v-model="currentTask.description" placeholder="Коротко опишите задачу"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отменить</button>
            <button type="button" class="btn btn-primary" @click="submitTask" :disabled="!currentTask.title">
              {{ isEditingTask ? 'Сохранить' : 'Создать задачу' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно управления командой -->
    <div class="modal fade" id="teamModal" tabindex="-1" aria-labelledby="teamModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="teamModalLabel">Управление командой проекта</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <h6>Добавить участника</h6>
                <div class="add-member-form">
                  <div class="mb-3">
                    <label class="form-label">Выберите пользователя</label>
                    <select class="form-select" v-model="selectedUserId">
                      <option value="">Выберите пользователя</option>
                      <option v-for="user in availableUsers" 
                              :key="user.id" 
                              :value="user.id">
                        {{ getUserDisplayName(user) }}
                      </option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Роль в проекте</label>
                    <select class="form-select" v-model="selectedRole">
                      <option value="member">Участник</option>
                      <option value="lead">Ведущий</option>
                      <option value="observer">Наблюдатель</option>
                    </select>
                  </div>
                  <button class="btn btn-primary d-inline-flex align-items-center gap-2" 
                          @click="addMember" 
                          :disabled="!selectedUserId || loadingTeamAction">
                    <Loader2 v-if="loadingTeamAction" class="me-1" :size="14" />
                    <span>Добавить в команду</span>
                  </button>
                </div>
              </div>
              <div class="col-md-6">
                <h6 class="mb-2">Текущая команда</h6>
                <div class="current-team">
                  
                  <!-- Владелец -->
                  <div class="team-member-modal" v-if="project && project.owner">
                    <img :src="getAvatarUrl(project.owner)" 
                         :alt="getUserDisplayName(project.owner)"
                         class="member-avatar-small">
                    <div class="member-info-modal">
                      <div class="member-name">{{ getUserDisplayName(project.owner) }}</div>
                      <div class="member-role owner-role">Владелец</div>
                    </div>
                  </div>
                  
                  <!-- Менеджер -->
                  <div class="team-member-modal" v-if="project && project.manager && project.manager.id !== project.owner?.id">
                    <img :src="getAvatarUrl(project.manager)" 
                         :alt="getUserDisplayName(project.manager)"
                         class="member-avatar-small">
                    <div class="member-info-modal">
                      <div class="member-name">{{ getUserDisplayName(project.manager) }}</div>
                      <div class="member-role manager-role">Менеджер проекта</div>
                    </div>
                  </div>
                  
                  <!-- Участники -->
                  <template v-for="member in filteredTeamMembers" :key="member.id">
                    <div class="team-member-modal" v-if="member && member.user">
                      <img :src="getAvatarUrl(member.user)" 
                           :alt="getUserDisplayName(member.user)"
                           class="member-avatar-small">
                      <div class="member-info-modal">
                        <div class="member-name">{{ getUserDisplayName(member.user) }}</div>
                        <div class="member-role" :class="getRoleClass(member.role)">{{ getRoleText(member.role) }}</div>
                      </div>
                      <button class="btn btn-delete-icon" @click="removeMember(member)" title="Исключить">
                        <UserMinus :size="12" />
                      </button>
                    </div>
                  </template>
                  
                  <div v-if="project && filteredTeamMembers.length === 0 && !project.owner && !project.manager" 
                       class="text-muted text-center">
                    <small>Пока нет участников</small>
                  </div>

                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap'
import { Edit, Trash2, Plus, Home, Info, PieChart, ListTodo, Calendar, Clock, Users, CheckCircle, AlertTriangle, UserPlus, UserMinus, GitBranch, FileText, Flag, Lock, Loader2 } from 'lucide-vue-next'
import projectManagementApi from '@/modules/crm/project-management/js/projectManagementApi.js'
import { useNotifications } from '@/modules/lms/composables/useNotifications'
import { getAvatarUrl } from '@/modules/cms/js/avatarUtils.js'
import ProjectTasksTree from './ProjectTasksTree.vue'

export default {
  name: 'ProjectDetail',
  components: {
    Edit,
    Trash2,
    Plus,
    Home,
    Info,
    PieChart,
    ListTodo,
    Calendar,
    Clock,
    Users,
    CheckCircle,
    AlertTriangle,
    UserPlus,
    UserMinus,
    GitBranch,
    ProjectTasksTree
  },
  setup() {
    const { showSuccess, showError, showConfirmDialog, closeConfirmDialog } = useNotifications()
    return { showSuccess, showError, showConfirmDialog, closeConfirmDialog }
  },
  data() {
    return {
      loading: false,
      error: null,
      project: null,
      tasks: [],
      showTaskTree: true,
      availableParentTasks: [],
      users: [],
      assigneesSearch: '',
      filteredAvailableUsers: [],
      currentTask: {
        title: '',
        description: '',
        assignee_id: '',
        assignee_ids: [],
        status: 'todo',
        priority: 'medium',
        start_date: '',
        due_date: '',
        estimated_hours: null,
        parent_id: null
      },
      currentProject: {
        name: '',
        description: '',
        start_date: '',
        end_date: '',
        status: 'planning',
        priority: 'medium',
        color: '#007bff'
      },
      isEditingTask: false,
      isEditingProject: false,
      // Динамические данные для статусов и приоритетов
      projectStatuses: [],
      projectPriorities: [],
      taskStatuses: [],
      taskPriorities: [],
      loadingStatuses: false,
      // Управление командой проекта
      selectedUserId: '',
      selectedRole: 'member',
      loadingTeamAction: false
    }
  },
  async mounted() {
    await Promise.all([
      this.loadUsers(),
      this.loadStatusesAndPriorities()
    ])
    await this.loadProjectData()
    // если пришёл запрос сфокусировать задачу в дереве
    const focusId = this.$route.query.focusTaskId
    if (focusId) {
      const t = this.tasks.find(x => String(x.id) === String(focusId)) || { id: focusId }
      await this.focusTaskInTree(t)
    }
  },
  computed: {
    availableUsers() {
      if (!this.users || !this.project) return []
      // показываем только участников проекта/команды
      const teamUserIds = new Set()
      if (this.project?.owner?.id) teamUserIds.add(this.project.owner.id)
      if (this.project?.manager?.id) teamUserIds.add(this.project.manager.id)
      if (this.project?.memberships && Array.isArray(this.project.memberships)) {
        this.project.memberships.forEach(m => m?.user?.id && teamUserIds.add(m.user.id))
      }
      return this.users.filter(u => u?.id && teamUserIds.has(u.id))
    },
    // триггер для синхронизации от availableUsers
    availableUsersSyncTrigger() {
      // при каждом пересчёте availableUsers — пересобираем фильтрованную выборку
      this.filteredAvailableUsers = this.availableUsers
      return true
    },

    allTeamMembers() {
      if (!this.project?.memberships || !Array.isArray(this.project.memberships)) return []
      
      return this.project.memberships.filter(member => {
        // Строгая проверка валидности участника
        return member && 
               typeof member === 'object' && 
               member.user && 
               typeof member.user === 'object' && 
               member.user.id && 
               member.id
      })
    },

    filteredTeamMembers() {
      if (!this.project?.memberships || !Array.isArray(this.project.memberships)) return []
      
      return this.project.memberships.filter(member => {
        // Строгая проверка валидности member
        if (!member || typeof member !== 'object') return false
        if (!member.user || typeof member.user !== 'object') return false
        if (!member.user.id || !member.id) return false
        
        // Исключаем владельца и менеджера (они отображаются отдельно)
        const isOwner = this.project.owner?.id === member.user.id
        const isManager = this.project.manager?.id === member.user.id
        
        return !isOwner && !isManager
      })
    },

    allProjectMembers() {
      if (!this.project) return []
      
      const members = []
      const processedUserIds = new Set()
      
             // 1. Добавляем владельца (если есть)
       if (this.project.owner) {
         members.push({
           id: `owner-${this.project.owner.id}`,
           type: 'owner',
           user: this.project.owner,
           roleText: 'Владелец проекта',
           roleClass: 'owner-role',
           badges: [],
           canRemove: false,
           originalMember: null
         })
         processedUserIds.add(this.project.owner.id)
       }
      
      // 2. Добавляем менеджера (если есть и не совпадает с владельцем)
      if (this.project.manager && !processedUserIds.has(this.project.manager.id)) {
        members.push({
          id: `manager-${this.project.manager.id}`,
          type: 'manager',
          user: this.project.manager,
          roleText: 'Менеджер проекта',
          roleClass: 'manager-role',
          badges: [],
          canRemove: false,
          originalMember: null
        })
        processedUserIds.add(this.project.manager.id)
      }
      
      // 3. Добавляем всех участников команды
      if (this.project.memberships && Array.isArray(this.project.memberships)) {
        this.project.memberships.forEach(member => {
          if (member && 
              typeof member === 'object' && 
              member.user && 
              typeof member.user === 'object' && 
              member.user.id && 
              member.id) {
            const badges = []
            let roleText = this.getRoleText(member.role)
            let roleClass = this.getRoleClass(member.role)
            
            // Если пользователь уже обработан как владелец/менеджер, добавляем дополнительные бейджи
            if (processedUserIds.has(member.user.id)) {
              // Находим существующего участника и добавляем дополнительную роль
              const existingMember = members.find(m => m.user.id === member.user.id)
              if (existingMember) {
                existingMember.badges.push({
                  text: this.getRoleText(member.role),
                  class: this.getRoleBadgeClass(member.role)
                })
                existingMember.originalMember = member // Сохраняем для возможного удаления
              }
            } else {
              // Добавляем как нового участника
              members.push({
                id: `member-${member.id}`,
                type: 'member',
                user: member.user,
                roleText: roleText,
                roleClass: roleClass,
                badges: [],
                canRemove: true,
                originalMember: member
              })
              processedUserIds.add(member.user.id)
            }
          }
        })
      }
      
      return members
    }
  },
  watch: {
    '$route'() {
      this.loadProjectData()
    }
  },
  methods: {
    toggleTaskView() {
      this.showTaskTree = !this.showTaskTree
      if (this.showTaskTree) {
        // при включении дерева подгружаем его с API
        this.loadProjectTree()
      } else {
        // возвращаемся к списку задач проекта
        this.loadProjectData()
      }
    },
    goToTasksList() {
      // Переход на общий список задач (табличный режим) с фильтром по проекту
      if (this.project?.id) {
        this.$router.push({ path: '/crm/project-management/tasks', query: { projectFilter: this.project.id } })
      } else {
        this.$router.push('/crm/project-management/tasks')
      }
    },
    async focusTaskInTree(task = null) {
      try {
        if (!this.project?.id) return
        const t = task || this.selectedTask || this.tasks?.[0]
        if (!t?.id) return
        // получаем путь от корня до задачи
        const res = await projectManagementApi.client.get(`/crm/tasks/${t.id}/path/`)
        const path = (res.data?.path || []).map(n => n.id)
        this.showTaskTree = true
        // дождаться рендера дерева
        this.$nextTick(async () => {
          const tree = this.$refs.tree
          if (tree && typeof tree.expandPathTo === 'function') {
            await tree.expandPathTo(path)
          }
        })
      } catch (e) {
        console.error('Не удалось выделить задачу в дереве', e)
      }
    },
    async loadProjectData() {
      const projectId = this.$route.params.id
      if (!projectId) {
        this.error = 'ID проекта не указан'
        return
      }

      this.loading = true
      this.error = null

      try {
        // Загружаем проект и задачи параллельно
         const [projectRes, tasksRes] = await Promise.all([
           projectManagementApi.getProject(projectId),
           projectManagementApi.getProjectTasks(projectId),
         ])
         this.project = projectRes.data
         this.tasks = Array.isArray(tasksRes.data) ? tasksRes.data.filter(t => t && t.id) : []
        // После загрузки проекта ограничим доступных пользователей командой
        const teamUserIds = new Set()
        if (this.project?.owner?.id) teamUserIds.add(this.project.owner.id)
        if (this.project?.manager?.id) teamUserIds.add(this.project.manager.id)
        if (Array.isArray(this.project?.memberships)) {
          this.project.memberships.forEach(m => m?.user?.id && teamUserIds.add(m.user.id))
        }
        const allowed = this.users.filter(u => u?.id && teamUserIds.has(u.id))
        // Сжать выбранные значения под разрешённых
        const allowedIds = new Set(allowed.map(u => u.id))
        this.currentTask.assignee_ids = (this.currentTask.assignee_ids || []).filter(id => allowedIds.has(id))
        if (this.currentTask.assignee_id && !allowedIds.has(this.currentTask.assignee_id)) {
          this.currentTask.assignee_id = ''
        }
        // Фоновая подгрузка ролей исполнителей, чтобы не блокировать интерфейс
        this.enrichAssigneeRolesInBatches(this.tasks, 8)

        // Обновляем прогресс проекта
        this.updateProjectProgress()
      } catch (error) {
        console.error('Ошибка загрузки проекта:', error)
        this.error = 'Ошибка загрузки данных проекта'
      } finally {
        this.loading = false
      }
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
          }
        }
        const workers = Array.from({ length: Math.max(1, concurrency) }, runWorker)
        await Promise.allSettled(workers)
      } catch (e) {
        console.error('Ошибка подгрузки ролей исполнителей', e)
      }
    },

    async loadProjectTree() {
      if (!this.project?.id) return
      try {
        const url = `/crm/tasks/project_tree/` // baseURL уже содержит /api
        const res = await projectManagementApi.client.get(url, { params: { project_id: this.project.id } })
        const tree = res.data?.tree || []
        // Преобразуем дерево в плоский список для текущих компонентов, если нужно
        // Пока просто сохраняем как есть для ProjectTasksTree
        this.tasks = tree
      } catch (e) {
        console.error('Ошибка загрузки дерева задач проекта', e)
      }
    },

    async loadUsers() {
      try {
        const response = await projectManagementApi.getUsers()
        const users = Array.isArray(response.data.results) ? response.data.results : 
                      Array.isArray(response.data) ? response.data : []
        
        // Фильтруем только валидных пользователей
        this.users = users.filter(user => user && user.id)
        this.filteredAvailableUsers = this.availableUsers
      } catch (error) {
        console.error('Ошибка загрузки пользователей:', error)
        this.users = []
      }
    },
    filterAvailableUsers() {
      const q = (this.assigneesSearch || '').toLowerCase().trim()
      const source = this.availableUsers || []
      if (!q) {
        this.filteredAvailableUsers = source
        return
      }
      this.filteredAvailableUsers = source.filter(u => {
        const login = (u.username || '').toLowerCase()
        const full = (u.full_name || `${u.first_name || ''} ${u.last_name || ''}`.trim()).toLowerCase()
        return login.includes(q) || full.includes(q)
      })
    },

    async loadStatusesAndPriorities() {
      try {
        this.loadingStatuses = true
        const [projectStatusesRes, projectPrioritiesRes, taskStatusesRes, taskPrioritiesRes] = await Promise.all([
          projectManagementApi.getProjectStatuses(),
          projectManagementApi.getProjectPriorities(),
          projectManagementApi.getTaskStatuses(),
          projectManagementApi.getTaskPriorities()
        ])
        
        this.projectStatuses = Array.isArray(projectStatusesRes.data) ? 
          projectStatusesRes.data.filter(s => s.is_active) : 
          (projectStatusesRes.data.results || []).filter(s => s.is_active)
          
        this.projectPriorities = Array.isArray(projectPrioritiesRes.data) ? 
          projectPrioritiesRes.data.filter(p => p.is_active) : 
          (projectPrioritiesRes.data.results || []).filter(p => p.is_active)

        this.taskStatuses = Array.isArray(taskStatusesRes.data) ? 
          taskStatusesRes.data.filter(s => s.is_active) : 
          (taskStatusesRes.data.results || []).filter(s => s.is_active)
          
        this.taskPriorities = Array.isArray(taskPrioritiesRes.data) ? 
          taskPrioritiesRes.data.filter(p => p.is_active) : 
          (taskPrioritiesRes.data.results || []).filter(p => p.is_active)
      } catch (error) {
        console.error('Ошибка загрузки статусов и приоритетов:', error)
        // Fallback к жестко заданным значениям
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

    editProject() {
      if (!this.project) return
      
      this.isEditingProject = true
      this.currentProject = {
        id: this.project.id,
        name: this.project.name,
        description: this.project.description,
        start_date: this.project.start_date || '',
        end_date: this.project.end_date || '',
        status: this.project.status,
        priority: this.project.priority,
        color: this.project.color
      }
      
      const modal = new Modal(document.getElementById('projectModal'))
      modal.show()
    },

    async createTask(parentTask = null) {
      if (!this.project) return

      // Устанавливаем значения по умолчанию из загруженных данных
      const defaultTaskStatus = this.taskStatuses.find(s => s.is_default) || this.taskStatuses[0]
      const defaultTaskPriority = this.taskPriorities.find(p => p.is_default) || this.taskPriorities[0]

      this.isEditingTask = false
      this.currentTask = {
        title: '',
        description: '',
        project_id: this.project.id,
        assignee_id: '',
        assignee_ids: [],
        status: defaultTaskStatus ? defaultTaskStatus.code : 'todo',
        priority: defaultTaskPriority ? defaultTaskPriority.code : 'medium',
        start_date: '',
        due_date: '',
        estimated_hours: null,
        parent_id: parentTask ? parentTask.id : null
      }
      await this.loadAvailableParentTasks()
      const modal = new Modal(document.getElementById('taskModal'))
      modal.show()
    },

    createSubTask(task) {
      this.createTask(task)
    },

    async editTask(task) {
      this.isEditingTask = true
      this.currentTask = {
        id: task.id,
        title: task.title,
        description: task.description,
        project_id: task.project?.id || this.project.id,
        assignee_id: task.assignee?.id || '',
        assignee_ids: (task.assignees || []).map(u => u.id),
        status: task.status,
        priority: task.priority,
        start_date: task.start_date ? this.formatDateTimeLocal(new Date(task.start_date)) : '',
        due_date: task.due_date ? this.formatDateTimeLocal(new Date(task.due_date)) : '',
        estimated_hours: task.estimated_hours,
        parent_id: task.parent || null
      }
      await this.loadAvailableParentTasks(task.id)
      const modal = new Modal(document.getElementById('taskModal'))
      modal.show()
    },

    async loadAvailableParentTasks(excludeTaskId = null) {
      try {
        const resp = await projectManagementApi.getTasks({ project_id: this.project?.id })
        const list = resp.data.results || resp.data || []
        this.availableParentTasks = Array.isArray(list)
          ? list.filter(t => (excludeTaskId ? t.id !== excludeTaskId : true))
          : []
      } catch (e) {
        console.error('Ошибка загрузки доступных родительских задач', e)
        this.availableParentTasks = []
      }
    },

    deleteTask(task) {
      this.confirmDeleteTask(task)
    },

    async submitProject() {
      try {
        // Подготавливаем данные проекта
        const projectData = {
          ...this.currentProject,
          // Конвертируем пустые строки в null для дат
          start_date: this.currentProject.start_date || null,
          end_date: this.currentProject.end_date || null
        }
        
        await projectManagementApi.updateProject(projectData.id, projectData)
        
        // Закрываем модальное окно
        const modal = Modal.getInstance(document.getElementById('projectModal'))
        if (modal) {
          modal.hide()
        }
        
        // Перезагружаем данные проекта
        await this.loadProjectData()
        
        this.showSuccess('Проект успешно обновлен!')
      } catch (error) {
        console.error('Ошибка обновления проекта:', error)
        
        let errorMessage = 'Ошибка обновления проекта'
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

    async submitTask() {
      try {
        // Клиентская проверка дублей в проекте и ветке
        const title = (this.currentTask.title || '').trim()
        if (title && this.project?.id) {
          try {
            const resp = await projectManagementApi.getTasks({ project_id: this.project.id })
            const list = resp.data.results || resp.data || []
            const parentId = this.currentTask.parent_id || null
            const norm = (s) => (s || '').toString().trim().replace(/\s+/g,' ').toLowerCase()
            const target = norm(title)
            const isDuplicate = list.some(t => {
              const sameBranch = (parentId ? (t.parent === parentId || t.parent_id === parentId) : (!t.parent && !t.parent_id))
              if (!sameBranch) return false
              return norm(t.title) === target && (!this.isEditingTask || t.id !== this.currentTask.id)
            })
            if (isDuplicate) {
              this.showError('Задача с таким названием уже существует в этом проекте/ветке')
              return
            }
          } catch (_) {}
        }
        // Гарантируем, что все выбранные исполнители состоят в команде проекта
        if (!this.isEditingTask && this.project?.id && Array.isArray(this.currentTask?.assignee_ids) && this.currentTask.assignee_ids.length) {
          try {
            const projectResp = await projectManagementApi.getProject(this.project.id)
            const project = projectResp.data
            const teamUserIds = new Set()
            if (project?.owner?.id) teamUserIds.add(project.owner.id)
            if (project?.manager?.id) teamUserIds.add(project.manager.id)
            if (Array.isArray(project?.memberships)) {
              project.memberships.forEach(m => m?.user?.id && teamUserIds.add(m.user.id))
            }
            for (const uid of this.currentTask.assignee_ids) {
              if (!teamUserIds.has(uid)) {
                if (project?.team?.id) {
                  await projectManagementApi.addTeamMember(project.team.id, { user_id: uid, role: 'member' })
                }
                await projectManagementApi.addProjectMember(this.project.id, { user_id: uid, role: 'member' })
                teamUserIds.add(uid)
              }
            }
          } catch (e) {
            // noop — сервер всё равно провалидирует
          }
        }
        // Подготавливаем данные задачи, конвертируя пустые строки в null
        const taskData = {
          ...this.currentTask,
          project_id: this.currentTask.project_id || null,
          assignee_id: this.currentTask.assignee_id || null,
          assignee_ids: this.currentTask.assignee_ids || [],
          start_date: this.currentTask.start_date || null,
          due_date: this.currentTask.due_date || null,
          estimated_hours: this.currentTask.estimated_hours || null,
          parent_id: this.currentTask.parent_id || null
        }
        
        if (this.isEditingTask) {
          await projectManagementApi.updateTask(taskData.id, taskData)
        } else {
          await projectManagementApi.createTask(taskData)
        }
        
        // Закрываем модальное окно
        const modal = Modal.getInstance(document.getElementById('taskModal'))
        if (modal) modal.hide()
        
        // Перезагружаем данные проекта и дерево
        await this.loadProjectData()
        await this.loadProjectTree()
        
        this.showSuccess(this.isEditingTask ? 'Задача обновлена' : 'Задача создана')
      } catch (error) {
        console.error('Ошибка сохранения задачи:', error)
        
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

    async confirmDeleteProject() {
      const confirmed = await this.showConfirmDialog({
        title: 'Удаление проекта',
        message: `Вы уверены, что хотите удалить проект "${this.project.name}"? Это действие необратимо.`,
        confirmText: 'Удалить',
        cancelText: 'Отмена',
        variant: 'danger'
      })
      
      if (confirmed) {
        try {
          await projectManagementApi.deleteProject(this.project.id)
          this.closeConfirmDialog()
          this.showSuccess('Проект успешно удален!')
          // Переходим к списку проектов
          this.$router.push('/crm/project-management/projects')
        } catch (error) {
          console.error('Ошибка удаления проекта:', error)
          this.closeConfirmDialog()
          this.showError('Ошибка удаления проекта')
        }
      }
    },

    async confirmDeleteTask(task) {
      const confirmed = await this.showConfirmDialog({
        title: 'Удаление задачи',
        message: `Вы уверены, что хотите удалить задачу "${task.title}"?`,
        confirmText: 'Удалить',
        cancelText: 'Отмена',
        variant: 'danger'
      })
      
      if (confirmed) {
        try {
          await projectManagementApi.deleteTask(task.id)
          this.closeConfirmDialog()
          await this.loadProjectData()
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
        'planning': 'bg-secondary',
        'active': 'bg-success',
        'on_hold': 'bg-warning',
        'completed': 'bg-primary',
        'cancelled': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },

    getStatusText(status) {
      if (!status) return 'Не указан'
      const statusObj = this.projectStatuses?.find(s => s.code === status)
      return statusObj?.name || status
    },

    getTaskStatusClass(status) {
      const classes = {
        'todo': 'bg-secondary',
        'in_progress': 'bg-warning',
        'review': 'bg-info',
        'done': 'bg-success',
        'cancelled': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },

    getTaskStatusText(status) {
      if (!status) return 'Не указан'
      const statusObj = this.taskStatuses?.find(s => s.code === status)
      return statusObj?.name || status
    },

    getPriorityClass(priority) {
      const classes = {
        'low': 'bg-secondary',
        'medium': 'bg-primary',
        'high': 'bg-warning',
        'urgent': 'bg-danger'
      }
      return classes[priority] || 'bg-secondary'
    },

    getPriorityText(priority) {
      if (!priority) return 'Не указан'
      // Сначала ищем в приоритетах задач, потом в приоритетах проектов
      const taskPriorityObj = this.taskPriorities?.find(p => p.code === priority)
      const projectPriorityObj = this.projectPriorities?.find(p => p.code === priority)
      return taskPriorityObj?.name || projectPriorityObj?.name || priority
    },

    getProgressClass(progress) {
      if (progress >= 80) return 'bg-success'
      if (progress >= 50) return 'bg-warning'
      return 'bg-danger'
    },

    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString('ru-RU')
    },

    formatDateTimeLocal(date) {
      if (!date) return ''
      return new Date(date).toISOString().slice(0, 16)
    },



    updateProjectProgress() {
      if (!this.project || !Array.isArray(this.tasks)) return
      
      // Фильтруем только валидные задачи
      const validTasks = this.tasks.filter(task => task && task.status)
      const totalTasks = validTasks.length
      const completedTasks = validTasks.filter(task => task.status === 'done').length
      const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
      
      // Обновляем локальные данные проекта
      this.project.task_count = totalTasks
      this.project.completed_task_count = completedTasks
      this.project.progress = progress
    },

    truncateText(text, maxLength) {
      if (!text || typeof text !== 'string') return ''
      if (text.length > maxLength) {
        return text.slice(0, maxLength) + '...'
      }
      return text
    },

    getDueDateClass(dueDate, status) {
      if (!dueDate) return ''
      const date = new Date(dueDate)
      const today = new Date()
      const diffInDays = Math.ceil((date - today) / (1000 * 60 * 60 * 24))

      if (diffInDays < 0) {
        return 'text-danger'
      } else if (diffInDays === 0 && status === 'todo') {
        return 'text-warning'
      } else if (diffInDays <= 7 && status === 'in_progress') {
        return 'text-primary'
      } else {
        return ''
      }
    },

    getBackRoute() {
      // Проверяем query параметр from для определения откуда пришли
      const from = this.$route.query.from
      if (from === 'management') {
        return '/crm/project-management/management'
      }
      // По умолчанию возвращаемся в "Мои проекты"
      return '/crm/project-management/my-projects'
    },

    getBackRouteTitle() {
      const from = this.$route.query.from
      if (from === 'management') {
        return 'Проекты и задачи'
      }
      return 'Мои проекты'
    },

    // Методы для управления командой проекта
    openTeamModal() {
      this.selectedUserId = ''
      this.selectedRole = 'member'
      const modal = new Modal(document.getElementById('teamModal'))
      modal.show()
    },

    async addMember() {
      if (!this.selectedUserId || !this.project?.id) {
        this.showError('Пожалуйста, выберите пользователя')
        return
      }

      this.loadingTeamAction = true
      try {
        const memberData = { user_id: this.selectedUserId, role: this.selectedRole }
        // если у проекта есть команда — синхронизируем: добавляем в команду
        if (this.project?.team?.id) {
          await projectManagementApi.addTeamMember(this.project.team.id, { user_id: this.selectedUserId, role: 'member' })
        }
        // затем — в проект
        const response = await projectManagementApi.addProjectMember(this.project.id, memberData)
        
        // Обновляем только данные команды
        await this.refreshTeamData()
        
        // Сбрасываем форму
        this.selectedUserId = ''
        this.selectedRole = 'member'
        
        this.showSuccess('Участник добавлен в команду проекта!')
      } catch (error) {
        console.error('Ошибка добавления участника:', error)
        
        let errorMessage = 'Ошибка добавления участника'
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
      } finally {
        this.loadingTeamAction = false
      }
    },

    async removeMember(member) {
      if (!member?.user?.id || !this.project?.id) {
        this.showError('Ошибка: данные участника или проекта недоступны')
        return
      }

      const userName = this.getUserDisplayName(member.user)
      const confirmed = await this.showConfirmDialog({
        title: 'Исключение из команды',
        message: `Вы уверены, что хотите исключить ${userName} из команды проекта?`,
        confirmText: 'Исключить',
        cancelText: 'Отмена',
        variant: 'danger'
      })

      if (!confirmed) {
        this.closeConfirmDialog()
        return
      }

      try {
        await projectManagementApi.removeProjectMember(this.project.id, member.user.id)
        this.closeConfirmDialog()
        
        // Обновляем данные команды
        await this.refreshTeamData()
        
        this.showSuccess('Участник исключен из команды проекта!')
      } catch (error) {
        console.error('Ошибка удаления участника:', error)
        this.closeConfirmDialog()
        this.showError('Ошибка исключения участника из команды')
      }
    },

    getRoleText(role) {
      const roles = {
        'member': 'Участник',
        'lead': 'Ведущий',
        'observer': 'Наблюдатель'
      }
      return roles[role] || role
    },

    getRoleClass(role) {
      const classes = {
        'member': 'member-role',
        'lead': 'lead-role',
        'observer': 'observer-role'
      }
      return classes[role] || 'member-role'
    },

    getRoleBadgeClass(role) {
      const classes = {
        'member': 'bg-secondary',
        'lead': 'bg-warning',
        'observer': 'bg-info'
      }
      return classes[role] || 'bg-secondary'
    },

    getUserDisplayName(user) {
      if (!user) return 'Неизвестный пользователь'
      
      if (user.full_name) {
        return user.full_name
      }
      
      if (user.first_name || user.last_name) {
        return `${user.first_name || ''} ${user.last_name || ''}`.trim()
      }
      
      return user.username || user.email || 'Пользователь'
    },

    getAvatarUrl(user) {
      // Используем локальную утилиту для генерации аватаров
      return getAvatarUrl(user, 40)
    },

    async refreshTeamData() {
      // Принудительное обновление только данных команды
      if (!this.project?.id) return
      
      try {
        const response = await projectManagementApi.getProject(this.project.id)
        
        // Обновляем только поле memberships
        if (this.project) {
          this.project.memberships = response.data.memberships || []
        }
      } catch (error) {
        console.error('Ошибка обновления команды:', error)
        this.showError('Ошибка обновления данных команды')
      }
    }
  }
}
</script>

<style scoped lang="scss">
@import './project-management.scss';

.project-detail-page {
  padding: 2rem;
  min-height: 100vh;
  background: var(--bs-gray-100);
}

// Заголовок страницы
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: $radius-usual;
  box-shadow: $pm-card-shadow;
  
  .header-content {
    flex: 1;
  }
  
  .header-actions {
    display: flex;
    gap: 0.75rem;
    margin-left: 2rem;
  }
}

// Чипы выбранных исполнителей внутри модалки
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

// Хлебные крошки
.breadcrumb-nav {
  margin-bottom: 1rem;
  
  .breadcrumb {
    background: transparent;
    padding: 0;
    margin: 0;
    
    .breadcrumb-item {
      font-size: 0.875rem;
      
      .breadcrumb-link {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--bs-secondary-color);
        text-decoration: none;
        transition: color 0.2s ease;
        
        &:hover {
          color: var(--bs-primary);
        }
      }
      
      &.active {
        color: var(--bs-heading-color);
        font-weight: 600;
      }
    }
  }
}

// Секция заголовка проекта
.project-title-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  
  .project-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  
  .project-title {
    h1 {
      font-size: 2rem;
      font-weight: 700;
      color: var(--bs-heading-color);
      margin: 0 0 0.5rem 0;
    }
    
    .project-meta-badges {
      display: flex;
      gap: 0.5rem;
      
      .badge {
        padding: 0.375rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 6px;
      }
    }
  }
}

// Кнопки в заголовке
.header-actions {
  .btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    font-weight: 600;
    border-radius: 8px;
    transition: all 0.2s ease;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
  }
}

// Состояния загрузки и ошибки
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: $radius-usual;
  box-shadow: $pm-card-shadow;
  
  h3 {
    margin: 1rem 0 0.5rem 0;
    color: var(--bs-heading-color);
  }
  
  p {
    color: var(--bs-secondary-color);
    margin-bottom: 1.5rem;
  }
}

.spinner-container {
  .spinner {
    width: 48px;
    height: 48px;
    border: 4px solid var(--bs-gray-200);
    border-left-color: var(--bs-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  .error-icon {
    color: var(--bs-danger);
    margin-bottom: 1rem;
  }
}

// Основной контент
.project-content {
  .info-section {
    margin-bottom: 2rem;
  }
  
  .info-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 1.5rem;
    
    @media (max-width: 1200px) {
      grid-template-columns: 1fr 1fr;
    }
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
}

// Карточки информации
.info-card {
  background: white;
  border-radius: $radius-usual;
  box-shadow: $pm-card-shadow;
  padding: 1.5rem;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: $pm-card-hover-shadow;
  }
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--bs-border-color);
    
    h3 {
      font-size: 1.25rem;
      font-weight: 600;
      color: var(--bs-heading-color);
      margin: 0;
    }
  }
  
  .card-body {
    .description-section {
      margin-bottom: 1.5rem;
      
      .description {
        color: var(--bs-secondary-color);
        line-height: 1.6;
        margin: 0;
      }
    }
  }
}

// Сетка метаданных
.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bs-gray-100);
    border-radius: 8px;
    
    .meta-icon {
      color: var(--bs-secondary-color);
    }
    
    .meta-content {
      display: flex;
      flex-direction: column;
      
      .meta-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--bs-secondary-color);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      
      .meta-value {
        font-weight: 600;
        color: var(--bs-heading-color);
      }
    }
  }
}

// Секция статистики
.stats-card {
  .progress-section {
    margin-bottom: 1.5rem;
    
    .progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
      
      span {
        font-size: 0.875rem;
        color: var(--bs-secondary-color);
      }
      
      .progress-value {
        font-weight: 600;
        color: var(--bs-primary);
      }
    }
    
    .progress-bar-container {
      height: 8px;
      background: var(--bs-gray-200);
      border-radius: 4px;
      overflow: hidden;
      
      .progress-bar {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
        
        &.bg-success { background: var(--bs-success); }
        &.bg-warning { background: var(--bs-warning); }
        &.bg-danger { background: var(--bs-danger); }
      }
    }
  }
  
  .stats-grid {
    display: grid;
    gap: 1rem;
    
    .stat-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem;
      background: var(--bs-gray-100);
      border-radius: 8px;
      
      .stat-icon {
        color: var(--bs-primary);
        
        &.completed { color: var(--bs-success); }
        &.in-progress { color: var(--bs-warning); }
      }
      
      .stat-content {
        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--bs-heading-color);
          line-height: 1;
        }
        
        .stat-label {
          font-size: 0.75rem;
          color: var(--bs-secondary-color);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
      }
    }
  }
}

// Секция команды
.team-card {
  .card-header {
    justify-content: space-between;
    
    .btn {
      margin-left: auto;
    }
  }
  
  .team-members {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    
    .team-member {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem;
      background: var(--bs-gray-100);
      border-radius: 8px;
      position: relative;
      
      .member-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
      
      .member-info {
        flex: 1;
        
        .member-name {
          font-weight: 600;
          color: var(--bs-heading-color);
        }
        
        .member-role {
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          
          &.owner-role {
            color: var(--bs-success);
            font-weight: 600;
          }
          
          &.manager-role {
            color: var(--bs-primary);
            font-weight: 600;
          }
          
          &.lead-role {
            color: var(--bs-warning);
            font-weight: 600;
          }
          
          &.member-role {
            color: var(--bs-secondary);
          }
          
          &.observer-role {
            color: var(--bs-info);
          }
        }
      }
      
      .member-actions {
        display: flex;
        gap: 0.25rem;
      }
    }
    
    .empty-team {
      text-align: center;
      padding: 2rem;
      
      .empty-icon {
        color: var(--bs-gray-400);
        margin-bottom: 1rem;
      }
      
      p {
        color: var(--bs-secondary-color);
        margin-bottom: 1rem;
      }
    }
  }
}

// Модальное окно управления командой
#teamModal {
  .modal-body {
    .current-team {
      max-height: 300px;
      overflow-y: auto;
      
      .team-member-modal {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        background: var(--bs-gray-100);
        border-radius: 6px;
        margin-bottom: 0.5rem;
        
        .member-avatar-small {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          object-fit: cover;
        }
        
        .member-info-modal {
          flex: 1;
          
          .member-name {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--bs-heading-color);
          }
          
          .member-role {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            
            &.owner-role {
              color: var(--bs-success);
            }
            
            &.manager-role {
              color: var(--bs-primary);
            }
            
            &.lead-role {
              color: var(--bs-warning);
            }
            
            &.member-role {
              color: var(--bs-secondary);
            }
            
            &.observer-role {
              color: var(--bs-info);
            }
          }
        }
      }
    }
    
    .add-member-form {
      .form-label {
        font-weight: 600;
        color: var(--bs-heading-color);
      }
    }
  }
}

// Секция задач
.tasks-section {
  background: white;
  border-radius: $radius-usual;
  box-shadow: $pm-card-shadow;
  overflow: hidden;
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid var(--bs-border-color);
    
    .section-title {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      
      h2 {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--bs-heading-color);
        margin: 0;
      }
    }

    .section-actions {
      display: flex;
      gap: 0.75rem;
    }

    .btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1.25rem;
      font-weight: 600;
      border-radius: 8px;
      transition: all 0.2s ease;
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
      }
    }
  }
  
  .tasks-content {
    padding: 1.5rem;

    .empty-state {
      text-align: center;
      padding: 3rem 2rem;
      
      .empty-icon {
        color: var(--bs-gray-400);
        margin-bottom: 1rem;
      }
      
      h3 {
        color: var(--bs-heading-color);
        margin-bottom: 0.5rem;
      }
      
      p {
        color: var(--bs-secondary-color);
        margin-bottom: 1.5rem;
      }
      
      .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem 2rem;
        font-weight: 600;
        border-radius: 8px;
      }
    }

    .task-tree-container {
      height: 400px;
    }
  }
}

// Таблица задач
.tasks-table-container {
  .tasks-table {
    width: 100%;
    border-collapse: collapse;
    
    thead {
      background: var(--bs-gray-100);
      
      th {
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        color: var(--bs-heading-color);
        border-bottom: 2px solid var(--bs-border-color);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
    }
    
    tbody {
      tr {
        border-bottom: 1px solid var(--bs-border-color);
        transition: background-color 0.2s ease;
        
        &:hover {
          background: var(--bs-gray-50);
        }
        
        td {
          padding: 1rem;
          vertical-align: top;
        }
      }
    }
  }
}

// Ячейки таблицы
.task-cell {
  .task-info {
    .task-title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--bs-heading-color);
      margin: 0 0 0.5rem 0;
    }
    
    .task-description {
      font-size: 0.875rem;
      color: var(--bs-secondary-color);
      margin: 0;
      line-height: 1.4;
    }
  }
}

.assignee-cell {
  .assignee-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    
    .assignee-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      object-fit: cover;
    }
    
    .assignee-name {
      font-weight: 600;
      color: var(--bs-heading-color);
    }
  }
  
  .no-assignee {
    color: var(--bs-secondary-color);
    font-style: italic;
  }
}

.status-cell,
.priority-cell {
  .badge {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 6px;
  }
}

.due-date-cell {
  span {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.875rem;
    
    &.text-danger { color: var(--bs-danger); }
    &.text-warning { color: var(--bs-warning); }
    &.text-primary { color: var(--bs-primary); }
  }
}

// Адаптивность
@media (max-width: 768px) {
  .project-detail-page {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    gap: 1rem;
    
    .header-actions {
      margin-left: 0;
      width: 100%;
      justify-content: flex-end;
    }
  }
  
  .project-title-section {
    .project-title h1 {
      font-size: 1.5rem;
    }
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .tasks-section {
    .section-header {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }
  }
  
  .tasks-table-container {
    overflow-x: auto;
    
    .tasks-table {
      min-width: 600px;
    }
  }
}

// Кнопки действий в таблице
.actions-cell {
  .action-buttons {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    
    .btn-edit-icon,
    .btn-delete-icon {
      width: 32px;
      height: 32px;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 6px;
      transition: all 0.2s ease;
      background: transparent;
      border: 1px solid;
      cursor: pointer;
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
      }
    }
    
    .btn-edit-icon {
      border-color: var(--bs-primary);
      color: var(--bs-primary);
      
      &:hover {
        background-color: var(--bs-primary);
        color: white;
      }
    }
    
    .btn-delete-icon {
      border-color: var(--bs-danger);
      color: var(--bs-danger);
      
      &:hover {
        background-color: var(--bs-danger);
        color: white;
      }
    }
  }
}
</style> 