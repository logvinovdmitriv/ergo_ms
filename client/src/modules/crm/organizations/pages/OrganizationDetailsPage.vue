<template>
  <OrgPageShell>
    <div class="orgs-scope">
      <OrganizationDetails />
    </div>
  </OrgPageShell>
</template>

<script>
import OrgPageShell from '../components/OrgPageShell.vue'
import OrganizationDetails from '../OrganizationDetails.vue'

export default {
  name: 'OrganizationDetailsPage',
  components: { OrgPageShell, OrganizationDetails }
}
</script>
