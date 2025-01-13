import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, cast

# Определяем корневую директорию проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Путь к директории с данными
DATA_DIR = PROJECT_ROOT / 'data'

# Путь к файлу операций
file_path = DATA_DIR / 'operations.xlsx'

# Путь к директории с логами
LOG_DIR = PROJECT_ROOT / 'logs'
os.makedirs(LOG_DIR, exist_ok=True)  # Создаем директорию для логов, если она не существует

# Файл логов
LOG_FILE = LOG_DIR / 'app.log'

# Настройки логирования
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'filename': LOG_FILE,
}

# Получаем путь к пользовательским настройкам
USER_SETTINGS_FILE = DATA_DIR / 'user_settings.json'


# Функция для загрузки пользовательских настроек
def load_user_settings() -> Optional[Dict[str, Any]]:
    """Загружает пользовательские настройки из файла."""
    try:
        with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return cast(Optional[Dict[str, Any]], json.load(f))
    except FileNotFoundError:
        # Создаем файл с настройками по умолчанию, если он не найден
        default_settings: Dict[str, Any] = {}  # Укажите правильные типы, если известно
        with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f)
        return default_settings
    except json.JSONDecodeError:
        return None
