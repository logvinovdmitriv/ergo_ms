<template>
  <div class="org-details orgs-scope">
    <!-- Общая информация -->
    <section class="card">
      <header class="card__header">
        <h2 class="card__title">Общая информация</h2>

        <div class="toolbar">
          <button v-if="canDeleteOrg" class="btn btn--sm btn--danger btn--ghost" @click="onDelete">
            Удалить организацию
          </button>
          <button v-if="canLeave" class="btn btn--sm btn--ghost" @click="onLeave">
            Выйти из организации
          </button>
        </div>
      </header>

      <div class="card__body">
        <div v-if="loadingOrg"><div class="skeleton skeleton--row"></div></div>
        <div v-else-if="error" class="text-danger">{{ error }}</div>
        <div v-else>
          <div class="org-summary">
            <div class="cell-main">
              <div class="avatar" v-if="org.logo_url"><img :src="org.logo_url" alt="" /></div>
              <div class="avatar avatar--placeholder" v-else>{{ (org.name || 'Организация')[0] }}</div>

              <div class="name-stack">
                <template v-if="!editMode">
                  <div class="title">
                    <span class="text-lg">{{ org.name || 'Без названия' }}</span>
                  </div>
                </template>

                <template v-else>
                  <input v-model="editForm.name" class="input input--md" placeholder="Название…" />
                </template>

                <div class="badges">
                  <span class="badge" :class="(org.status || 'active') === 'active' ? 'badge--success' : 'badge--muted'">
                    {{ org.status || 'active' }}
                  </span>
                  <span class="badge badge--outline">{{ myRole(org) }}</span>
                  <span class="badge badge--neutral">{{ membersCount }} участника</span>
                </div>
              </div>
            </div>

            <div class="toolbar">
              <button
                v-if="!editMode && canEditOrg"
                class="btn btn--sm btn--secondary"
                @click="startEdit"
              >
                Изменить
              </button>
              <div v-if="editMode" class="toolbar__edit">
                <button class="btn btn--sm btn--primary" :disabled="saving" @click="saveInfo">
                  {{ saving ? 'Сохраняем…' : 'Сохранить' }}
                </button>
                <button class="btn btn--sm btn--ghost" :disabled="saving" @click="cancelEdit">
                  Отмена
                </button>
              </div>

              <button v-if="canManageMembers || canInvite" class="btn btn--sm btn--primary" @click="showInvite = true">
                Пригласить
              </button>
            </div>
          </div>

          <!-- VIEW MODE -->
          <dl v-if="!editMode" class="dl dl--grid">
            <div><dt>Сайт</dt><dd>
              <template v-if="org.website">
                <a :href="org.website" target="_blank" rel="noopener">{{ org.website }}</a>
              </template>
              <span v-else class="muted">не указано</span>
            </dd></div>

            <div><dt>Email</dt><dd>{{ org.email || 'не указано' }}</dd></div>
            <div><dt>Телефон</dt><dd>{{ org.phone || 'не указано' }}</dd></div>
            <div><dt>Страна</dt><dd>{{ org.country || 'не указано' }}</dd></div>
            <div><dt>Часовой пояс</dt><dd>{{ org.timezone || 'не указано' }}</dd></div>
            <div class="col-2"><dt>Адрес</dt><dd>{{ org.address || 'не указано' }}</dd></div>
            <div class="col-2"><dt>Описание</dt><dd>{{ org.description || 'не указано' }}</dd></div>
            <div class="col-2"><dt>Отрасль</dt><dd>{{ org.industry || 'не указано' }}</dd></div>
            <div><dt>Плательщик</dt><dd>{{ org.billing_name || 'не указано' }}</dd></div>
            <div><dt>VAT</dt><dd>{{ org.billing_vat || 'не указано' }}</dd></div>
            <div class="col-2"><dt>Адрес для счетов</dt><dd>{{ org.billing_address || 'не указано' }}</dd></div>

            <div><dt>Видимость</dt><dd>{{ org.visibility || 'private' }}</dd></div>
            <div class="col-2"><dt>Роль приглашённых по умолчанию</dt><dd>{{ org.default_role || 'member' }}</dd></div>
          </dl>

          <!-- EDIT MODE -->
          <div v-else class="form-grid">
            <label>
              <span>Сайт</span>
              <input v-model="editForm.website" class="input" placeholder="https://example.com" />
            </label>

            <label>
              <span>Email</span>
              <input v-model="editForm.email" class="input" />
            </label>

            <label>
              <span>Телефон</span>
              <input v-model="editForm.phone" class="input" />
            </label>

            <label>
              <span>Страна</span>
              <input v-model="editForm.country" class="input" />
            </label>

            <label>
              <span>Часовой пояс</span>
              <input v-model="editForm.timezone" class="input" />
            </label>

            <label class="col-span-2">
              <span>Адрес</span>
              <input v-model="editForm.address" class="input" />
            </label>

            <label class="col-span-2">
              <span>Описание</span>
              <textarea v-model="editForm.description" class="input textarea" />
            </label>

            <label class="col-span-2">
              <span>Отрасль</span>
              <input v-model="editForm.industry" class="input" />
            </label>

            <label>
              <span>Плательщик</span>
              <input v-model="editForm.billing_name" class="input" />
            </label>

            <label>
              <span>VAT</span>
              <input v-model="editForm.billing_vat" class="input" />
            </label>

            <label class="col-span-2">
              <span>Адрес для счетов</span>
              <input v-model="editForm.billing_address" class="input" />
            </label>

            <label>
              <span>Видимость</span>
              <select v-model="editForm.visibility" class="input">
                <option value="private">private</option>
                <option value="internal">internal</option>
                <option value="public">public</option>
              </select>
            </label>

            <label class="col-span-2">
              <span>Роль приглашённых по умолчанию</span>
              <select v-model="editForm.default_role" class="input">
                <option value="member">member</option>
                <option value="observer">observer</option>
                <option value="admin">admin</option>
              </select>
            </label>
          </div>
        </div>
      </div>
    </section>

    <!-- Участники -->
    <section class="card">
      <header class="card__header">
        <h3 class="card__title">Участники</h3>
      </header>
      <div class="card__body">
        <div class="table-wrap">
          <table class="table table--hover">
            <thead>
              <tr>
                <th>Участник</th>
                <th>Роль</th>
                <th>Статус</th>
                <th class="col-actions" v-if="canManageMembers">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in members" :key="m.user?.id">
                <td>
                  <div class="cell-main">
                    <div class="avatar avatar--sm">
                      <div class="avatar avatar--placeholder">{{ initials(m.user) }}</div>
                    </div>
                    <div class="cell-main__text">
                      <div class="title">{{ m.user?.full_name || m.user?.username || '—' }}</div>
                      <div class="muted">{{ m.user?.email || '—' }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <!-- селект убран для самого себя -->
                  <template v-if="canChangeRole(m) && toStr(m.user?.id) !== uid">
                    <select v-model="m.role" class="input input--sm" @change="changeRole(m)">
                      <option v-for="r in memberRoles" :key="r" :value="r">{{ r }}</option>
                    </select>
                  </template>
                  <span v-else class="badge badge--outline">{{ m.role || 'member' }}</span>
                </td>
                <td>
                  <span class="badge" :class="(m.status || 'pending') === 'accepted' ? 'badge--success' : 'badge--muted'">
                    {{ m.status || 'pending' }}
                  </span>
                </td>
                <td class="col-actions" v-if="canManageMembers">
                  <button class="btn btn--xs btn--ghost"
                          v-if="canManageMembers && toStr(m.user?.id) !== uid"
                          :disabled="m.role === 'owner'"
                          title="Удалить из организации"
                          @click="removeMember(m.user.id)">
                    Удалить
                  </button>
                </td>
              </tr>
              <tr v-if="members.length === 0"><td colspan="4" class="muted">Участников пока нет</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- Проекты -->
    <section class="card">
      <header class="card__header">
        <h3 class="card__title">Проекты</h3>
      </header>
      <div class="card__body">
        <div v-if="loadingProjects" class="text-center py-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
          </div>
        </div>
        <div v-else-if="projects.length === 0" class="text-center text-muted py-3">
          Проектов пока нет
        </div>
        <div v-else class="list-group">
          <router-link
            v-for="p in projects"
            :key="p.id"
            class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
            :to="`/crm/project-management/project/${p.id}`"
          >
            <div class="me-3">
              <div class="fw-bold">{{ p.name }}</div>
              <div class="small text-muted">
                <span v-if="p.organization">Орг: {{ p.organization.name }}</span>
                <span v-else>Орг: —</span>
                ·
                <span>Нач: {{ formatDate(p.start_date) }}</span>
                ·
                <span>Кон: {{ formatDate(p.end_date) }}</span>
              </div>
              <div class="small text-muted" v-if="p.tasks_count || p.task_count">
                {{ p.tasks_count || p.task_count }} задач
              </div>
            </div>
            <div class="text-end">
              <span class="badge rounded-pill me-2" :class="getProjectStatusClass(p.status)">
                {{ humanProjectStatus(p.status) }}
              </span>
              <span class="badge rounded-pill" :class="getPriorityClass(p.priority)">
                {{ humanPriority(p.priority) }}
              </span>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Задачи -->
    <section class="card">
      <header class="card__header">
        <h3 class="card__title">Задачи</h3>
      </header>
      <div class="card__body">
        <div v-if="loadingTasks" class="text-center py-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
          </div>
        </div>
        <div v-else-if="tasks.length === 0" class="text-center text-muted py-3">
          Задач пока нет
        </div>
        <div v-else class="list-group">
          <router-link
            v-for="t in tasks"
            :key="t.id"
            class="list-group-item list-group-item-action"
            :to="taskLink(t)"
          >
            <div class="d-flex justify-content-between align-items-start">
              <div class="me-3">
                <div class="fw-bold">{{ t.title || 'Без названия' }}</div>
                <div class="small text-muted d-flex align-items-center flex-wrap">
                  <span v-if="t.project">Проект: {{ t.project.name }}</span>
                  <span v-else>Без проекта</span>
                  <span class="mx-1">·</span>
                  <span v-if="t.assignee" class="d-flex align-items-center">
                    <img
                      :src="getAvatarUrl(t.assignee, 24)"
                      alt=""
                      class="rounded-circle me-1"
                      style="width:24px;height:24px;"
                    />
                    {{ t.assignee.full_name || t.assignee.username }}
                  </span>
                  <span v-else>Исполнитель: —</span>
                </div>
              </div>
              <div class="text-end">
                <div class="mb-1">
                  <span class="badge rounded-pill me-2" :class="getTaskStatusClass(t.status)">
                    {{ humanTaskStatus(t.status) }}
                  </span>
                  <span class="badge rounded-pill" :class="getPriorityClass(t.priority)">
                    {{ humanPriority(t.priority) }}
                  </span>
                </div>
                <div class="small" :class="dueClass(t.due_date, t.status)">
                  <i class="fas fa-clock me-1"></i>{{ formatDate(t.due_date) }}
                </div>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <!-- invite modal -->
    <OrganizationInviteModal
      v-if="showInvite"
      :org-id="id"
      :inviting="inviting"
      @close="showInvite = false"
      @submit="onInviteSubmit"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useUserStore } from '@/modules/cms/js/userStore.js';
