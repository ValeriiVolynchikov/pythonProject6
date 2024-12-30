# # src/config.py
# import os
# from pathlib import Path
# import json
#
# # Определяем корневую директорию проекта
# PROJECT_ROOT = Path(__file__).resolve().parent.parent
#
# # Пример определения ROOT_PATH
# #ROOT_PATH = 'C:\\Users\\avto1\\PycharmProjects\\pythonProject6\\'
#
# # Пример использования os.path.join
# #file_path = os.path.join(ROOT_PATH, 'data', 'operations.xlsx')
#
# file_path = "\\data\\operations.xlsx"
#
# # Путь к директории с данными
# #DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
# #DATA_DIR = PROJECT_ROOT / 'data'
#
# # Путь к директории с логами
# LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
# os.makedirs(LOG_DIR, exist_ok=True)  # Создаем директорию для логов, если она не существует
#
# # Файл логов
# LOG_FILE = os.path.join(LOG_DIR, 'app.log')
#
#
# # Настройки логирования
# LOGGING_CONFIG = {
#     'level': 'INFO',
#     'format': '%(asctime)s - %(levelname)s - %(message)s',
#     'filename': LOG_FILE,
# }
#
# # Получаем путь к пользовательским настройкам
# USER_SETTINGS_FILE = PROJECT_ROOT / 'data' / 'user_settings.json'
#
# # Функция для загрузки пользовательских настроек
# def load_user_settings():
#     with open(USER_SETTINGS_FILE) as f:
#         return json.load(f)
#
# # Получаем путь к базовой директории проекта
# #
# # BASE_DIR = Path(__file__).resolve().parent.parent # Это указывает на директорию project/
# # DATA_DIR = BASE_DIR / 'data'
# src/config.py
import os
from pathlib import Path
import json

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
def load_user_settings():
    with open(USER_SETTINGS_FILE) as f:
        return json.load(f)

