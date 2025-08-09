<template>
  <OrgPageShell>
    <OrganizationForm />
  </OrgPageShell>
</template>

<script>
import OrgPageShell from '../components/OrgPageShell.vue';
import OrganizationForm from '../OrganizationForm.vue';

export default { name: 'OrganizationNewPage', components: { OrgPageShell, OrganizationForm } };
</script>
