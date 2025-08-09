<template>
  <!-- общий CRM layout -->
  <CRMParentLayout>
    <!-- шапка раздела + табы -->
    <CRMOrganizationsPage>
      <!-- сюда упадет контент конкретной страницы (список/инвайты/форма/детали) -->
      <slot />
    </CRMOrganizationsPage>
  </CRMParentLayout>
</template>

<script>
import CRMParentLayout from '@/modules/crm/ParentLayout.vue';
import CRMOrganizationsPage from '../pages/CRMOrganizationsPage.vue';

export default {
  name: 'OrgPageShell',
  components: { CRMParentLayout, CRMOrganizationsPage }
};
</script>

