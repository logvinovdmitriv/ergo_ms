import axios from "axios";
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

  // list
  async getOrganizations(params = {}) {
    return await this.client.get('/crm/organizations/', { params })
  }

  async getMyOrganizations(params = {}) {
    return await this.client.get('/crm/organizations/', {
      params: { my: true, page_size: 1000, ...params }
    })
  }
  // details
  async getOrganization(id) { return await this.client.get(`/crm/organizations/${id}/`); }
  // create/update/delete
  async createOrganization(data) { return await this.client.post('/crm/organizations/', data); }
  async updateOrganization(id, data) { return await this.client.patch(`/crm/organizations/${id}/`, data); }
// убедитесь, что этот метод есть (и baseURL = '/api'):
  // create/update/delete
  async deleteOrganization(id) {
    const resp = await this.client.delete(`/crm/organizations/${id}/`);
    return resp?.status ?? 204;
  }


  async archiveOrganization(id) { return await this.client.post(`/crm/organizations/${id}/archive`); }

  // members & projects
  async getOrganizationMembers(id, params = {}) {
    return await this.client.get(`/crm/organizations/${id}/members/`, { params })
  }
  async updateOrganizationMember(orgId, userId, data) { return await this.client.patch(`/crm/organizations/${orgId}/members/${userId}/`, data); }
  async removeOrganizationMember(id, userId) {
    // если на бэке есть отдельная ручка — подставить; иначе временный эндпоинт недоступен
    // здесь показываем пример DELETE на гипотетический /members/{user_id}
    return await this.client.delete(`/crm/organizations/${id}/members/${userId}/`);
  }
  async leaveOrganization(id) {
    return await this.client.post(`/crm/organizations/${id}/leave/`);
  }
  async getProjects(orgId) { return await this.client.get(`/crm/projects/`, { params: { organization: orgId } }); }
  async getTasks(orgId) { return await this.client.get(`/crm/tasks/`, { params: { organization: orgId } }); }
  getAssignableMembers(orgId) {
    return this.client.get(`/crm/organizations/${orgId}/assignable_members/`);
  }

  // invites
  async inviteToOrganization(orgId, data) { return await this.client.post(`/crm/organizations/${orgId}/invite/`, data); }
  async getInvites() { return await this.client.get('/crm/invites/'); }
  async acceptInvite(token) { return await this.client.post('/crm/invites/accept/', { token }); }
  async declineInvite(token) { return await this.client.post('/crm/invites/decline/', { token }); }
}

export default new OrganizationApi();
