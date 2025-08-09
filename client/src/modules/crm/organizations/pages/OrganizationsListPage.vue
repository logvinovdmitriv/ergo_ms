<template>
  <OrgPageShell>
    <!-- ВАЖНО: используем то же имя, что импортируем -->
    <OrganizationsList />
  </OrgPageShell>
</template>

<script>
import OrgPageShell from '../components/OrgPageShell.vue'

// Если файл реально называется "OrganizationsList.vue" (как у тебя в репо) —
import OrganizationsList from '../OrganizationsList.vue'

// Если у тебя файл всё же называется "OrganizationList.vue",
// смени строку выше на:
// import OrganizationsList from '../OrganizationList.vue'

export default {
  name: 'OrganizationListPage',
  components: { OrgPageShell, OrganizationsList }
}
</script>
