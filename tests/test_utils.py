import datetime
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List
from unittest import mock

import pandas as pd
import pytest

from src.utils import (get_currency_rates, get_data, get_dict_transaction, get_expenses_cards, get_stock_price,
                       get_user_setting, greeting_by_time_of_day, reader_transaction_excel, top_transaction,
                       transaction_currency)

ROOT_PATH = Path(__file__).resolve().parent.parent


def test_get_data_input() -> None:
    """Проверяем, что функция корректно обрабатывает ввод"""
    input_data: str = "01.01.2023 12:00:00"
    expected_output: tuple[datetime.datetime, datetime.datetime] = (
        datetime.datetime(2023, 1, 1, 0, 0, 1),
        datetime.datetime(2023, 1, 1, 12, 0),
    )
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
        user_stocks: List[str] = user_settings[1]  # Исправлено
        assert user_currencies == ["USD", "EUR"]
        assert user_stocks == ["AAPL", "AMZN"]


def test_get_user_setting_empty(monkeypatch: mock.MagicMock) -> None:
    """Тестируем получение пустых настроек пользователя"""
    mock_data: str = '{"user_currencies": [], "user_stocks": []}'
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_data)):
        user_settings: tuple = get_user_setting("dummy_path.json")
        user_currencies: List[str] = user_settings[0]  # Исправлено
        user_stocks: List[str] = user_settings[1]  # Исправлено
        assert user_currencies == []
        assert user_stocks == []


def test_get_user_setting_file_not_found(monkeypatch: mock.MagicMock) -> None:
    """Тестируем обработку ошибки FileNotFoundError"""
    with mock.patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            get_user_setting("dummy_path.json")


def test_get_currency_rates_success(monkeypatch: mock.MagicMock) -> None:
    """Тестируем получение курсов валют при успешном запросе"""
    mock_response: mock.Mock = mock.Mock()
    mock_response.json.return_value = {
        "rates": {
            "RUB": 70,  # Пример курса USD к RUB
            "EUR": 0.85,  # Пример курса EUR к USD
        }
    }

    with mock.patch("src.utils.requests.get", return_value=mock_response):
        currencies: List[str] = ["USD", "EUR"]
        result: Any = get_currency_rates(currencies)

        # Проверяем, что в результатах есть курс для EUR
        assert any(rate["currency"] == "EUR" for rate in result)


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


@pytest.fixture
def start_date() -> dt.datetime:
    return dt.datetime(2021, 11, 25, 0, 0, 0)


@pytest.fixture
def fin_date() -> dt.datetime:
    return dt.datetime(2021, 11, 26, 0, 0, 0)


@pytest.fixture
def df_transactions() -> pd.DataFrame:
    """Фикстура для настройки тестовых данных."""
    df = pd.DataFrame(
        {
            "Дата операции": [
                "25.11.2021 21:29:17",
                "25.11.2021 20:47:27",
                "25.11.2021 20:29:13",
                "25.11.2021 19:02:06",
                "25.11.2021 18:46:44",
                "01.01.2022 10:00:00",
                "02.01.2022 11:00:00",
                "03.01.2022 12:00:00",
            ],
            "Номер карты": [
                "1234567890123456",
                "1234567890123456",
                "6543210987654321",
                "6543210987654321",
                "1234567890123456",
                "1234567890123456",
                "9876543210123456",
                "9876543210123456",
            ],
            "Сумма платежа": [-300.00, -151.90, -681.00, -132.70, -143.41, 100, 200, -250],
            "Категория": ["Еда", "Транспорт", "Развлечения", "Шопинг", "Еда", "Еда", "Транспорт", "Развлечения"],
            "Описание": ["Обед", "Такси", "Билет в кино", "Одежда", "Ужин", "Завтрак", "Поездка", "Концерт"],
        }
    )
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    return df


def test_greeting_by_time_of_day() -> None:
    """Тест функции приветствия."""
    greeting = greeting_by_time_of_day()
    assert greeting in ["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"]


def test_top_transaction(df_transactions: pd.DataFrame, start_date: dt.datetime, fin_date: dt.datetime) -> None:
    """Тест функции получения топ 5 транзакций."""

    # Вызов функции
    top_transactions = top_transaction(df_transactions, start_date, fin_date)

    # Проверяем, что мы получили 5 транзакций
    assert len(top_transactions) == 5

    # Проверяем, что первая транзакция имеет максимальную (по абсолютному значению) сумму
    max_amount = df_transactions["Сумма платежа"].min()  # Если вы сортируете по убыванию, используйте `.min()`
    assert top_transactions[0]["amount"] == max_amount


def test_get_expenses_cards(df_transactions: pd.DataFrame, start_date: dt.datetime) -> None:
    """Тест функции получения расходов по картам."""

    start_date_str = df_transactions.iloc[0]["Дата операции"].strftime("%d.%m.%Y %H:%M:%S")

    # Передаем в get_expenses_cards
    expenses_cards = get_expenses_cards(df_transactions, start_date_str)  # Проверьте как второй аргумент

    # Здесь вы можете добавить ваши проверки
    assert len(expenses_cards) == 2  # Две карты с расходами
    assert pytest.approx(expenses_cards[0]["total_spent"], rel=0.01) == 595.31  # Проверка суммы расходов


def test_transaction_currency(df_transactions: pd.DataFrame) -> None:
    """Тест функции получения транзакций в заданном интервале."""
    filtered_transactions = transaction_currency(df_transactions, "25.11.2021 21:29:17")
    assert len(filtered_transactions) == 5  # Все транзакции должны быть возвращены


if __name__ == "__main__":
    pytest.main()
