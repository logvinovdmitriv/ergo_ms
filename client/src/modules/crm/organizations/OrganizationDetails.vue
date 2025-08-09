<template>
  <div class="org-details orgs-scope">
    <!-- Общая информация -->
    <section class="card">
      <header class="card__header">
        <h2 class="card__title">Общая информация</h2>

        <div class="toolbar">
          <button v-if="isOwner" class="btn btn--sm btn--danger btn--ghost" @click="onDelete">
            Удалить организацию
          </button>
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

              <div>
                <div class="title">{{ org.name || 'Без названия' }}</div>
                <div class="muted" v-if="org.slug">@{{ org.slug }}</div>
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

          <dl class="dl dl--grid">
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
          </dl>
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
import { ref, computed, onMounted } from 'vue';
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
    const userId = store.state?.auth?.user?.id;
    const id = Number(route.params.id);

    const org = ref({});
    const members = ref([]);
    const projects = ref([]);

    const loadingOrg = ref(false);
    const loadingMembers = ref(false);
    const loadingProjects = ref(false);

    const showInvite = ref(false);
    const inviting = ref(false);

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

    const isOwner = computed(() => org.value?.owner && org.value.owner.id === userId);
    const myRole  = (o) => (o?.owner?.id === userId ? 'owner' : (o?.my_role || 'member'));
    const canInvite = computed(() => isOwner.value || members.value.some(m => m.user?.id === userId && (m.role === 'admin' || m.role === 'owner')));
    const canManage = canInvite;

    const initials = (u) => (u?.full_name || u?.username || u?.email || 'U').slice(0,1).toUpperCase();

    const removeMember = async (userIdToRemove) => {
      if (!confirm('Удалить участника из организации?')) return;
      await OrganizationApi.removeOrganizationMember(id, userIdToRemove);
      await loadMembers();
    };

    const onInviteSubmit = async ({ email, role }) => {
      inviting.value = true;
      try {
        await OrganizationApi.inviteToOrganization(id, { email, role });
        showInvite.value = false;
        await loadMembers();
      } finally {
        inviting.value = false;
      }
    };

    const onDelete = async () => {
      if (!confirm('Удалить организацию? Это действие нельзя отменить.')) return;
      await OrganizationApi.deleteOrganization(id);
      router.push({ name: 'OrganizationList' });
    };

    onMounted(async () => {
      await Promise.all([loadOrg(), loadMembers(), loadProjects()]);
    });

    return {
      org, members, projects,
      loadingOrg, loadingMembers, loadingProjects,
      showInvite, inviting, onInviteSubmit,
      myRole, canInvite, canManage, initials, removeMember,
      isOwner: isOwner.value, onDelete
    };
  }
};
</script>

<style scoped lang="scss">
.orgs-scope {
  .toolbar { display:flex; gap:8px; align-items:center; }
  .btn--danger { border-color: rgba(220,38,38,.3); color:#dc2626; }
  .btn--danger:hover { background:#fee2e2; }
  .dl { display:grid; grid-template-columns: 1fr; gap: 12px; }
  .dl > div { display:grid; grid-template-columns: 180px 1fr; gap: 12px; align-items:start; }
  .dl .col-2 { grid-column: 1 / -1; }
  @media (max-width: 768px) { .dl > div { grid-template-columns: 1fr; } }
}
</style>
