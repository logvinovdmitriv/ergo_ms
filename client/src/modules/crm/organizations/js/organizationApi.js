import axios from 'axios';
import Cookies from 'js-cookie';

// Базовый URL API
const API_BASE_URL = `http://${import.meta.env.VITE_API_HOST || 'localhost'}:${import.meta.env.VITE_API_PORT || '8000'}/api`;

/**
 * API для работы с организациями и приглашениями
 */
class OrganizationApi {
    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            headers: { 'Content-Type': 'application/json' }
        });

        // Подставляем токен в каждый запрос
        this.client.interceptors.request.use((config) => {
            const token = Cookies.get('token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            } else {
                console.warn('Токен авторизации не найден!');
            }
            return config;
        }, (error) => Promise.reject(error));
    }

    /**
     * Получить список организаций, в которых пользователь owner или accepted
     */
    async getOrganizations() {
        return await this.client.get('/crm/organizations/');
    }

    /**
     * Создать новую организацию
     * @param {Object} data { name, ... }
     */
    async createOrganization(data) {
        return await this.client.post('/crm/organizations/', data);
    }

    /**
     * Обновить организацию (только owner)
     */
    async updateOrganization(id, data) {
        return await this.client.patch(`/crm/organizations/${id}/`, data);
    }

    /**
     * Архивировать организацию
     */
    async archiveOrganization(id) {
        return await this.client.post(`/crm/organizations/${id}/archive`);
    }

    /**
     * Получить список участников организации
     */
    async getOrganizationMembers(id) {
        return await this.client.get(`/crm/organizations/${id}/members`);
    }

    /**
     * Пригласить пользователя в организацию
     * @param {Number} orgId
     * @param {Object} data { email, role }
     */
    async inviteToOrganization(orgId, data) {
        return await this.client.post(`/crm/organizations/${orgId}/invite/`, data);
    }

    /**
     * Удалить участника (owner/admin)
     */
    async removeOrganizationMember(orgId, userId) {
        return await this.client.delete(`/crm/organizations/${orgId}/members/${userId}`);
    }

    // ==== Приглашения ====

    /** Получить все pending приглашения для текущего пользователя */
    async getInvites() {
        return await this.client.get('/crm/invites/');
    }

    /** Принять приглашение */
    async acceptInvite(token) {
        return await this.client.post('/crm/invites/accept/', { token });
    }

    /** Отклонить приглашение */
    async declineInvite(token) {
        return await this.client.post('/crm/invites/decline/', { token });
    }
}

const organizationApi = new OrganizationApi();
export default organizationApi;
