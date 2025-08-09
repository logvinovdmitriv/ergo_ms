<template>
  <!-- один .page! и общий локальный scope-класс -->
  <div class="page orgs-scope">
    <header class="page__header">
      <h1 class="page__title">CRM · Организации</h1>
      <p class="muted">Управление организациями и участниками</p>

      <div class="page__actions">
        <router-link class="btn btn--primary" :to="{ name: 'OrganizationNew' }">
          Создать организацию
        </router-link>
      </div>
    </header>

    <!-- используем существующие табы темы, только добавим небольшой отступ в scss -->
    <nav class="tabs tabs--underline orgs-tabs">
      <router-link
        :to="{ name: 'OrganizationList' }"
        class="tabs__link"
        :class="{ 'is-active': $route.name === 'OrganizationList' }"
      >Организации</router-link>

      <router-link
        :to="{ name: 'OrganizationInvites' }"
        class="tabs__link"
        :class="{ 'is-active': $route.name === 'OrganizationInvites' }"
      >Приглашения</router-link>
    </nav>

    <main class="page__content">
      <router-view />
    </main>
  </div>
</template>

<script>
export default { name: 'CRMOrganizationsPage' };
</script>

<style lang="scss">
@import './orgs.scss'; /* не scoped — чтобы стили доходили до детей через .orgs-scope */
</style>
