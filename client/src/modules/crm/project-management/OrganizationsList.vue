<template>
  <div class="organizations-list">
    <h2>Организации</h2>
    <form @submit.prevent="createOrganization" class="mb-3">
      <input v-model="newOrg" placeholder="Название организации" />
      <button type="submit">Создать</button>
    </form>
    <ul>
      <li v-for="org in organizations" :key="org.id">
        <div v-if="editingId === org.id">
          <input v-model="editName" />
          <button @click="saveEdit(org.id)">Сохранить</button>
          <button @click="cancelEdit">Отмена</button>
        </div>
        <div v-else>
          {{ org.name }}
          <span v-if="org.owner && org.owner.id === userId">(владелец)</span>
          <button v-if="org.owner && org.owner.id === userId" @click="startEdit(org)">Редактировать</button>
        </div>
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
    const editingId = ref(null);
    const editName = ref('');

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

    const startEdit = (org) => {
      editingId.value = org.id;
      editName.value = org.name;
    };

    const cancelEdit = () => {
      editingId.value = null;
    };

    const saveEdit = async (orgId) => {
      await ProjectManagementApi.updateOrganization(orgId, { name: editName.value });
      editingId.value = null;
      await load();
    };

    onMounted(load);

    return { organizations, newOrg, createOrganization, userId, editingId, editName, startEdit, cancelEdit, saveEdit };
  }
};
</script>

<style scoped>
.organizations-list input {
  margin-right: 8px;
}
</style>