import { storeToRefs } from 'pinia';
import { useRoute, useRouter } from 'vue-router';
import OrganizationApi from './js/organizationApi.js';
import OrganizationInviteModal from './components/OrganizationInviteModal.vue';
import { getAvatarUrl } from '@/modules/cms/js/avatarUtils.js';

export default {
  name: 'OrganizationDetails',
  components: { OrganizationInviteModal },
  setup() {
    const userStore = useUserStore();
    const { user, profile } = storeToRefs(userStore);
    const route = useRoute();
    const router = useRouter();
    const id = Number(route.params.id);

    const org = ref({});
    const members = ref([]);
    const myMember = ref(null);
    const isParticipant = ref(false);
    const projects = ref([]);
    const tasks = ref([]);

    const loadingOrg = ref(false);
    const loadingMembers = ref(false);
    const loadingProjects = ref(false);
    const loadingTasks = ref(false);
    const error = ref(null);

    const showInvite = ref(false);
    const inviting = ref(false);

    // === Редактирование общей информации ===
    const editMode = ref(false);
    const saving = ref(false);
    const editForm = ref({});

    const loadOrg = async () => {
      loadingOrg.value = true;
      try {
        const resp = await OrganizationApi.getOrganization(id);
        org.value = resp?.data || {};
        error.value = null;
      } catch (e) {
        error.value = e?.response?.data?.detail || 'Ошибка загрузки организации';
      } finally {
        loadingOrg.value = false;
      }
    };

    const loadMembers = async () => {
      loadingMembers.value = true;
      try {
        const resp = await OrganizationApi.getOrganizationMembers(id);
        members.value = resp?.data || [];
        updateMyMember();
      } finally { loadingMembers.value = false; }
    };

    const loadProjects = async () => {
      if (!org.value?.id) return;
      loadingProjects.value = true;
      try {
        const resp = await OrganizationApi.getOrganizationProjects(org.value.id, { page_size: 10 });
        const data = resp?.data;
        projects.value = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : []);
      } finally {
        loadingProjects.value = false;
      }
    };

    const loadTasks = async () => {
      if (!org.value?.id) return;
      loadingTasks.value = true;
      try {
        const resp = await OrganizationApi.getOrganizationTasks(org.value.id, { page_size: 10 });
        const data = resp?.data;
        tasks.value = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : []);
      } finally {
        loadingTasks.value = false;
      }
    };

    // ====== Хелперы ======
    const formatDate = (date) => {
      if (!date) return '—';
      return new Date(date).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    };

    const projectStatusClasses = {
      planning: 'bg-secondary',
      active: 'bg-success',
      on_hold: 'bg-warning text-dark',
      completed: 'bg-primary',
      cancelled: 'bg-danger'
    };

    const projectStatusTexts = {
      planning: 'Планирование',
      active: 'Активный',
      on_hold: 'На паузе',
      completed: 'Завершен',
      cancelled: 'Отменен'
    };

    const taskStatusClasses = {
      todo: 'bg-secondary',
      in_progress: 'bg-info',
      review: 'bg-warning text-dark',
      done: 'bg-success',
      cancelled: 'bg-danger'
    };

    const taskStatusTexts = {
      todo: 'К выполнению',
      in_progress: 'В работе',
      review: 'На проверке',
      done: 'Готово',
      cancelled: 'Отменена'
    };

    const priorityClasses = {
      low: 'bg-light text-dark',
      medium: 'bg-info',
      high: 'bg-warning text-dark',
      urgent: 'bg-danger'
    };

    const priorityTexts = {
      low: 'Низкий',
      medium: 'Средний',
      high: 'Высокий',
      urgent: 'Срочный'
    };

    const getProjectStatusClass = (s) => projectStatusClasses[s] || 'bg-secondary';
    const getTaskStatusClass = (s) => taskStatusClasses[s] || 'bg-secondary';
    const getPriorityClass = (p) => priorityClasses[p] || 'bg-light text-dark';
    const humanProjectStatus = (s) => projectStatusTexts[s] || s;
    const humanTaskStatus = (s) => taskStatusTexts[s] || s;
    const humanPriority = (p) => priorityTexts[p] || p;

    const dueClass = (due, status) => {
      if (!due) return 'text-muted';
      if (status === 'done') return 'text-muted';
      const now = new Date();
      const d = new Date(due);
      if (d < now) return 'text-danger fw-bold';
      if (d - now < 24 * 60 * 60 * 1000) return 'text-warning fw-bold';
      return 'text-muted';
    };

    const taskLink = (task) => `/crm/project-management/task/${task.id}`;

    // ====== ПРАВА (как в списке) ======
    const toStr = v => (v == null ? null : String(v));
    const uid = computed(() => toStr(user.value?.id ?? profile.value?.id));

    const defaultPerms = {
      view: false,
      edit_org: false,
      manage_members: false,
      invite: false,
      delete_org: false,
      project_create: false,
      task_assign: false
    };
    const abilities = computed(() => org.value?.my_membership?.permissions ?? defaultPerms);
    const role = computed(() => org.value?.my_membership?.role ?? null);
    const isOwner = computed(() => role.value === 'owner');
    const isAdmin = computed(() => role.value === 'admin');
    const isMember = computed(() => role.value === 'member');
    const isObserver = computed(() => role.value === 'observer');

    const canView = computed(() => !!abilities.value.view);
    const canEditOrg = computed(() => !!abilities.value.edit_org);
    const canManageMembers = computed(() => !!abilities.value.manage_members);
    const canInvite = computed(() => !!abilities.value.invite);
    const canDeleteOrg = computed(() => !!abilities.value.delete_org);
    const canCreateProject = computed(() => !!abilities.value.project_create);
    const canAssignTasks = computed(() => !!abilities.value.task_assign);
    const canLeave = computed(() => {
      const owners = (members.value ?? []).filter(m => m.role === 'owner');
      return isOwner.value ? owners.length > 1 : true;
    });

    function updateMyMember() {
      myMember.value = members.value.find(m => toStr(m.user?.id) === uid.value) || null;
      isParticipant.value = !!myMember.value;
    }
    watch([members, uid], updateMyMember, { immediate: true });

    const myRole = (o) =>
      (o?.my_membership?.role) ||
      (toStr(o?.owner?.id ?? o?.owner_id) === uid.value ? 'owner' : 'member');

    const memberRoles = computed(() =>
      isOwner.value ? ['owner', 'admin', 'member', 'observer'] : ['admin', 'member', 'observer']
    );

    const canChangeRole = (m) =>
      canManageMembers.value && toStr(m.user?.id) !== uid.value && !(m.role === 'owner' && !isOwner.value);

    const initials = (u) => (u?.full_name || u?.username || u?.email || 'U').slice(0,1).toUpperCase();

    const changeRole = async (m) => {
      try {
        await OrganizationApi.updateMemberRole(id, m.id, m.role);
        await Promise.all([loadMembers(), loadOrg()]);
      } catch (e) {
        alert(e?.response?.data?.detail || 'Ошибка изменения роли');
      }
    };

    const removeMember = async (userIdToRemove) => {
      if (!confirm('Удалить участника из организации?')) return;
      try {
        await OrganizationApi.removeOrganizationMember(id, userIdToRemove);
        await loadMembers();
      } catch (e) {
        alert(e?.response?.data?.detail || 'Ошибка удаления участника');
      }
    };

    const onInviteSubmit = async ({ email, role }) => {
      inviting.value = true;
      try {
        await OrganizationApi.inviteToOrganization(id, { email, role });
        showInvite.value = false;
        await loadMembers();
      } catch (e) {
        alert(e?.response?.data?.detail || 'Ошибка приглашения');
      } finally {
        inviting.value = false;
      }
    };

    const onDelete = async () => {
      if (!confirm('Удалить организацию? Это действие нельзя отменить.')) return;
      try {
        await OrganizationApi.deleteOrganization(id);
        router.push({ name: 'OrganizationList' });
      } catch (e) {
        alert(e?.response?.data?.detail || 'Ошибка удаления');
      }
    };

    const onLeave = async () => {
      if (!confirm('Выйти из организации?')) return;
      try {
        await OrganizationApi.leaveOrganization(id);
        router.push({ name: 'OrganizationList' });
      } catch (e) {
        alert(e?.response?.data?.detail || 'Ошибка выхода');
      }
    };

    // === редактирование: старт/отмена/сохранение ===
    const startEdit = () => {
      editForm.value = {
        visibility: 'private',
        default_role: 'member',
        status: 'active',
        ...org.value,
      };
      editMode.value = true;
    };
    const cancelEdit = () => {
      editForm.value = { ...org.value };
      editMode.value = false;
    };
    const sanitizePatch = (data) => {
      const allowed = ['name','website','email','phone','country','timezone','address','description','industry','billing_name','billing_vat','billing_address','visibility','default_role','status'];
      const patch = {};
      allowed.forEach(k => {
        const val = data[k];
        if (val !== undefined && val !== null && val !== '' && val !== org.value[k]) {
          patch[k] = val;
        }
      });
      if (patch.default_role === 'owner') patch.default_role = 'member';
      return patch;
    };
    const saveInfo = async () => {
      saving.value = true;
      try {
        await OrganizationApi.updateOrganization(id, sanitizePatch(editForm.value));
        await loadOrg();
        editMode.value = false;
      } catch (e) {
        alert(e?.response?.data?.detail || 'Ошибка сохранения');
      } finally {
        saving.value = false;
      }
    };

    // синхронизация формы, если org обновился вне редактирования
    watch(org, (val) => {
      if (!editMode.value) editForm.value = { ...val };
    }, { deep: true });

    const membersCount = computed(() =>
      org.value?.members_count ?? members.value?.length ?? 0
    );

    onMounted(async () => {
      await loadOrg();
      if (!error.value) {
        await Promise.all([loadMembers(), loadProjects(), loadTasks()]);
        editForm.value = { ...org.value };
      }
    });

    return {
      id,

      org, members, projects, tasks,
      loadingOrg, loadingMembers, loadingProjects, loadingTasks,
      showInvite, inviting, onInviteSubmit,
      error,

      // права
      uid, toStr,
      isParticipant, role, isObserver, isMember, isOwner, isAdmin,
      abilities, canView, canEditOrg, canManageMembers, canInvite, canDeleteOrg,
      canCreateProject, canAssignTasks, canLeave, myRole, membersCount,

      // members
      initials, removeMember, changeRole, memberRoles, canChangeRole,

      // действия
      onDelete, onLeave,

      // edit
      editMode, startEdit, cancelEdit, saveInfo, saving, editForm
      ,
      // helpers
      formatDate,
      getProjectStatusClass,
      getTaskStatusClass,
      getPriorityClass,
      humanProjectStatus,
      humanTaskStatus,
      humanPriority,
      dueClass,
      taskLink,
      getAvatarUrl
    };
  }
};
</script>

