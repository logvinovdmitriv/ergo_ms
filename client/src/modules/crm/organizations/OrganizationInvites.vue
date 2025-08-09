<template>
  <section class="card">
    <header class="card__header">
      <h2 class="card__title">Приглашения</h2>
      <div class="muted">Показываются только приглашения со статусом pending</div>
    </header>

    <div class="card__body">
      <div v-if="!loading && invites.length === 0" class="empty">
        <p class="muted">Новых приглашений нет.</p>
      </div>

      <div v-else class="table-wrap">
        <table class="table table--compact">
          <thead>
            <tr>
              <th>Организация</th>
              <th class="hide-sm">Роль</th>
              <th class="hide-sm">Истекает</th>
              <th class="col-actions">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="4"><div class="skeleton skeleton--row"></div></td>
            </tr>
            <tr v-for="invite in invites" :key="invite.id">
              <td>{{ invite.organization?.name || invite.organization }}</td>
              <td class="hide-sm"><span class="badge badge--outline">{{ invite.role || 'member' }}</span></td>
              <td class="hide-sm"><span class="muted">{{ invite.expires_at ? formatDate(invite.expires_at) : '—' }}</span></td>
              <td class="col-actions">
                <button class="btn btn--xs btn--primary" @click="accept(invite.token)">Принять</button>
                <button class="btn btn--xs btn--ghost" @click="decline(invite.token)">Отклонить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script>
import { ref, onMounted } from 'vue';
import OrganizationApi from './js/organizationApi.js';

export default {
  name: 'OrganizationInvites',
  setup() {
    const invites = ref([]);
    const loading = ref(false);

    const load = async () => {
      loading.value = true;
      try {
        const resp = await OrganizationApi.getInvites();
        invites.value = resp?.data || [];
      } finally {
        loading.value = false;
      }
    };

    const accept = async (token) => { try { await OrganizationApi.acceptInvite(token); } finally { await load(); } };
    const decline = async (token) => { try { await OrganizationApi.declineInvite(token); } finally { await load(); } };

    const formatDate = (iso) => new Date(iso).toLocaleString();

    onMounted(load);
    return { invites, loading, accept, decline, formatDate };
  }
};
</script>
