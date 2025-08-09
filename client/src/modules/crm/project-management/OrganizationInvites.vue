<template>
  <div class="org-invites">
    <h2>Приглашения</h2>
    <ul>
      <li v-for="invite in invites" :key="invite.id">
        {{ invite.organization?.name || invite.organization }}
        <span v-if="invite.role">({{ invite.role }})</span>
        <button @click="accept(invite.token)">Принять</button>
        <button @click="decline(invite.token)">Отклонить</button>
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import ProjectManagementApi from './js/projectManagementApi';

export default {
  name: 'OrganizationInvites',
  setup() {
    const invites = ref([]);

    const load = async () => {
      const resp = await ProjectManagementApi.getInvites();
      invites.value = resp.data;
    };

    const accept = async (token) => {
      await ProjectManagementApi.acceptInvite(token);
      await load();
    };

    const decline = async (token) => {
      await ProjectManagementApi.declineInvite(token);
      await load();
    };

    onMounted(load);

    return { invites, accept, decline };
  }
};
</script>

<style scoped>
.org-invites ul {
  list-style: none;
  padding: 0;
}
.org-invites li {
  margin-bottom: 8px;
}
</style>
