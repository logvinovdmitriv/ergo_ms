<template>
  <div class="org-details orgs-scope">
    <!-- Общая информация -->
    <section class="card">
      <header class="card__header">
        <h2 class="card__title">Общая информация</h2>

        <div class="toolbar">
          <button v-if="canManage" class="btn btn--sm btn--danger btn--ghost" @click="onDelete">
            Удалить организацию
          </button>
          <button v-if="isParticipant" class="btn btn--sm btn--ghost" @click="onLeave">
            Выйти из организации
          </button>
        </div>
      </header>

      <div class="card__body">
        <div v-if="loadingOrg"><div class="skeleton skeleton--row"></div></div>

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
                v-if="!editMode && canManage"
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

              <button v-if="canInvite" class="btn btn--sm btn--primary" @click="showInvite = true">
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
                <option value="viewer">viewer</option>
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
                <th class="col-actions" v-if="canManage">Действия</th>
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
                <td class="col-actions" v-if="canManage">
                  <button class="btn btn--xs btn--ghost"
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
        <div v-if="loadingProjects"><div class="skeleton skeleton--row"></div></div>
        <div v-else>
          <ul>
            <li v-for="p in projects" :key="p.id">
              <router-link :to="{ name: 'ProjectDetail', params: { id: p.id } }">{{ p.name }}</router-link>
            </li>
            <li v-if="projects.length === 0" class="muted">Проектов пока нет</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Задачи -->
    <section class="card">
      <header class="card__header">
        <h3 class="card__title">Задачи</h3>
      </header>
      <div class="card__body">
        <div v-if="loadingTasks"><div class="skeleton skeleton--row"></div></div>
        <div v-else>
          <ul>
            <li v-for="t in tasks" :key="t.id">
              <router-link :to="{ name: 'TaskDetail', params: { id: t.id } }">{{ t.title }}</router-link>
            </li>
            <li v-if="tasks.length === 0" class="muted">Задач пока нет</li>
          </ul>
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
      } finally { loadingOrg.value = false; }
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
      loadingProjects.value = true;
      try {
        const resp = await OrganizationApi.getProjects(id);
        projects.value = resp?.data?.results || resp?.data || [];
      } finally { loadingProjects.value = false; }
    };

    const loadTasks = async () => {
      loadingTasks.value = true;
      try {
        const resp = await OrganizationApi.getTasks(id);
        tasks.value = resp?.data?.results || resp?.data || [];
      } finally { loadingTasks.value = false; }
    };

    // ====== ПРАВА (как в списке) ======
    const toStr = v => (v == null ? null : String(v));
    const uid = computed(() => toStr(user.value?.id ?? profile.value?.id));
    const ownerIdFromOrg = computed(() => toStr(org.value?.owner?.id ?? org.value?.owner_id));

    const isOwner = computed(() =>
      org.value?.my_role === 'owner' || (uid.value && ownerIdFromOrg.value === uid.value)
    );

    const isAdminFromMembers = computed(() => ['admin', 'owner'].includes(myMember.value?.role));
    const isAdmin = computed(() => org.value?.my_role === 'admin' || isAdminFromMembers.value);

    const canInvite = computed(() => isOwner.value || isAdmin.value);
    const canManage = canInvite;

    function updateMyMember() {
      myMember.value = members.value.find(m => toStr(m.user?.id) === uid.value) || null;
      isParticipant.value = !!myMember.value;
    }
    watch([members, uid], updateMyMember, { immediate: true });

    const myRole = (o) =>
      (o?.my_role) ||
      (toStr(o?.owner?.id ?? o?.owner_id) === uid.value ? 'owner' : 'member');

    const memberRoles = computed(() =>
      isOwner.value ? ['owner', 'admin', 'member', 'viewer'] : ['admin', 'member', 'viewer']
    );

    const canChangeRole = (m) =>
      (isOwner.value || isAdmin.value) && toStr(m.user?.id) !== uid.value && m.role !== 'owner';

    const initials = (u) => (u?.full_name || u?.username || u?.email || 'U').slice(0,1).toUpperCase();

    const changeRole = async (m) => {
      try {
        await OrganizationApi.updateOrganizationMember(id, m.user.id, { role: m.role });
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
      if (isOwner.value) {
        alert('Вы владелец организации. Сначала передайте статус владельца.');
        return;
      }
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
      await Promise.all([loadOrg(), loadMembers(), loadProjects(), loadTasks()]);
      editForm.value = { ...org.value };
    });

    return {
      id,

      org, members, projects, tasks,
      loadingOrg, loadingMembers, loadingProjects, loadingTasks,
      showInvite, inviting, onInviteSubmit,

      // права
      uid, toStr,
      isParticipant, isOwner, isAdmin, canInvite, canManage, myRole,
      membersCount,

      // members
      initials, removeMember, changeRole, memberRoles, canChangeRole,

      // действия
      onDelete, onLeave,

      // edit
      editMode, startEdit, cancelEdit, saveInfo, saving, editForm
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
