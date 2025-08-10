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

          <!-- Редактирование общей информации -->
          <button
            v-if="canInvite && !editMode"
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
                  <div class="title">{{ org.name || 'Без названия' }}</div>
                  <div class="muted" v-if="org.slug">@{{ org.slug }}</div>
                </template>
                <template v-else>
                  <input v-model="editForm.name" class="input input--md" placeholder="Название" />
                  <input v-model="editForm.slug" class="input input--sm" placeholder="slug" />
                </template>
              </div>
            </div>

            <div class="org-meta">
              <span class="badge" :class="(org.status || 'active') === 'active' ? 'badge--success' : 'badge--muted'">
                {{ org.status || 'active' }}
              </span>
              <span class="badge badge--outline">{{ myRole(org) }}</span>
              <span class="badge badge--neutral">{{ org.members_count ?? members.length ?? 0 }} участника</span>
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
              <input v-model="editForm.website" class="input" placeholder="https://…" />
            </label>

            <label>
              <span>Email</span>
              <input v-model="editForm.email" class="input" placeholder="name@domain" />
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
              <input v-model="editForm.timezone" class="input" placeholder="Europe/Moscow" />
            </label>

            <label class="col-span-2">
              <span>Адрес</span>
              <input v-model="editForm.address" class="input" />
            </label>

            <label class="col-span-2">
              <span>Описание</span>
              <textarea v-model="editForm.description" class="input textarea" rows="4"></textarea>
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
                <option value="admin">admin</option>
                <option value="viewer">viewer</option>
              </select>
            </label>

            <label>
              <span>Статус</span>
              <select v-model="editForm.status" class="input">
                <option value="active">active</option>
                <option value="archived">archived</option>
              </select>
            </label>
          </div>
        </div>
      </div>
    </section>

    <!-- Участники -->
    <section class="card">
      <header class="card__header">
        <h2 class="card__title">Участники</h2>
        <div class="toolbar" v-if="canInvite">
          <button class="btn btn--sm btn--primary" @click="showInvite = true">Пригласить</button>
        </div>
      </header>

      <div class="card__body">
        <div v-if="loadingMembers"><div class="skeleton skeleton--row"></div></div>

        <div v-else class="table-wrap">
          <table class="table table--compact">
            <thead>
              <tr>
                <th>Пользователь</th>
                <th>Роль</th>
                <th>Статус</th>
                <th class="col-actions" v-if="canManage">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in members" :key="m.user?.id || m.id">
                <td>
                  <div class="cell-main">
                    <div class="avatar">{{ initials(m.user) }}</div>
                    <div>
                      <div class="title">{{ m.user?.full_name || m.user?.username || m.user?.email || 'Пользователь' }}</div>
                      <div class="muted">{{ m.user?.email || '—' }}</div>
                    </div>
                  </div>
                </td>
                <td><span class="badge badge--outline">{{ m.role || 'member' }}</span></td>
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

    <!-- Проекты организации -->
    <section class="card">
      <header class="card__header">
        <h2 class="card__title">Проекты организации</h2>
      </header>
      <div class="card__body">
        <div v-if="loadingProjects"><div class="skeleton skeleton--row"></div></div>

        <div v-else-if="projects.length === 0" class="empty">
          <p class="muted">Проектов пока нет.</p>
          <router-link class="btn btn--sm btn--primary" to="/crm/project-management/my-projects">К проектам</router-link>
        </div>

        <div v-else class="table-wrap">
          <table class="table table--compact">
            <thead><tr><th>Название</th><th class="hide-sm">Статус</th></tr></thead>
            <tbody>
              <tr v-for="p in projects" :key="p.id">
                <td>{{ p.name }}</td>
                <td class="hide-sm"><span class="badge badge--outline">{{ p.status || 'active' }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- Модалка приглашения -->
    <OrganizationInviteModal
      v-if="showInvite"
      :org="org"
      :loading="inviting"
      @close="showInvite = false"
      @submit="onInviteSubmit"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';
import OrganizationApi from './js/organizationApi.js';
import OrganizationInviteModal from './components/OrganizationInviteModal.vue';

export default {
  name: 'OrganizationDetails',
  components: { OrganizationInviteModal },
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    const id = Number(route.params.id);

    const org = ref({});
    const members = ref([]);
    const projects = ref([]);

    const loadingOrg = ref(false);
    const loadingMembers = ref(false);
    const loadingProjects = ref(false);

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
      } finally { loadingMembers.value = false; }
    };

    const loadProjects = async () => {
      loadingProjects.value = true;
      try {
        const resp = await OrganizationApi.getProjects(id);
        projects.value = resp?.data?.results || resp?.data || [];
      } finally { loadingProjects.value = false; }
    };

    // ====== ПРАВА (как в списке) ======
    const toStr = v => (v == null ? null : String(v));
    const uid = computed(() => toStr(store.state?.auth?.user?.id));
    const ownerIdFromOrg = computed(() => toStr(org.value?.owner?.id ?? org.value?.owner_id));

    const isOwner = computed(() =>
      org.value?.my_role === 'owner' || (uid.value && ownerIdFromOrg.value === uid.value)
    );

    const myMember = computed(() => members.value.find(m => toStr(m.user?.id) === uid.value));
    const isAdminFromMembers = computed(() => ['admin', 'owner'].includes(myMember.value?.role));
    const isAdmin = computed(() => org.value?.my_role === 'admin' || isAdminFromMembers.value);

    const canInvite = computed(() => isOwner.value || isAdmin.value);
    const canManage = canInvite;

    const myRole = (o) =>
      (o?.my_role) ||
      (toStr(o?.owner?.id ?? o?.owner_id) === uid.value ? 'owner' : 'member');

    const initials = (u) => (u?.full_name || u?.username || u?.email || 'U').slice(0,1).toUpperCase();

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
        editMode.value = false;
        await loadOrg();
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

    onMounted(async () => {
      await Promise.all([loadOrg(), loadMembers(), loadProjects()]);
      editForm.value = { ...org.value };
    });

    return {
      org, members, projects,
      loadingOrg, loadingMembers, loadingProjects,
      showInvite, inviting, onInviteSubmit,

      // права
      myRole, canInvite, canManage, isOwner,

      // members
      initials, removeMember,

      // удаление
      onDelete,

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
    gap: 12px 14px;
    align-items:center;
  }
  .form-grid > label { display:contents; }
  .form-grid > label > span {
    grid-column: 1 / 2;
    color: var(--muted, #9ca3af);
    font-size: 0.9rem;
  }
  .form-grid > label > .input,
  .form-grid > label > .textarea,
  .form-grid > label > select {
    grid-column: 2 / -1;
    width: 100%;
  }
  .form-grid .col-span-2 { grid-column: 1 / -1; display:grid; grid-template-columns: 200px 1fr; gap: 12px 14px; }
  .form-grid .col-span-2 > span { grid-column: 1 / 2; }
  .form-grid .col-span-2 > .input,
  .form-grid .col-span-2 > .textarea,
  .form-grid .col-span-2 > select { grid-column: 2 / -1; }

  @media (max-width: 768px) {
    .dl > div { grid-template-columns: 1fr; align-items: start; }
    .form-grid, .form-grid .col-span-2 { grid-template-columns: 1fr; }
    .form-grid > label > span, .form-grid .col-span-2 > span { margin-bottom: 6px; }
  }
}

.input { width: 100%; padding: 8px 10px; border: 1px solid #3b3f46; border-radius: 6px; background: transparent; color: inherit; }
.input--sm { padding: 6px 8px; }
.input--md { padding: 8px 10px; }
.textarea { min-height: 110px; resize: vertical; }
</style>
