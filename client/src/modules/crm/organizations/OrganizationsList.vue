<template>
  <section class="card orgs-scope">
    <header class="card__header">
      <h2 class="card__title">Организации</h2>
      <div class="toolbar">
        <div class="toolbar__left">
          <input v-model="q" class="input input--sm" placeholder="Поиск по названию…" />
        </div>
        <div class="toolbar__right">
          <button class="btn btn--sm btn--ghost" @click="load" :disabled="loading">
            Обновить
          </button>
          <router-link class="btn btn--sm btn--primary" :to="{ name: 'OrganizationNew' }">
            Создать
          </router-link>
        </div>
      </div>
    </header>

    <div class="card__body">
      <div v-if="!loading && filtered.length === 0" class="empty">
        <p class="muted">Пока нет организаций.</p>
        <router-link class="btn btn--primary btn--sm" :to="{ name: 'OrganizationNew' }">
          Создать первую
        </router-link>
      </div>

      <div v-else class="table-wrap">
        <table class="table table--hover table--compact">
          <thead>
            <tr>
              <th>Название</th>
              <th class="hide-sm">Статус</th>
              <th class="hide-sm">Моя роль</th>
              <th>Участники</th>
              <th class="col-actions">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="5">
                <div class="skeleton skeleton--row"></div>
              </td>
            </tr>

            <tr
              v-for="org in filtered"
              :key="org.id"
              class="row--clickable"
              @click="goDetails(org.id)"
            >
              <td>
                <div class="cell-main">
                  <div class="avatar" v-if="org.logo_url"><img :src="org.logo_url" alt="" /></div>
                  <div class="avatar avatar--placeholder" v-else>{{ org.name?.[0] || 'О' }}</div>

                  <div class="cell-main__text">
                    <div v-if="editingId === org.id" class="inline-edit" @click.stop>
                      <input v-model="editName" class="input input--sm" />
                      <button class="btn btn--sm btn--primary" @click.stop="saveEdit(org.id)">Сохранить</button>
                      <button class="btn btn--sm btn--ghost" @click.stop="cancelEdit">Отмена</button>
                    </div>
                    <template v-else>
                      <div class="title">
                        {{ org.name }}
                        <span v-if="isOwner(org)" class="badge badge--outline">владелец</span>
                      </div>
                      <div class="muted slug" v-if="org.slug">@{{ org.slug }}</div>
                    </template>
                  </div>
                </div>
              </td>

              <td class="hide-sm">
                <span class="badge" :class="org.status === 'active' ? 'badge--success' : 'badge--muted'">
                  {{ org.status || 'active' }}
                </span>
              </td>

              <td class="hide-sm">
                <span class="badge badge--outline">{{ myRole(org) }}</span>
              </td>

              <td>
                <span class="badge badge--neutral">
                  {{ org.members_count ?? org.members?.length ?? 0 }}
                </span>
              </td>

              <td class="col-actions" @click.stop>
                <button
                  v-if="isOwner(org)"
                  class="btn btn--xs btn--link"
                  title="Редактировать"
                  @click.stop="startEdit(org)"
                >
                  Ред.
                </button>
                <router-link
                  class="btn btn--xs btn--link"
                  title="Открыть"
                  :to="{ name: 'OrganizationDetails', params: { id: org.id } }"
                  @click.stop
                >
                  Откр.
                </router-link>
                <button
                  v-if="isOwner(org)"
                  class="btn btn--xs btn--ghost btn--danger"
                  title="Удалить организацию"
                  @click.stop="deleteOrg(org.id)"
                >
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import OrganizationApi from './js/organizationApi.js';

export default {
  name: 'OrganizationsList',
  setup() {
    const store = useStore();
    const router = useRouter();

    // Нормализованный id текущего пользователя (реактивно и без .value гонок)
    const toStr = v => (v == null ? null : String(v));
    const uid   = computed(() => toStr(store.state?.auth?.user?.id));

    const organizations = ref([]);
    const loading = ref(false);
    const q = ref('');

    const editingId = ref(null);
    const editName = ref('');

    const load = async () => {
      loading.value = true;
      try {
        const resp = await OrganizationApi.getOrganizations();
        organizations.value = resp?.data?.results || resp?.data || [];
      } finally {
        loading.value = false;
      }
    };

    const filtered = computed(() => {
      const term = q.value.trim().toLowerCase();
      const items = organizations.value || [];
      if (!term) return items;
      return items.filter(o => (o?.name || '').toLowerCase().includes(term));
    });

    // методы
    const isOwner = (o) =>
      o?.my_role === 'owner' || toStr(o?.owner?.id ?? o?.owner_id) === uid.value;

    async function remove(o) {
      if (!confirm(`Удалить организацию «${o.name}»?`)) return;
      await OrganizationApi.deleteOrganization(o.id);
      await load();
    }

    const myRole = (org) => (isOwner(org) ? 'owner' : (org.my_role || 'member'));

    const startEdit = (org) => { editingId.value = org.id; editName.value = org.name || ''; };
    const cancelEdit = () => { editingId.value = null; editName.value = ''; };
    const saveEdit = async (orgId) => {
      await OrganizationApi.updateOrganization(orgId, { name: editName.value });
      editingId.value = null;
      await load();
    };

    const deleteOrg = async (id) => {
      if (!confirm('Удалить организацию? Это действие нельзя отменить.')) return;
      await OrganizationApi.deleteOrganization(id);
      await load();
    };

    const goDetails = (id) => {
      router.push({ name: 'OrganizationDetails', params: { id } });
    };

    onMounted(load);

    return {
      organizations, loading, q,
      editingId, editName, startEdit, cancelEdit, saveEdit,
      filtered, isOwner, myRole, load, deleteOrg, goDetails
    };
  }
};
</script>

<style scoped lang="scss">
.orgs-scope {
  --gap: 16px; --radius: 8px; --muted: #6b7280;

  .toolbar { display:flex; gap:12px; align-items:center; justify-content:space-between; }
  .toolbar__left, .toolbar__right { display:flex; gap:8px; align-items:center; }

  .table-wrap { width:100%; overflow:auto; }
  .table { width:100%; border-collapse:collapse; }
  .table th, .table td { padding:10px 12px; border-bottom:1px solid rgba(0,0,0,.06); }
  .table--hover tbody tr:hover { background:#fafafa; }

  .cell-main { display:flex; align-items:center; gap:12px; }
  .avatar { width:32px; height:32px; border-radius:50%; overflow:hidden; background:#f3f4f6; display:flex; align-items:center; justify-content:center; font-weight:600; }
  .avatar img { width:100%; height:100%; object-fit:cover; }
  .avatar--placeholder { color:#374151; }
  .title { font-weight:600; }
  .slug { font-size:12px; }

  .btn--danger { border-color: rgba(220,38,38,.3); color:#dc2626; }
  .btn--danger:hover { background: #fee2e2; }

  @media (max-width: 768px) { .hide-sm { display:none; } }
}
</style>
