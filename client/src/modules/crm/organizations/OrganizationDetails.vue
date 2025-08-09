<template>
  <section class="card">
    <header class="card__header">
      <h2 class="card__title">{{ org.name || 'Организация' }}</h2>
      <div class="muted" v-if="org.slug">@{{ org.slug }}</div>
    </header>

    <div class="card__body">
      <div v-if="loading"><div class="skeleton skeleton--row"></div></div>
      <div v-else class="org-details">
        <div class="org-details__info">
          <p v-if="org.description" class="org-details__description">{{ org.description }}</p>
          <ul class="org-details__meta">
            <li v-if="org.website">
              <label>Сайт</label>
              <a :href="org.website" target="_blank" rel="noopener">{{ org.website }}</a>
            </li>
            <li v-if="org.email">
              <label>Email</label>
              <a :href="`mailto:${org.email}`">{{ org.email }}</a>
            </li>
            <li v-if="org.phone">
              <label>Телефон</label>
              <span>{{ org.phone }}</span>
            </li>
            <li v-if="org.address">
              <label>Адрес</label>
              <span>{{ org.address }}</span>
            </li>
          </ul>
        </div>

        <div class="org-details__members">
          <h3>Участники</h3>
          <div class="table-wrap">
            <table class="table table--compact">
              <thead>
                <tr>
                  <th>Имя</th>
                  <th class="hide-sm">Роль</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in members" :key="m.id">
                  <td>{{ m.user?.full_name || m.user }}</td>
                  <td class="hide-sm">
                    <span class="badge badge--outline">{{ m.role || 'member' }}</span>
                  </td>
                </tr>
                <tr v-if="members.length === 0">
                  <td colspan="2"><span class="muted">Нет участников</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import OrganizationApi from './js/organizationApi.js';

export default {
  name: 'OrganizationDetails',
  setup() {
    const route = useRoute();
    const org = ref({});
    const members = ref([]);
    const loading = ref(false);

    const load = async () => {
      loading.value = true;
      try {
        const id = route.params.id;
        const [orgResp, membersResp] = await Promise.all([
          OrganizationApi.getOrganization(id),
          OrganizationApi.getOrganizationMembers(id)
        ]);
        org.value = orgResp?.data || {};
        members.value = membersResp?.data || [];
      } finally {
        loading.value = false;
      }
    };

    onMounted(load);
    return { org, members, loading };
  }
};
</script>


