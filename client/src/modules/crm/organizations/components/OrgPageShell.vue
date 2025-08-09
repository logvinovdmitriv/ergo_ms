<!-- src/modules/crm/organizations/components/OrgPageShell.vue -->
<template>
  <CRMOrganizationsPage>
    <slot />
  </CRMOrganizationsPage>
</template>

<script>
import CRMOrganizationsPage from '../pages/CRMOrganizationsPage.vue';
export default { name: 'OrgPageShell', components: { CRMOrganizationsPage } };
</script>
