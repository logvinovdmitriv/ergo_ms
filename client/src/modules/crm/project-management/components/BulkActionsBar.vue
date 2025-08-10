<template>
  <div class="pm-filters-card mb-3" v-if="visible">
    <div class="card-body d-flex flex-wrap align-items-center gap-2">
      <span class="badge bg-primary rounded-pill px-3 py-2">
        Выбрано: {{ selectedCount }}
      </span>

      <!-- Для задач -->
      <template v-if="entity === 'task'">
        <div class="d-flex align-items-center gap-2">
          <label class="form-label mb-0 small">Статус</label>
          <select class="form-select" :disabled="loading || loadingDictionaries"
                  v-model="task.statusCode">
            <option value="" disabled>— выбрать —</option>
            <option v-for="s in statuses" :key="s.code" :value="s.code">{{ s.name }}</option>
          </select>
          <button class="btn btn-outline-primary" :disabled="!task.statusCode || loading"
                  @click="$emit('change-status', task.statusCode)">
            Применить
          </button>
        </div>

        <div class="d-flex align-items-center gap-2">
          <label class="form-label mb-0 small">Приоритет</label>
          <select class="form-select" :disabled="loading || loadingDictionaries"
                  v-model="task.priorityCode">
            <option value="" disabled>— выбрать —</option>
            <option v-for="p in priorities" :key="p.code" :value="p.code">{{ p.name }}</option>
          </select>
          <button class="btn btn-outline-primary" :disabled="!task.priorityCode || loading"
                  @click="$emit('change-priority', task.priorityCode)">
            Применить
          </button>
        </div>

        <div class="d-flex align-items-center gap-2">
          <label class="form-label mb-0 small">Исполнитель</label>
          <select class="form-select" :disabled="loading || loadingUsers"
                  v-model="task.assigneeId">
            <option value="" disabled>— выбрать —</option>
            <option value="__none">Снять исполнителя</option>
            <option v-for="u in users" :key="u.id" :value="u.id">
              {{ u.full_name || (u.first_name + ' ' + u.last_name).trim() || u.username }}
            </option>
          </select>
          <button class="btn btn-outline-primary" :disabled="!task.assigneeId || loading"
                  @click="applyAssignee">
            Применить
          </button>
        </div>

        <div class="d-flex align-items-center gap-2">
          <label class="form-label mb-0 small">Дедлайн</label>
          <input type="datetime-local" class="form-control" v-model="task.dueDate"
                 :disabled="loading"/>
          <button class="btn btn-outline-primary" :disabled="!task.dueDate || loading"
                  @click="$emit('change-due-date', task.dueDate)">
            Применить
          </button>
        </div>

        <div class="d-flex align-items-center gap-2">
          <label class="form-label mb-0 small">Перенести в проект</label>
          <select class="form-select" :disabled="loading || loadingProjects"
                  v-model="task.projectId">
            <option value="" disabled>— выбрать —</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
          <button class="btn btn-outline-primary" :disabled="!task.projectId || loading"
                  @click="$emit('move-to-project', task.projectId)">
            Перенести
          </button>
        </div>
      </template>

      <!-- Для проектов -->
      <template v-else-if="entity === 'project'">
        <div class="d-flex align-items-center gap-2">
          <label class="form-label mb-0 small">Статус</label>
          <select class="form-select" :disabled="loading || loadingDictionaries"
                  v-model="project.statusCode">
            <option value="" disabled>— выбрать —</option>
            <option v-for="s in statuses" :key="s.code" :value="s.code">{{ s.name }}</option>
          </select>
          <button class="btn btn-outline-primary" :disabled="!project.statusCode || loading"
                  @click="$emit('change-status', project.statusCode)">
            Применить
          </button>
        </div>
      </template>

      <div class="ms-auto d-flex align-items-center gap-2">
        <button class="btn btn-outline-danger" :disabled="loading"
                @click="$emit('delete-selected')">
          Удалить выбранные
        </button>
        <button class="btn btn-outline-secondary" :disabled="loading"
                @click="$emit('clear-selection')">
          Отменить выбор
        </button>
        <div v-if="loading" class="spinner-border spinner-border-sm text-primary" role="status"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BulkActionsBar',
  props: {
    entity: { type: String, required: true }, // 'task' | 'project'
    visible: { type: Boolean, default: false },
    selectedCount: { type: Number, default: 0 },
    loading: { type: Boolean, default: false },

    // словари / списки
    statuses: { type: Array, default: () => [] },
    priorities: { type: Array, default: () => [] },
    users: { type: Array, default: () => [] },
    projects: { type: Array, default: () => [] },

    loadingDictionaries: { type: Boolean, default: false },
    loadingUsers: { type: Boolean, default: false },
    loadingProjects: { type: Boolean, default: false }
  },
  data() {
    return {
      task: { statusCode: '', priorityCode: '', assigneeId: '', dueDate: '', projectId: '' },
      project: { statusCode: '' }
    }
  },
  methods: {
    applyAssignee() {
      if (this.task.assigneeId === '__none') {
        this.$emit('clear-assignee') // снять исполнителя
      } else if (this.task.assigneeId) {
        this.$emit('assign-user', this.task.assigneeId)
      }
    }
  }
}
</script>
