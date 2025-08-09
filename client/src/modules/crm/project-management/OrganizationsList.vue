<template>
  <div class="organizations-list">
    <h2>Организации</h2>
    <form @submit.prevent="createOrganization" class="mb-3">
      <input v-model="newOrg" placeholder="Название организации" />
      <button type="submit">Создать</button>
    </form>
    <ul>
      <li v-for="org in organizations" :key="org.id">
        {{ org.name }}
        <span v-if="org.owner && org.owner.id === userId">(владелец)</span>
        <button v-if="requiresAcceptance(org)" @click="accept(org.id)">Присоединиться</button>
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import ProjectManagementApi from './js/projectManagementApi';

export default {
  name: 'OrganizationsList',
  setup() {
    const store = useStore();
    const organizations = ref([]);
    const newOrg = ref('');
    const userId = store.state?.auth?.user?.id;

    const load = async () => {
      const resp = await ProjectManagementApi.getOrganizations();
      organizations.value = resp.data.results || resp.data;
    };

    const createOrganization = async () => {
      if (!newOrg.value) return;
      await ProjectManagementApi.createOrganization({ name: newOrg.value });
      newOrg.value = '';
      await load();
    };

    const accept = async (id) => {
      await ProjectManagementApi.acceptOrganization(id);
      await load();
    };

    const requiresAcceptance = (org) => {
      const membership = org.memberships.find(m => m.user.id === userId);
      return membership && !membership.is_accepted;
    };

    onMounted(load);

    return { organizations, newOrg, createOrganization, accept, requiresAcceptance, userId };
  }
};
</script>

<style scoped>
.organizations-list input {
  margin-right: 8px;
}
</style>

