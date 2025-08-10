<template>
  <OrgPageShell>
    <div class="orgs-scope">
      <nav class="tabs tabs--underline orgs-tabs mb-3">
        <router-link
          :to="`/crm/organizations/${$route.params.id}`"
          class="tabs__link"
          :class="{ 'is-active': !$route.path.includes('/stats') }"
        >Информация</router-link>
        <router-link
          :to="`/crm/organizations/${$route.params.id}/stats`"
          class="tabs__link"
          :class="{ 'is-active': $route.path.includes('/stats') }"
        >Статистика</router-link>
      </nav>

      <OrganizationStats :org-id="$route.params.id" />
    </div>
  </OrgPageShell>
</template>

<script>
import OrgPageShell from '../components/OrgPageShell.vue'
import OrganizationStats from '../components/OrganizationStats.vue'

export default {
  name: 'OrganizationStatsPage',
  components: { OrgPageShell, OrganizationStats },
}
</script>

