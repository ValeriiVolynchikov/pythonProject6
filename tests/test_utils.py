import datetime
import json
from pathlib import Path
from typing import Any, Dict, List
from unittest import mock

import pandas as pd
import pytest

from src.utils import (get_currency_rates, get_data, get_dict_transaction, get_stock_price, get_user_setting,
                       reader_transaction_excel)

ROOT_PATH = Path(__file__).resolve().parent.parent


def test_get_data_input() -> None:
    """Проверяем, что функция корректно обрабатывает ввод"""
    input_data: str = "01.01.2023 12:00:00"
    expected_output: datetime.datetime = datetime.datetime(2023, 1, 1, 12, 0, 0)
    assert get_data(input_data) == expected_output


def test_get_data_format() -> None:
    """Проверяем, что функция обрабатывает исключение при неверном формате ввода"""
    input_data: str = "01-01-2023 12:00:00"
    with pytest.raises(ValueError):
        get_data(input_data)


def test_get_data_empty_input() -> None:
    """Проверяем, что функция обрабатывает пустой ввод"""
    input_data: str = ""
    with pytest.raises(ValueError):
        get_data(input_data)


def test_reader_excel_file_not_found() -> None:
    """Проверка, что функция поднимает исключение при передаче несуществующего файла"""
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        reader_transaction_excel("path/to/non-existent/file.xlsx")


def test_reader_transaction_excel_success(monkeypatch: mock.MagicMock) -> None:
    """Тестируем успешное чтение Excel файла"""
    mock_df: pd.DataFrame = pd.DataFrame({"transaction_id": [1, 2, 3]})
    with mock.patch("pandas.read_excel", return_value=mock_df):
        result: pd.DataFrame = reader_transaction_excel("test_file.xlsx")
        assert result.shape == mock_df.shape
        assert all(result["transaction_id"] == mock_df["transaction_id"])


def test_get_dict_transaction_file_not_found() -> None:
    """Тест проверяет обработку ошибки FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        get_dict_transaction("non_existent_file.xlsx")


def test_get_user_setting_success(monkeypatch: mock.MagicMock) -> None:
    """Тестируем успешное получение настроек пользователя"""
    mock_data: str = '{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}'
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_data)):
        user_settings: tuple = get_user_setting("dummy_path.json")
        user_currencies: List[str] = user_settings[0]  # Исправлено
        user_stocks: List[str] = user_settings[1]      # Исправлено
        assert user_currencies == ["USD", "EUR"]
        assert user_stocks == ["AAPL", "AMZN"]


def test_get_user_setting_empty(monkeypatch: mock.MagicMock) -> None:
    """Тестируем получение пустых настроек пользователя"""
    mock_data: str = '{"user_currencies": [], "user_stocks": []}'
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_data)):
        user_settings: tuple = get_user_setting("dummy_path.json")
        user_currencies: List[str] = user_settings[0]  # Исправлено
        user_stocks: List[str] = user_settings[1]      # Исправлено
        assert user_currencies == []
        assert user_stocks == []


def test_get_user_setting_file_not_found(monkeypatch: mock.MagicMock) -> None:
    """Тестируем обработку ошибки FileNotFoundError"""
    with mock.patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            get_user_setting("dummy_path.json")


def test_get_currency_rates_success(monkeypatch: mock.MagicMock) -> None:
    """Тестируем успешное получение курсов валют"""
    mock_response: mock.Mock = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"quotes": {"USDRUB": 73.97, "USDEUR": 0.84}}
    with mock.patch("src.utils.requests.get", return_value=mock_response):
        currencies: List[str] = ["RUB", "EUR"]
        result: List[Dict[str, Any]] = get_currency_rates(currencies)
        expected_result: List[Dict[str, Any]] = [
            {"currency": "USD", "rate": 73.97},
            {"currency": "EUR", "rate": round(73.97 / 0.84, 2)},
        ]
        assert result == expected_result


def test_get_currency_rates_failure(monkeypatch: mock.MagicMock) -> None:
    """Тестируем обработку ошибки при получении курсов валют"""
    mock_response: mock.Mock = mock.Mock()
    mock_response.status_code = 500
    mock_response.reason = "Internal Server Error"
    with mock.patch("src.utils.requests.get", return_value=mock_response):
        currencies: List[str] = ["RUB", "EUR"]
        result: Any = get_currency_rates(currencies)
        assert result is None


def test_get_user_setting_invalid_json(monkeypatch: mock.MagicMock) -> None:
    """Тестируем случай с некорректным JSON в файле настроек"""
    mock_data: str = '{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]'  # некорректный JSON
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_data)):
        with pytest.raises(json.JSONDecodeError):
            get_user_setting("dummy_path.json")


def test_get_currency_rates_empty_response(monkeypatch: mock.MagicMock) -> None:
    """Тестируем случай, когда API возвращает пустые данные"""
    mock_response: mock.Mock = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"quotes": {}}
    with mock.patch("src.utils.requests.get", return_value=mock_response):
        currencies: List[str] = ["RUB", "EUR"]
        result: List[Dict[str, Any]] = get_currency_rates(currencies)
        assert result == []  # или другое ожидаемое значение


def test_get_stock_price_success(monkeypatch: mock.MagicMock) -> None:
    """Тестируем успешное получение цены акций"""
    mock_response: mock.Mock = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Global Quote": {"05. price": "145.67"}}
    with mock.patch("src.utils.requests.get", return_value=mock_response):
        stocks: List[str] = ["IBM"]
        result: List[Dict[str, Any]] = get_stock_price(stocks)
        assert result == [{"stock": "IBM", "price": 145.67}]


def test_get_stock_price_failure(monkeypatch: mock.MagicMock) -> None:
    """Тестируем обработку ошибки при получении цены акций"""
    mock_response: mock.Mock = mock.Mock()
    mock_response.status_code = 500
    with mock.patch("src.utils.requests.get", return_value=mock_response):
        stocks: List[str] = ["IBM"]
        result: List[Dict[str, Any]] = get_stock_price(stocks)
        assert result == []  # или другое ожидаемое значение, если не удалось получить цену


def test_get_user_setting_invalid_data(monkeypatch: mock.MagicMock) -> None:
    """Тестируем случай, когда файл настроек существует, но содержит неверные данные"""
    mock_data: str = '{"user_currencies": "invalid_data"}'  # Неверный формат
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_data)):
        with pytest.raises(KeyError):
            get_user_setting("dummy_path.json")


def test_get_currency_rates_missing_keys(monkeypatch: mock.MagicMock) -> None:
    """Тестируем случай, когда API возвращает данные, но не содержит ожидаемых ключей"""
    mock_response: mock.Mock = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"quotes": {}}  # Нет ожидаемых курсов
    with mock.patch("src.utils.requests.get", return_value=mock_response):
        currencies: List[str] = ["RUB", "EUR"]
        result: List[Dict[str, Any]] = get_currency_rates(currencies)
        assert result == []  # Ожидаем пустой список


def test_get_stock_price_invalid_response(monkeypatch: mock.MagicMock) -> None:
    """Тестируем обработку ошибки при получении некорректных данных о ценах акций"""
    mock_response: mock.Mock = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}  # Нет данных о цене
    with mock.patch("src.utils.requests.get", return_value=mock_response):
        stocks: List[str] = ["IBM"]
        result: List[Dict[str, Any]] = get_stock_price(stocks)
        assert result == []  # Ожидаем пустой список


if __name__ == "__main__":
    pytest.main()
