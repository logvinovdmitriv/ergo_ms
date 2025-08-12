"""
Файл объединяющий локальные настройки для Django-приложения.

Он автоматически импортирует и объединяет настройки из различных модулей конфигурации в папке settings.
"""

import importlib
from pathlib import Path

# Получаем путь к папке settings
settings_dir = Path(__file__).parent.parent / 'settings'

# Автоматически импортируем все .py файлы из папки settings
for file_path in settings_dir.glob('*.py'):
    if file_path.name != '__init__.py' and not file_path.name.startswith('__'):
        module_name = file_path.stem
        module_path = f'config.settings.{module_name}'
        
        try:
            # Проверяем, что файл существует и не пустой
            if file_path.exists() and file_path.stat().st_size > 0:
                module = importlib.import_module(module_path)
                # Импортируем все из модуля
                globals().update({name: getattr(module, name) for name in dir(module) 
                                if not name.startswith('_')})
        except ImportError as e:
            print(f"Ошибка импорта модуля {module_path}: {e}")
        except Exception as e:
            print(f"Ошибка при загрузке модуля {module_path}: {e}")