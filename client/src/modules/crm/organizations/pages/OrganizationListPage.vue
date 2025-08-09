<template>
  <OrgPageShell>
    <div class="orgs-scope">
      <OrganizationsList />
    </div>
  </OrgPageShell>
</template>

<script>
import OrgPageShell from '../components/OrgPageShell.vue'
import OrganizationsList from '../OrganizationsList.vue'

export default {
  name: 'OrganizationListPage',
  components: { OrgPageShell, OrganizationsList }
}
</script>
