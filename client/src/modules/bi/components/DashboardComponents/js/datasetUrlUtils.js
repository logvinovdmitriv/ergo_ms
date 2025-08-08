/**
 * Утилиты для работы с URL датасетов
 */

/**
 * Проверяет корректность URL датасета и доступ к нему
 * @param {string} url - URL датасета для проверки
 * @param {Object} apiClient - Клиент для API запросов
 * @param {boolean} silentMode - Отключить логирование ошибок (по умолчанию true)
 * @returns {Promise<Object>} Результат валидации
 */
export async function validateDatasetUrlWithAccess(url, apiClient, silentMode = true) {
  try {
    // Проверяем формат URL
    const urlPattern = /^https?:\/\/[^\/]+\/bi\/dataset\/(\d+)\/?$/;
    const match = url.match(urlPattern);
    
    if (!match) {
      return {
        isValid: false,
        error: 'Неверный формат URL. Ожидается: http://host/bi/dataset/ID/',
        datasetId: null
      };
    }
    
    const datasetId = parseInt(match[1]);
    
    if (!datasetId || datasetId <= 0) {
      return {
        isValid: false,
        error: 'Неверный ID датасета',
        datasetId: null
      };
    }

    // Проверяем доступность датасета через API
    try {
      const response = await apiClient.get(`bi_analysis/bi_datasets/${datasetId}/`);
      
      if (response.success && response.data) {
        return {
          isValid: true,
          error: null,
          datasetId: datasetId,
          datasetName: response.data.name || response.data.title || `Датасет ${datasetId}`
        };
      } else {
        return {
          isValid: false,
          error: 'Датасет не найден или доступ запрещен',
          datasetId: null
        };
      }
    } catch (apiError) {
      // Логируем только неожиданные ошибки (не 404, 403) и только если не в тихом режиме
      const status = apiError.response?.status;
      if (!silentMode && status && status !== 404 && status !== 403) {
        console.error('Ошибка при проверке доступа к датасету:', apiError);
      }
      
      if (status === 404) {
        return {
          isValid: false,
          error: 'Датасет не найден',
          datasetId: null
        };
      } else if (status === 403) {
        return {
          isValid: false,
          error: 'Доступ к датасету запрещен',
          datasetId: null
        };
      } else if (status === 500) {
        return {
          isValid: false,
          error: 'Ошибка сервера при обработке запроса',
          datasetId: null
        };
      } else {
        return {
          isValid: false,
          error: 'Не удалось проверить доступ к датасету',
          datasetId: null
        };
      }
    }
    
  } catch (error) {
    // Логируем только если не в тихом режиме
    if (!silentMode) {
      console.error('Ошибка при валидации URL датасета:', error);
    }
    return {
      isValid: false,
      error: 'Произошла ошибка при проверке URL',
      datasetId: null
    };
  }
}

/**
 * Извлекает ID датасета из URL
 * @param {string} url - URL датасета
 * @returns {number|null} ID датасета или null если URL неверный
 */
export function extractDatasetIdFromUrl(url) {
  const urlPattern = /\/bi\/dataset\/(\d+)\/?$/;
  const match = url.match(urlPattern);
  return match ? parseInt(match[1]) : null;
}

/**
 * Формирует URL датасета по ID
 * @param {number} datasetId - ID датасета
 * @param {string} baseUrl - Базовый URL (по умолчанию текущий хост)
 * @returns {string} Полный URL датасета
 */
export function buildDatasetUrl(datasetId, baseUrl = window.location.origin) {
  return `${baseUrl}/bi/dataset/${datasetId}/`;
}