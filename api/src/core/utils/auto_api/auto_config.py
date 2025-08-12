"""
Файл с функциями для автоматизации сборки Django приложений (модулей).
"""

import os
import re
import importlib
import inspect
import logging

from typing import List

from django.apps import AppConfig
from django.urls import (
    include, 
    path
)

# Импорт env делаем лениво внутри функций, чтобы избежать циклических импортов

logger = logging.getLogger('utils')

def discover_installed_apps(apps_dir: str) -> List[str]:
    """
    Рекурсивно обходит директории и находит установленные приложения, включая подмодули.
    Аргументы:
        apps_dir (str): Базовая директория, в которой находятся приложения.
    Возвращает:
        list: Список строк, представляющих пути к установленным приложениям.
    """
    installed_apps = []

    def recursively_find_apps(current_dir: str, base_module: str) -> None:
        """
        Рекурсивно обходит директории и находит установленные приложения, включая подмодули.
        Аргументы:
            current_dir (str): Текущая директория для обхода.
            base_module (str): Базовый модуль для текущей директории.
        """
        for app_name in os.listdir(current_dir):
            app_path = os.path.join(current_dir, app_name)

            # Проверяем, является ли это директорией
            if os.path.isdir(app_path):
                module_path = f'{base_module}.{app_name}' if base_module else app_name

                # Проверяем наличие файла apps.py и просто регистрируем модуль без импорта
                apps_py_path = os.path.join(app_path, 'apps.py')
                if os.path.exists(apps_py_path):
                    installed_apps.append(f'{module_path}')
                    logger.debug(f"Найдено приложение: {module_path}")
                
                # Продолжаем рекурсивный обход независимо от наличия apps.py
                recursively_find_apps(app_path, module_path)

    # Начинаем обход с базовой директории
    base_module = ''
    if apps_dir.endswith('/core'):
        base_module = 'src.core'
    elif apps_dir.endswith('/modules'):
        base_module = 'src.modules'
    recursively_find_apps(apps_dir, base_module)
    
    return installed_apps

def discover_installed_app_urls(apps_dir: str, prefix: str = None) -> List[str]:
    """
    Рекурсивно обходит директории и находит URL-конфигурации для установленных приложений.

    Аргументы:
        apps_dir (str): Базовая директория, в которой находятся приложения.
        prefix (str): Префикс для импорта модулей (например, "src.modules").

    Возвращает:
        list: Список URL-конфигураций для установленных приложений.
    """
    urlpatterns = []

    def recursively_find_urls(current_dir: str, current_prefix: str, current_route: str = "") -> None:
        """
        Рекурсивно обходит директории и находит URL-конфигурации.

        Аргументы:
            current_dir (str): Текущая директория для обхода.
            current_prefix (str): Текущий префикс для импорта модулей.
            current_route (str): Текущий маршрут, учитывающий иерархию модулей.
        """
        for module_name in os.listdir(current_dir):
            module_path = os.path.join(current_dir, module_name)
            if os.path.isdir(module_path):
                # Проверяем, является ли папка Python-пакетом (имеет __init__.py)
                init_py_path = os.path.join(module_path, '__init__.py')
                if os.path.exists(init_py_path):
                    # Формируем полный путь к модулю
                    module_full_path = f"{current_prefix}.{module_name}" if current_prefix else module_name

                    # Формируем маршрут с учетом иерархии
                    new_route = f"{current_route}{module_name}/"

                    # Проверяем наличие файла urls.py
                    urls_py_path = os.path.join(module_path, 'urls.py')
                    if os.path.exists(urls_py_path):
                        # Пытаемся импортировать urls модуля; если не получилось (нет опциональных зависимостей) — пропускаем
                        try:
                            importlib.import_module(f"{module_full_path}.urls")
                            url_pattern = path(new_route, include(f"{module_full_path}.urls"))
                            urlpatterns.append(url_pattern)
                        except Exception as import_error:
                            logger.warning(
                                "Пропуск URL для %s из-за ошибки импорта: %s",
                                module_full_path,
                                str(import_error),
                            )

                    # Рекурсивно обходим подмодули
                    recursively_find_urls(module_path, module_full_path, new_route)

    # Начинаем рекурсивный поиск
    recursively_find_urls(apps_dir, prefix, "")

    return urlpatterns

def check_app_config_name(directory: str, config_name: str) -> bool:
    """
    Проверяет все файлы apps.py в указанной директории на наличие определенного названия конфига.

    Аргументы:
        directory (str): Директория, в которой находятся файлы apps.py.
        config_name (str): Название конфига, которое нужно проверить.

    Возвращает:
        bool: True, если конфиг найден, иначе False.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'apps.py':
                file_path = os.path.join(root, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    searched_class_signature = rf'class\s+{config_name}Config\s*\(AppConfig\):'
                    if re.search(searched_class_signature, content):
                        return True
    return False

def get_env_deploy_type():
    development = 'src.config.patterns.development'
    production = 'src.config.patterns.production'

    try:
        from src.config.env import env  # lazy import to avoid circular deps
        deploy_type = env.str('API_DEPLOY_TYPE', default='development')
    except Exception:
        deploy_type = 'development'

    if deploy_type == 'production':
        return production
    else:
        return development
    
def is_valid_module_name(module_name: str) -> bool:
    """
    Проверяет, соответствует ли имя модуля требованиям:
    - только английские буквы в нижнем регистре
    - допустим символ подчеркивания `_`
    - не должно содержать цифр, других символов или букв в верхнем регистре

    Args:
        module_name (str): Имя модуля для проверки

    Returns:
        bool: True, если имя допустимо, иначе False
    """
    # Регулярное выражение для проверки
    pattern = r'^[a-z_]+$'
    return bool(re.match(pattern, module_name))