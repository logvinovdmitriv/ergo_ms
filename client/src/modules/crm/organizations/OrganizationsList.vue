<template>
  <section class="card">
    <header class="card__header">
      <h2 class="card__title">Организации</h2>
      <div class="toolbar">
        <div class="toolbar__left">
          <input v-model="q" class="input input--sm" placeholder="Поиск по названию…" />
        </div>
        <div class="toolbar__right">
          <button class="btn btn--sm btn--ghost" @click="load" :disabled="loading">Обновить</button>
          <router-link class="btn btn--sm btn--primary" :to="{ name: 'OrganizationNew' }">Создать</router-link>
        </div>
      </div>
    </header>

    <div class="card__body">
      <div v-if="!loading && filtered.length === 0" class="empty">
        <p class="muted">Пока нет организаций.</p>
        <router-link class="btn btn--primary btn--sm" :to="{ name: 'OrganizationNew' }">Создать первую</router-link>
      </div>

      <div v-else class="table-wrap">
        <table class="table table--hover table--compact">
          <thead>
            <tr>
              <th>Название</th>
              <th class="hide-sm">Статус</th>
              <th class="hide-sm">Моя роль</th>
              <th>Участники</th>
              <th class="col-actions">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="5"><div class="skeleton skeleton--row"></div></td>
            </tr>

            <tr v-for="org in filtered" :key="org.id" class="row--clickable" @click="goDetails(org.id)">
              <td>
                <div class="cell-main">
                  <div class="avatar" v-if="org.logo_url"><img :src="org.logo_url" alt="" /></div>
                  <div class="avatar avatar--placeholder" v-else>{{ org.name?.[0] || 'О' }}</div>
                  <div class="cell-main__text">
                    <div class="title">
                      {{ org.name }}
                      <span v-if="isOwner(org)" class="badge badge--outline">владелец</span>
                    </div>
                    <div class="muted slug" v-if="org.slug">@{{ org.slug }}</div>
                  </div>
                </div>
              </td>

              <td class="hide-sm">
                <span class="badge" :class="org.status === 'active' ? 'badge--success' : 'badge--muted'">
                  {{ org.status || 'active' }}
                </span>
              </td>

              <td class="hide-sm"><span class="badge badge--outline">{{ myRole(org) }}</span></td>

              <td><span class="badge badge--neutral">{{ org.members_count ?? org.members?.length ?? 0 }}</span></td>

              <td class="col-actions" @click.stop>
                <button class="btn btn--xs btn--link" title="Открыть" @click="goDetails(org.id)">Открыть</button>
                <button class="btn btn--xs btn--link" title="Пригласить" @click="openInvite(org)">Пригласить</button>
                <button v-if="isOwner(org)" class="btn btn--xs btn--ghost" title="Удалить" @click="removeOrg(org)">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <OrganizationInviteModal
      v-if="showInvite"
      :org="inviteOrg"
      :loading="inviting"
      @close="closeInvite"
      @submit="sendInvite"
    />
  </section>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import OrganizationApi from './js/organizationApi.js'
// Путь ВАЖЕН: файл лежит в organizations/components
import OrganizationInviteModal from './components/OrganizationInviteModal.vue'

export default {
  name: 'OrganizationsList',
  components: { OrganizationInviteModal },
  setup() {
    const store = useStore()
    const router = useRouter()
    const userId = store.state?.auth?.user?.id

    const organizations = ref([])
    const loading = ref(false)
    const q = ref('')

    const showInvite = ref(false)
    const inviteOrg = ref(null)
    const inviting = ref(false)

    const load = async () => {
      loading.value = true
      try {
        const resp = await OrganizationApi.getOrganizations()
        organizations.value = resp?.data?.results || resp?.data || []
      } finally {
        loading.value = false
      }
    }

    const filtered = computed(() => {
      const term = q.value.trim().toLowerCase()
      if (!term) return organizations.value
      return organizations.value.filter(o => (o.name || '').toLowerCase().includes(term))
    })

    const isOwner = (org) => org?.owner?.id === userId
    const myRole = (org) => (isOwner(org) ? 'owner' : (org?.my_role || 'member'))

    const goDetails = (id) => router.push({ name: 'OrganizationDetails', params: { id } })

    const openInvite = (org) => { inviteOrg.value = org; showInvite.value = true }
    const closeInvite = () => { showInvite.value = false; inviteOrg.value = null }
    const sendInvite = async ({ email, role }) => {
      if (!inviteOrg.value) return
      inviting.value = true
      try {
        await OrganizationApi.inviteToOrganization(inviteOrg.value.id, { email, role })
        closeInvite()
      } finally {
        inviting.value = false
      }
    }

    const removeOrg = async (org) => {
      if (!isOwner(org)) return
      if (!confirm(`Удалить организацию «${org.name}»? Действие необратимо.`)) return
      await OrganizationApi.deleteOrganization(org.id)
      await load()
    }

    onMounted(load)

    return {
      // state
      organizations, loading, q, filtered,
      // helpers
      isOwner, myRole, goDetails,
      // invite
      showInvite, inviteOrg, inviting, openInvite, closeInvite, sendInvite,
      // delete
      removeOrg, load
    }
  }
}
</script>