<style scoped lang="scss">
.orgs-scope {
  .toolbar { display:flex; gap:8px; align-items:center; flex-wrap: wrap; }
  .toolbar__edit { display:flex; gap:8px; align-items:center; }
  .btn--danger { border-color: rgba(220,38,38,.3); color:#dc2626; }
  .btn--danger:hover { background:#fee2e2; }

  .name-stack > .input { display:block; margin-bottom:6px; }

  .dl { display:grid; grid-template-columns: 1fr; gap: 12px; }
  .dl > div { display:grid; grid-template-columns: 200px 1fr; gap: 12px; align-items:center; }
  .dl .col-2 { grid-column: 1 / -1; }

  /* Режим редактирования — аккуратная сетка */
  .form-grid {
    display:grid;
    grid-template-columns: 200px 1fr;
    gap: 12px 16px;
    align-items:start;
  }
  .form-grid > label { display:grid; grid-template-columns: 200px 1fr; gap: 8px; align-items:center; }
  .form-grid .col-span-2 { grid-column: 1 / -1; display:grid; grid-template-columns: 200px 1fr; gap: 8px; }
  .form-grid .col-span-2 > textarea { grid-column: 2 / -1; min-height: 140px; }
  .form-grid .col-span-2 > select { grid-column: 2 / -1; }

  @media (max-width: 768px) {
    .dl > div { grid-template-columns: 1fr; align-items: start; }
    .form-grid, .form-grid .col-span-2 { grid-template-columns: 1fr; }
    .form-grid > label > span, .form-grid .col-span-2 > span { margin-bottom: 6px; }
  }
}

.input { width: 100%; padding: 8px 10px; border: 1px solid #3b3f3f; border-radius: 6px; background: transparent; color: inherit; }
.input--sm { padding: 6px 8px; }
.input--md { padding: 8px 10px; }
.textarea { min-height: 110px; resize: vertical; }
</style>
