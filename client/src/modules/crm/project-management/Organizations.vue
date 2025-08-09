<template>
  <div class="organizations-page">
    <div class="tabs mb-3">
      <button @click="active = 'list'" :class="{ active: active === 'list' }">Организации</button>
      <button @click="active = 'invites'" :class="{ active: active === 'invites' }">Приглашения</button>
    </div>
    <OrganizationsList v-if="active === 'list'" />
    <OrganizationInvites v-else />
  </div>
</template>

<script>
import { ref } from 'vue';
import OrganizationsList from './OrganizationsList.vue';
import OrganizationInvites from './OrganizationInvites.vue';

export default {
  name: 'Organizations',
  components: { OrganizationsList, OrganizationInvites },
  setup() {
    const active = ref('list');
    return { active };
  }
};
</script>

<style scoped>
.tabs button {
  margin-right: 8px;
}
.tabs button.active {
  font-weight: bold;
}
</style>

