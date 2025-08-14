import { apiClient } from '@/js/api/manager'

export function getOverview(params?: { category?: number | string }) {
  return apiClient.get('lms/stats/overview/', params)
}
