<template>
  <div class="pm-filters-card bulk-bar" v-if="visible">
    <div class="card-body">

      <!-- шапка: счётчик + кнопки -->
      <div class="bulk-head">
        <span class="bulk-chip">Выбрано: {{ selectedCount }}</span>
        <div class="bulk-head-actions">
          <button class="btn btn-outline-danger"
                  :disabled="loading"
                  @click="$emit('delete-selected')">
            Удалить выбранные
          </button>
          <button class="btn btn-outline-secondary"
                  :disabled="loading"
                  @click="$emit('clear-selection')">
            Отменить выбор
          </button>
          <div v-if="loading" class="spinner-border spinner-border-sm text-primary" role="status"
               aria-label="Выполняется..."></div>
        </div>
      </div>

      <!-- ДЕЙСТВИЯ: ЗАДАЧИ -->
      <div v-if="entity === 'task'" class="row g-3 align-items-end">
        <!-- Статус -->
        <div class="col-12 col-md-6 col-lg-4 col-xl-3">
          <label class="form-label bulk-label">Статус</label>
          <div class="bulk-control">
            <select class="form-select"
                    :disabled="loading || loadingDictionaries"
                    v-model="task.statusCode">
              <option value="" disabled>— выбрать —</option>
              <option v-for="s in statuses" :key="s.code" :value="s.code">{{ s.name }}</option>
            </select>
            <button class="btn btn-outline-primary btn-apply"
                    :disabled="!task.statusCode || loading"
                    @click="$emit('change-status', task.statusCode)">
              Применить
            </button>
          </div>
        </div>

        <!-- Приоритет -->
        <div class="col-12 col-md-6 col-lg-4 col-xl-3">
          <label class="form-label bulk-label">Приоритет</label>
          <div class="bulk-control">
            <select class="form-select"
                    :disabled="loading || loadingDictionaries"
                    v-model="task.priorityCode">
              <option value="" disabled>— выбрать —</option>
              <option v-for="p in priorities" :key="p.code" :value="p.code">{{ p.name }}</option>
            </select>
            <button class="btn btn-outline-primary btn-apply"
                    :disabled="!task.priorityCode || loading"
                    @click="$emit('change-priority', task.priorityCode)">
              Применить
            </button>
          </div>
        </div>

        <!-- Исполнитель -->
        <div class="col-12 col-md-6 col-lg-4 col-xl-3">
          <label class="form-label bulk-label">Исполнитель</label>
          <div class="bulk-control">
            <select class="form-select"
                    :disabled="loading || loadingUsers"
                    v-model="task.assigneeId">
              <option value="" disabled>— выбрать —</option>
              <option value="__none">Снять исполнителя</option>
              <option v-for="u in users" :key="u.id" :value="u.id">
                {{ u.full_name || (u.first_name + ' ' + u.last_name).trim() || u.username }}
              </option>
            </select>
            <button class="btn btn-outline-primary btn-apply"
                    :disabled="!task.assigneeId || loading"
                    @click="applyAssignee">
              Применить
            </button>
          </div>
        </div>

        <!-- Дедлайн -->
        <div class="col-12 col-md-6 col-lg-4 col-xl-3">
          <label class="form-label bulk-label">Дедлайн</label>
          <div class="bulk-control">
            <input type="datetime-local"
                   class="form-control"
                   v-model="task.dueDate"
                   :disabled="loading"/>
            <button class="btn btn-outline-primary btn-apply"
                    :disabled="!task.dueDate || loading"
                    @click="$emit('change-due-date', task.dueDate)">
              Применить
            </button>
          </div>
        </div>

        <!-- Перенести в проект -->
        <div class="col-12 col-md-6 col-lg-4 col-xl-3">
          <label class="form-label bulk-label">Перенести в проект</label>
          <div class="bulk-control">
            <select class="form-select"
                    :disabled="loading || loadingProjects"
                    v-model="task.projectId">
              <option value="" disabled>— выбрать —</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <button class="btn btn-outline-primary btn-apply"
                    :disabled="!task.projectId || loading"
                    @click="$emit('move-to-project', task.projectId)">
              Перенести
            </button>
          </div>
        </div>
      </div>

      <!-- ДЕЙСТВИЯ: ПРОЕКТЫ -->
      <div v-else-if="entity === 'project'" class="row g-3 align-items-end">
        <div class="col-12 col-md-6 col-lg-4 col-xl-3">
          <label class="form-label bulk-label">Статус</label>
          <div class="bulk-control">
            <select class="form-select"
                    :disabled="loading || loadingDictionaries"
                    v-model="project.statusCode">
              <option value="" disabled>— выбрать —</option>
              <option v-for="s in statuses" :key="s.code" :value="s.code">{{ s.name }}</option>
            </select>
            <button class="btn btn-outline-primary btn-apply"
                    :disabled="!project.statusCode || loading"
                    @click="$emit('change-status', project.statusCode)">
              Применить
            </button>
          </div>
        </div>
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
        this.$emit('clear-assignee')
      } else if (this.task.assigneeId) {
        this.$emit('assign-user', this.task.assigneeId)
      }
    }
  }
}
</script>

<style scoped>
/* шапка */
.bulk-head{
  display:grid;
  grid-template-columns: 1fr auto;
  gap:.75rem 1rem;
  align-items:center;
  margin-bottom: .5rem;
}
.bulk-head-actions{
  display:flex;
  gap:.5rem;
  align-items:center;
  justify-content:flex-end;
  flex-wrap:wrap;
}

/* аккуратная «пилюля» со счетчиком */
.bulk-chip{
  display:inline-flex;
  align-items:center;
  gap:.5rem;
  padding:.35rem .75rem;
  border-radius:999px;
  background:var(--bs-danger, #dc3545);
  color:#fff;
  font-weight:600;
  line-height:1;
}

/* подписи */
.bulk-label{
  margin-bottom:.35rem;
  font-size:.8rem;
  color:var(--bs-secondary-color,#6c757d);
  text-transform:uppercase;
  letter-spacing:.02em;
}

/* основа: сетка «контрол + кнопка» */
.bulk-control{
  display:grid;
  grid-template-columns: 1fr auto;     /* контрол растёт, кнопка — авто */
  column-gap:.5rem;
  align-items:center;
}

/* чтобы точно не было наложений: всё растянуто и без отрицательных маргинов */
.bulk-control .form-select,
.bulk-control .form-control{
  width:100%;
  position:relative;
  z-index:1;
}
.btn-apply{
  position:relative;
  z-index:0;
  white-space:nowrap;
}

/* компактные отступы панели */
.bulk-bar .card-body{
  padding:1rem 1.25rem;
}

/* мобильная адаптация: кнопка уходит на вторую строку и растягивается */
@media (max-width: 576px){
  .bulk-control{
    grid-template-columns: 1fr;
    row-gap:.5rem;
  }
  .btn-apply{ width:100%; }
}
</style>
