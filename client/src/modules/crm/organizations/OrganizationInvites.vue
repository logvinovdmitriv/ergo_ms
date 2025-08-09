<template>
  <section class="card">
    <header class="card__header">
      <h2 class="card__title">Приглашения</h2>
    </header>

    <div class="card__body">
      <div v-if="loading" class="table-wrap">
        <table class="table table--compact">
          <tbody>
            <tr><td><div class="skeleton skeleton--row"></div></td></tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="invites.length === 0" class="empty">
        <p class="muted">Нет приглашений.</p>
      </div>

      <div v-else class="table-wrap">
        <table class="table table--hover table--compact">
          <thead>
            <tr>
              <th>Организация</th>
              <th class="hide-sm">Роль</th>
              <th class="hide-sm">Отправитель</th>
              <th class="hide-sm">Действует до</th>
              <th class="col-actions">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inv in invites" :key="inv.token">
              <td>{{ inv.organization?.name || '-' }}</td>
              <td class="hide-sm"><span class="badge badge--outline">{{ inv.role }}</span></td>
              <td class="hide-sm">{{ inv.inviter?.full_name || inv.inviter }}</td>
              <td class="hide-sm">
                <span v-if="isExpired(inv)">Истёк</span>
                <span v-else>{{ formatDate(inv.expires_at) }}</span>
              </td>
              <td class="col-actions">
                <button class="btn btn--xs btn--primary" @click="accept(inv.token)" :disabled="acting">
                  Принять
                </button>
                <button class="btn btn--xs btn--ghost" @click="decline(inv.token)" :disabled="acting">
                  Отклонить
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
import { ref, onMounted } from 'vue';
import OrganizationApi from './js/organizationApi.js';

export default {
  name: 'OrganizationInvites',
  setup() {
    const invites = ref([]);
    const loading = ref(false);
    const acting = ref(false);

    const load = async () => {
      loading.value = true;
      try {
        const resp = await OrganizationApi.getInvites();
        invites.value = resp?.data || [];
      } finally {
        loading.value = false;
      }
    };

    const isExpired = (inv) => inv.expires_at && new Date(inv.expires_at) < new Date();
    const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '';

    const accept = async (token) => {
      acting.value = true;
      try {
        await OrganizationApi.acceptInvite(token);
        await load();
      } finally {
        acting.value = false;
      }
    };

    const decline = async (token) => {
      acting.value = true;
      try {
        await OrganizationApi.declineInvite(token);
        await load();
      } finally {
        acting.value = false;
      }
    };

    onMounted(load);
    return { invites, loading, acting, load, accept, decline, formatDate, isExpired };
  }
};
</script>
