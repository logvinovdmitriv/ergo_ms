"""
Файл для определения маршрутов URL для Django-API-приложения.

Он использует функцию `path` из `django.urls` для определения маршрутов и функцию `include`
для включения URL-конфигураций из других модулей. Также используется функция
`discover_installed_app_urls` для автоматического обнаружения и включения URL-конфигураций
из модулей, находящихся в директории `MODULES_DIR`.
"""

from django.urls import path, include

from src.core.utils.auto_api.auto_config import discover_installed_app_urls
from src.config.settings.apps import CORE_DIR, MODULES_DIR

urlpatterns = []

# Явно подключаем CRM-модуль, чтобы гарантировать доступность /api/crm/*
urlpatterns += [
    path('crm/', include('src.modules.crm.urls')),
]

core_urlpatterns = discover_installed_app_urls(CORE_DIR, prefix='src.core')
urlpatterns += core_urlpatterns

# Добавляем URL-конфигурации модулей, автоматически 
# обнаруженные в директории MODULES_DIR
modules_urlpatterns = discover_installed_app_urls(MODULES_DIR, prefix='src.modules')
urlpatterns += modules_urlpatterns