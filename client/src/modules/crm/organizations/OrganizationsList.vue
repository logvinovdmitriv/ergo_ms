<template>
  <section class="card">
    <header class="card__header">
      <h2 class="card__title">Организации</h2>

      <div class="toolbar">
        <div class="toolbar__left">
          <input v-model="q" class="input input--sm" placeholder="Поиск по названию…" />
        </div>
        <div class="toolbar__right">
          <button class="btn btn--sm btn--ghost" @click="load" :disabled="loading">Обновить</button>
          <router-link class="btn btn--sm btn--primary" to="/crm/organizations/new">Создать</router-link>
        </div>
      </div>
    </header>

    <div class="card__body">
      <div v-if="!loading && filtered.length === 0" class="empty">
        <p class="muted">Пока нет организаций.</p>
        <router-link class="btn btn--primary btn--sm" to="/crm/organizations/new">Создать первую</router-link>
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
              <td colspan="5"><div class="skeleton skeleton--row"></div></td>
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
                      <button class="btn btn--sm btn--primary" @click="saveEdit(org.id)">Сохранить</button>
                      <button class="btn btn--sm btn--ghost" @click="cancelEdit">Отмена</button>
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
                  @click="startEdit(org)"
                >
                  Редактировать
                </button>
                <router-link
                  class="btn btn--xs btn--link"
                  :to="`/crm/organizations/${org.id}`"
                  title="Открыть"
                >Открыть</router-link>
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
    const userId = store.state?.auth?.user?.id;

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
      if (!term) return organizations.value;
      return organizations.value.filter(o => (o.name || '').toLowerCase().includes(term));
    });

    const isOwner = (org) => org?.owner && org.owner.id === userId;
    const myRole = (org) => (isOwner(org) ? 'owner' : (org.my_role || 'member'));

    const startEdit = (org) => { editingId.value = org.id; editName.value = org.name; };
    const cancelEdit = () => { editingId.value = null; };
    const saveEdit = async (orgId) => {
      await OrganizationApi.updateOrganization(orgId, { name: editName.value });
      editingId.value = null;
      await load();
    };

    const goDetails = (id) => router.push(`/crm/organizations/${id}`);

    onMounted(load);

    return {
      organizations, loading, q,
      editingId, editName, startEdit, cancelEdit, saveEdit,
      filtered, isOwner, myRole, load, goDetails
    };
  }
};
</script>
