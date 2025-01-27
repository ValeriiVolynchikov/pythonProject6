import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.config import load_user_currencies, load_user_stocks, user_setting_path

# Тестовые данные
mock_user_settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}


def test_load_user_currencies() -> None:
    """Тестирование функции загрузки пользовательских валют."""
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_user_settings))):
        currencies = load_user_currencies()
        assert currencies == mock_user_settings["user_currencies"], "Должны получить корректный список валют"


def test_load_user_stocks() -> None:
    """Тестирование функции загрузки пользовательских акций."""
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_user_settings))):
        stocks = load_user_stocks()
        assert stocks == mock_user_settings["user_stocks"], "Должны получить корректный список акций"


def test_user_setting_path() -> None:
    """Проверка корректности пути к файлу с пользовательскими настройками."""
    assert user_setting_path.is_file(), "Путь к файлу user_settings.json должен существовать"


def test_data_directory() -> None:
    """Проверка корректности пути к директории с данными."""
    data_dir = Path(__file__).resolve().parent.parent / "data"
    assert data_dir.is_dir(), "Директория данных должна существовать"


def test_log_directory() -> None:
    """Проверка создания директории для логов."""
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    assert log_dir.is_dir(), "Директория логов должна существовать"


if __name__ == "__main__":
    pytest.main()
