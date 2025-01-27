import json
import os
from pathlib import Path
from typing import List

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

# Путь к файлу с пользовательскими настройками
user_setting_path = Path(__file__).parent.parent / "user_settings.json"


def load_user_currencies() -> List[str]:
    """Загружает пользовательские валюты из файла user_settings.json."""
    with open(user_setting_path, encoding="utf-8") as file:
        content = json.load(file)
    return [currency for currency in content.get('user_currencies', []) if isinstance(currency, str)]


def load_user_stocks() -> List[str]:
    """Загружает пользовательские акции из файла user_settings.json."""
    with open(user_setting_path, encoding="utf-8") as file:
        content = json.load(file)
    return [stock for stock in content.get('user_stocks', []) if isinstance(stock, str)]
