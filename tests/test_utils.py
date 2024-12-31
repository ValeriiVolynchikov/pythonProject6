import pytest
import datetime
from pathlib import Path
from src.config import file_path
from src.utils import get_data, reader_transaction_excel, get_dict_transaction, get_user_setting, get_currency_rates
import pandas as pd
from unittest import mock

ROOT_PATH = Path(__file__).resolve().parent.parent

def test_get_data_input():
    """Проверяем, что функция корректно обрабатывает ввод"""
    input_data = "01.01.2023 12:00:00"
    expected_output = datetime.datetime(2023, 1, 1, 12, 0, 0)
    assert get_data(input_data) == expected_output

def test_get_data_format():
    """Проверяем, что функция обрабатывает исключение при неверном формате ввода"""
    input_data = "01-01-2023 12:00:00"
    with pytest.raises(ValueError):
        get_data(input_data)

def test_get_data_empty_input():
    """Проверяем, что функция обрабатывает пустой ввод"""
    input_data = ""
    with pytest.raises(ValueError):
        get_data(input_data)

def test_reader_excel_file_not_found():
    """Проверка, что функция поднимает исключение при передаче несуществующего файла"""
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        reader_transaction_excel("path/to/non-existent/file.xlsx")

def test_reader_transaction_excel_success(monkeypatch):
    """Тестируем успешное чтение Excel файла"""
    mock_df = pd.DataFrame({'transaction_id': [1, 2, 3]})
    with mock.patch('pandas.read_excel', return_value=mock_df):
        result = reader_transaction_excel('test_file.xlsx')
        assert result.shape == mock_df.shape
        assert all(result['transaction_id'] == mock_df['transaction_id'])

def test_get_dict_transaction_file_not_found():
    """Тест проверяет обработку ошибки FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        get_dict_transaction("non_existent_file.xlsx")



def test_get_user_setting_success(monkeypatch):
    """Тестируем успешное получение настроек пользователя"""
    mock_data = '{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}'
    # Замокаем open, чтобы вернуть mock_data
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_data)):
        user_currencies, user_stocks = get_user_setting("dummy_path.json")
        assert user_currencies == ["USD", "EUR"]
        assert user_stocks == ["AAPL", "AMZN"]

def test_get_user_setting_success(monkeypatch):
    """Тестируем успешное получение настроек пользователя"""
    mock_data = '{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}'
    # Замокаем open, чтобы вернуть mock_data
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_data)):
        user_currencies, user_stocks = get_user_setting("dummy_path.json")
        assert user_currencies == ["USD", "EUR"]
        assert user_stocks == ["AAPL", "AMZN"]

def test_get_user_setting_empty(monkeypatch):
    """Тестируем получение пустых настроек пользователя"""
    mock_data = '{"user_currencies": [], "user_stocks": []}'
    # Замокаем open, чтобы вернуть mock_data
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_data)):
        user_currencies, user_stocks = get_user_setting("dummy_path.json")
        assert user_currencies == []
        assert user_stocks == []

def test_get_user_setting_file_not_found(monkeypatch):
    """Тестируем обработку ошибки FileNotFoundError"""
    with mock.patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            get_user_setting("dummy_path.json")

def test_get_currency_rates_success(monkeypatch):
    """Тестируем успешное получение курсов валют"""
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "quotes": {
            "USDRUB": 73.97,
            "USDEUR": 0.84
        }
    }
    with mock.patch('src.utils.requests.get', return_value=mock_response):
        currencies = ["RUB", "EUR"]
        result = get_currency_rates(currencies)
        expected_result = [
            {"currency": "USD", "rate": 73.97},
            {"currency": "EUR", "rate": round(73.97 / 0.84, 2)},
        ]
        assert result == expected_result

def test_get_currency_rates_failure(monkeypatch):
    """Тестируем обработку ошибки при получении курсов валют"""
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_response.reason = "Internal Server Error"
    with mock.patch('src.utils.requests.get', return_value=mock_response):
        currencies = ["RUB", "EUR"]
        result = get_currency_rates(currencies)
        assert result is None

if __name__ == "__main__":
    pytest.main()
