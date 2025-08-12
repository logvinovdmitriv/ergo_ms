import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = `http://${import.meta.env.VITE_API_HOST || 'localhost'}:${import.meta.env.VITE_API_PORT || '8000'}/api`;

class OrganizationApi {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: { 'Content-Type': 'application/json' }
    });

    this.client.interceptors.request.use((config) => {
      const token = Cookies.get('token');
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });
  }

  // Организации
  getOrganizations() { return this.client.get('/crm/organizations/'); }
  getOrganization(id) { return this.client.get(`/crm/organizations/${id}/`); }
  createOrganization(data) { return this.client.post('/crm/organizations/', data); }
  updateOrganization(id, data) { return this.client.patch(`/crm/organizations/${id}/`, data); }
  archiveOrganization(id) { return this.client.post(`/crm/organizations/${id}/archive`); }

  // Участники
  getOrganizationMembers(id) { return this.client.get(`/crm/organizations/${id}/members/`); }
  updateOrganizationMember(orgId, userId, data) { return this.client.patch(`/crm/organizations/${orgId}/members/${userId}/`, data); }
  removeOrganizationMember(orgId, userId) { return this.client.delete(`/crm/organizations/${orgId}/members/${userId}/`); }

  // Инвайты (внутри организации)
  inviteToOrganization(orgId, data) { return this.client.post(`/crm/organizations/${orgId}/invite/`, data); }

  // Общий список приглашений пользователя
  getInvites() { return this.client.get('/crm/invites/'); }
  acceptInvite(token) { return this.client.post('/crm/invites/accept/', { token }); }
  declineInvite(token) { return this.client.post('/crm/invites/decline/', { token }); }

  // Проекты (по организации)
  getProjects(orgId) { return this.client.get('/crm/projects/', { params: { organization_id: orgId } }); }

  deleteOrganization(id) { return this.client.delete(`/crm/organizations/${id}/`); }
}

export default new OrganizationApi();
