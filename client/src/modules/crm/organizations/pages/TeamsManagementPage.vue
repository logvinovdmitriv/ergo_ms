<template>
  <OrgPageShell>
    <div class="card p-3">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="mb-0 d-flex align-items-center gap-2"><i class="fas fa-users"></i> Команды организаций</h5>
        <button class="btn btn-primary" @click="openCreateTeam"><i class="fas fa-plus me-1"></i>Создать команду</button>
      </div>
      <div class="row g-2 mb-3">
        <div class="col-md-4">
          <label class="form-label">Поиск</label>
          <input class="form-control" v-model="search" placeholder="Название/описание" @input="loadTeams" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Организация</label>
          <select class="form-select" v-model="orgFilter" @change="loadTeams">
            <option value="">Все</option>
            <option v-for="o in organizations" :key="o.id" :value="o.id">{{ o.name }}</option>
          </select>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Команда</th>
              <th>Организация</th>
              <th>Участники</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in teams" :key="t.id">
              <td>{{ t.name }}</td>
              <td>{{ t.organization?.name || '-' }}</td>
              <td><span class="badge bg-light text-dark">{{ t.members_count || (t.memberships?.length || 0) }}</span></td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary me-2" @click="openMembers(t)">Участники</button>
                <button class="btn btn-sm btn-outline-secondary me-2" @click="openEditTeam(t)">Редактировать</button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteTeam(t)">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Модалка команды -->
    <div class="modal fade" id="teamEditModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title d-flex align-items-center gap-2"><i class="fas fa-users"></i>{{ editingTeam?.id ? 'Редактировать команду' : 'Создать команду' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Название</label>
              <input class="form-control" v-model="teamForm.name" placeholder="Например, Команда продаж" />
            </div>
            <div class="mb-3">
              <label class="form-label">Организация</label>
              <select class="form-select" v-model="teamForm.organization_id" @change="loadOrgMembers(teamForm.organization_id); teamForm.manager_id = ''">
                <option value="">Выберите</option>
                <option v-for="o in organizations" :key="o.id" :value="o.id">{{ o.name }}</option>
              </select>
            </div>
            <div class="mb-3" v-if="teamForm.organization_id">
              <label class="form-label">Менеджер команды (опционально)</label>
              <select class="form-select" v-model="teamForm.manager_id" :disabled="loadingOrgMembers || orgMembersForManager.length === 0">
                <option value="">Не выбран</option>
                <option v-for="m in orgMembersForManager" :key="m.id || m.user?.id" :value="m.user?.id || m.id">
                  {{ (m.user?.full_name || m.user?.username || m.user?.email || m.full_name || m.username) }}
                </option>
              </select>
              <small class="text-muted" v-if="!loadingOrgMembers && orgMembersForManager.length === 0">В организации пока нет участников</small>
            </div>
            <div class="mb-3">
              <label class="form-label">Описание</label>
              <textarea class="form-control" rows="3" v-model="teamForm.description" placeholder="Кратко опишите цели команды"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-light" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" :disabled="!teamForm.name || !teamForm.organization_id" @click="submitTeam">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка участников -->
    <div class="modal fade" id="teamMembersModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title d-flex align-items-center gap-2">
              <i class="fas fa-user-friends"></i>
              Участники команды: {{ editingTeam?.name }}
              <span v-if="teamMembers?.length" class="ms-2 badge bg-light text-dark">{{ teamMembers.length }}</span>
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-2 d-flex gap-2">
              <input class="form-control" v-model="userQuery" placeholder="Поиск по логину/ФИО" @keyup.enter="searchUsers" />
              <button class="btn btn-outline-primary" @click="searchUsers"><i class="fas fa-search me-1"></i>Найти</button>
            </div>
            <div v-if="userResults.length" class="border rounded p-2" style="max-height: 240px; overflow:auto;">
              <div class="d-flex justify-content-between align-items-center py-1" v-for="u in userResults" :key="`u-${u.id}`">
                <span>{{ u.full_name || `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.username }}</span>
                <button class="btn btn-sm btn-primary" @click="addMemberToTeam(u)">Добавить</button>
              </div>
            </div>
            <hr />
            <div v-if="teamMembers.length">
              <div class="d-flex justify-content-between align-items-center py-1" v-for="m in teamMembers" :key="`m-${m.id}`">
                <span>{{ m.user?.full_name || m.user?.username }}</span>
                <button class="btn btn-sm btn-outline-danger" @click="removeMemberFromTeam(m.user)">Исключить</button>
              </div>
            </div>
            <div v-else class="text-muted">Пока нет участников</div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-light" data-bs-dismiss="modal">Закрыть</button>
          </div>
        </div>
      </div>
    </div>
  </OrgPageShell>
</template>

<script>
import { Modal } from 'bootstrap'
import OrgPageShell from '../components/OrgPageShell.vue'
import OrganizationApi from '../js/organizationApi.js'
import projectManagementApi from '@/modules/crm/project-management/js/projectManagementApi.js'
import { useToast } from 'vue-toastification'

export default {
  name: 'TeamsManagementPage',
  components: { OrgPageShell },
  data() {
    return {
      teams: [],
      organizations: [],
      orgFilter: '',
      search: '',
      editingTeam: null,
      teamForm: { name: '', description: '', organization_id: '', manager_id: '' },
      teamMembers: [],
      userQuery: '',
      userResults: [],
      orgMembersForManager: [],
      loadingOrgMembers: false
    }
  },
  async mounted() {
    await Promise.all([this.loadTeams(), this.loadOrganizations()])
  },
  methods: {
    async loadTeams() {
      const params = {}
      if (this.search) params.search = this.search
      const res = await projectManagementApi.getTeams(params)
      const list = res.data.results || res.data || []
      this.teams = this.orgFilter ? list.filter(t => t.organization?.id === Number(this.orgFilter)) : list
    },
    async loadOrganizations() {
      const res = await OrganizationApi.getOrganizations()
      this.organizations = res.data.results || res.data || []
    },
    openCreateTeam() {
      this.editingTeam = null
      this.teamForm = { name: '', description: '', organization_id: '', manager_id: '' }
      this.orgMembersForManager = []
      new Modal(document.getElementById('teamEditModal')).show()
    },
    openEditTeam(team) {
      this.editingTeam = team
      this.teamForm = { name: team.name, description: team.description, organization_id: team.organization?.id, manager_id: team.manager?.id || '' }
      this.loadOrgMembers(this.teamForm.organization_id)
      new Modal(document.getElementById('teamEditModal')).show()
    },
    async submitTeam() {
      // Клиентская проверка дублей имён внутри организации (нормализовано)
      try {
        const toast = useToast()
        const name = (this.teamForm.name || '').trim()
        const orgId = this.teamForm.organization_id
        if (!name || !orgId) return
        const res = await projectManagementApi.getTeams({ organization_id: orgId, page_size: 1000 })
        const list = res.data.results || res.data || []
        const norm = (s) => (s || '').toString().trim().replace(/\s+/g, ' ').toLowerCase()
        const exists = list.some(t => norm(t.name) === norm(name) && (!this.editingTeam || t.id !== this.editingTeam.id))
        if (exists) {
          toast.error('Команда с таким названием уже существует в этой организации')
          return
        }
      } catch (_) {}

      const payload = { ...this.teamForm }
      if (this.editingTeam?.id) {
        await projectManagementApi.updateTeam(this.editingTeam.id, payload)
      } else {
        await projectManagementApi.createTeam(payload)
      }
      new Modal(document.getElementById('teamEditModal')).hide()
      await this.loadTeams()
    },
    async loadOrgMembers(orgId) {
      this.loadingOrgMembers = true
      try {
        if (!orgId) { this.orgMembersForManager = []; return }
        const res = await OrganizationApi.getOrganizationMembers(orgId)
        const members = res.data || []
        this.orgMembersForManager = members
      } catch (e) {
        this.orgMembersForManager = []
      } finally {
        this.loadingOrgMembers = false
      }
    },
    async deleteTeam(team) {
      await projectManagementApi.deleteTeam(team.id)
      await this.loadTeams()
    },
    async openMembers(team) {
      // Подгружаем актуальные данные команды с сервера, чтобы подтянуть участников и счетчики
      try {
        const res = await projectManagementApi.getTeam(team.id)
        this.editingTeam = res.data || team
        this.teamMembers = (this.editingTeam.memberships || []).map(m => m)
      } catch {
        this.editingTeam = team
        this.teamMembers = (team.memberships || []).map(m => m)
      }
      new Modal(document.getElementById('teamMembersModal')).show()
    },
    async searchUsers() {
      const q = (this.userQuery || '').trim()
      if (!q) { this.userResults = []; return }
      const res = await projectManagementApi.getUsers({ search: q })
      this.userResults = res.data.results || res.data || []
    },
    async addMemberToTeam(u) {
      if (!this.editingTeam?.id) return
      await projectManagementApi.addTeamMember(this.editingTeam.id, { user_id: u.id, role: 'member' })
      await this.loadTeams()
      await this.openMembers(this.teams.find(t => t.id === this.editingTeam.id) || this.editingTeam)
      // Сообщаем странице организации об изменениях для автообновления
      try {
        const orgId = this.editingTeam?.organization?.id
        if (orgId) {
          window.dispatchEvent(new CustomEvent('organization-data-refresh', { detail: { organizationId: orgId } }))
        }
      } catch (_) {}
    },
    async removeMemberFromTeam(u) {
      if (!this.editingTeam?.id) return
      await projectManagementApi.removeTeamMember(this.editingTeam.id, u.id)
      await this.loadTeams()
      await this.openMembers(this.teams.find(t => t.id === this.editingTeam.id) || this.editingTeam)
      // Сообщаем странице организации об изменениях для автообновления
      try {
        const orgId = this.editingTeam?.organization?.id
        if (orgId) {
          window.dispatchEvent(new CustomEvent('organization-data-refresh', { detail: { organizationId: orgId } }))
        }
      } catch (_) {}
    }
  }
}
</script>

<style scoped>

</style>

