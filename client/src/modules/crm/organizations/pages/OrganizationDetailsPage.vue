<template>
  <OrgPageShell>
    <OrganizationDetails />
  </OrgPageShell>
</template>

<script>
import OrgPageShell from '../components/OrgPageShell.vue';
import OrganizationDetails from '../OrganizationDetails.vue';

export default { name: 'OrganizationDetailsPage', components: { OrgPageShell, OrganizationDetails } };
</script>
