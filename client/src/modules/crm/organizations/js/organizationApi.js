import axios from 'axios'

export default {
  getOrganizations(params = {}) {
    return axios.get('/api/crm/organizations/', { params })
  },
  getMyOrganizations(params = {}) {
    return axios.get('/api/crm/organizations/', { params: { my: true, page_size: 1000, ...params } })
  },
  getOrganization(id) {
    return axios.get(`/api/crm/organizations/${id}/`)
  },
  createOrganization(data) {
    return axios.post('/api/crm/organizations/', data)
  },
  updateOrganization(id, data) {
    return axios.patch(`/api/crm/organizations/${id}/`, data)
  },
  deleteOrganization(id) {
    return axios.delete(`/api/crm/organizations/${id}/`)
  },
  archiveOrganization(id) {
    return axios.post(`/api/crm/organizations/${id}/archive`)
  },
  getOrganizationMembers(id, params = {}) {
    return axios.get(`/api/crm/organizations/${id}/members/`, { params })
  },
  removeOrganizationMember(id, userId) {
    return axios.delete(`/api/crm/organizations/${id}/members/${userId}/`)
  },
  leaveOrganization(id) {
    return axios.post(`/api/crm/organizations/${id}/leave/`)
  },
  getOrganizationProjects(id, params = {}) {
    return axios.get('/api/crm/projects/', { params: { organization: id, ...params } })
  },
  getOrganizationTasks(id, params = {}) {
    return axios.get('/api/crm/tasks/', { params: { organization: id, ...params } })
  },
  updateMemberRole(orgId, memberId, role) {
    return axios.post(`/api/crm/organizations/${orgId}/members/${memberId}/update-role/`, { role })
  },
  getAssignableMembers(orgId) {
    return axios.get(`/api/crm/organizations/${orgId}/assignable_members/`)
  },
  inviteToOrganization(orgId, data) {
    return axios.post(`/api/crm/organizations/${orgId}/invite/`, data)
  },
  getInvites() {
    return axios.get('/api/crm/invites/')
  },
  acceptInvite(token) {
    return axios.post('/api/crm/invites/accept/', { token })
  },
  declineInvite(token) {
    return axios.post('/api/crm/invites/decline/', { token })
  }
}
