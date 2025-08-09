<template>
  <div class="page orgs-scope">
    <header class="page__header">
      <div>
        <h1 class="page__title">Организации</h1>
      </div>
    </header>

    <nav class="tabs tabs--underline orgs-tabs">
      <router-link
        to="/crm/organizations/list"
        class="tabs__link"
        :class="{ 'is-active': $route.path.startsWith('/crm/organizations') && !$route.path.startsWith('/crm/invites') }"
      >Организации</router-link>

      <router-link
        to="/crm/invites"
        class="tabs__link"
        :class="{ 'is-active': $route.path.startsWith('/crm/invites') }"
      >Приглашения</router-link>
    </nav>

    <main class="page__content">
      <slot />
    </main>
  </div>
</template>

<script>
export default { name: 'CRMOrganizationsPage' };
</script>

<style lang="scss">
@import '../orgs.scss';
.link { text-decoration: none; }
.mt-1 { margin-top: 4px; }
.inline-block { display: inline-block; }
</style>
