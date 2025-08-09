<template>
  <OrgPageShell>
    <OrganizationInvites />
  </OrgPageShell>
</template>

<script>
import OrgPageShell from '../components/OrgPageShell.vue';
import OrganizationInvites from '../OrganizationInvites.vue';

export default { name: 'OrganizationInvitesPage', components: { OrgPageShell, OrganizationInvites } };
</script>
