import json
import os

import pytest

from src.config import USER_SETTINGS_FILE, load_user_settings


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Фикстура для настройки и очистки окружения перед и после тестов."""
    # Удаляем файл пользовательских настроек, если он существует
    if os.path.exists(USER_SETTINGS_FILE):
        os.remove(USER_SETTINGS_FILE)

    yield  # Позволяем тестам выполняться

    # Удаляем файл пользовательских настроек после тестов
    if os.path.exists(USER_SETTINGS_FILE):
        os.remove(USER_SETTINGS_FILE)


def test_load_user_settings_creates_file() -> None:
    """Тест загружает настройки и проверяет, что файл создается при отсутствии."""
    settings = load_user_settings()

    # Проверяем, что файл настроек был создан
    assert os.path.exists(USER_SETTINGS_FILE)
    assert settings == {}  # Проверяем, что настройки по умолчанию пустые


def test_load_user_settings_returns_correct_data() -> None:
    """Тест загружает настройки и проверяет, что они возвращаются корректно."""
    default_settings = {"theme": "dark", "language": "en"}

    # Создаем файл с настройками
    with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(default_settings, f)

    settings = load_user_settings()
    assert settings == default_settings


def test_load_user_settings_handles_file_not_found() -> None:
    """Тест для обработки отсутствия файла с настройками."""
    # Удаляем файл настроек, если он существует
    if os.path.exists(USER_SETTINGS_FILE):
        os.remove(USER_SETTINGS_FILE)

    settings = load_user_settings()

    # Проверяем, что файл настроек был создан
    assert os.path.exists(USER_SETTINGS_FILE)
    assert settings == {}  # Проверяем, что настройки по умолчанию пустые


def test_load_user_settings_handles_json_decode_error() -> None:
    """Тест для обработки ошибок при декодировании JSON."""
    # Создаем файл с некорректным JSON
    with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write("not a json")

    settings = load_user_settings()
    assert settings is None  # Проверяем, что возвращается None
