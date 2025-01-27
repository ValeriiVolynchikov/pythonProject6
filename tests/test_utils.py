from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest
from freezegun import freeze_time

from src.utils import (get_currency_rates, get_data, get_dict_transaction, get_expenses_cards, get_stock_price,
                       greeting_by_time_of_day, top_transaction)

# Тестовые данные
mock_transactions = pd.DataFrame({
    "Дата операции": ["01.01.2021 12:00:00", "02.01.2021 12:00:00", "03.01.2021 12:00:00"],
    "Сумма платежа": [-1000, -500, -200],
    "Номер карты": ["1234567812345678", "8765432187654321", "1234567812345678"],
    "Категория": ["Еда", "Топливо", "Развлечения"],
    "Описание": ["Обед", "Заправка", "Кино"]
})

# Преобразуем даты в datetime
mock_transactions["Дата операции"] = pd.to_datetime(mock_transactions["Дата операции"], dayfirst=True)


@freeze_time("2022-01-01 08:00:00")
def test_greeting_by_time_of_day() -> None:
    assert greeting_by_time_of_day() == "Доброе утро"


def test_get_data() -> None:
    start_date, fin_date = get_data("01.01.2021 12:00:00")
    assert start_date == datetime(2021, 1, 1, 0, 0, 0)
    assert fin_date == datetime(2021, 1, 1, 12, 0, 0)

    with pytest.raises(ValueError):
        get_data("Некорректная дата")


def test_top_transaction() -> None:
    result = top_transaction(mock_transactions)
    assert len(result) == 3  # Ожидаем 3 транзакции
    assert result[0]["amount"] == -1000  # Проверяем, что первая транзакция с самой высокой суммой


def test_get_expenses_cards() -> None:
    result = get_expenses_cards(mock_transactions)
    assert len(result) == 2  # Ожидаем 2 уникальные карты
    assert result[0]["last_digits"] == "5678"  # Проверяем последние 4 цифры первой карты


def test_get_dict_transaction(mocker: Any) -> None:
    # Используем mock для pd.read_excel
    mocker.patch("src.utils.pd.read_excel", return_value=mock_transactions)
    mocker.patch("os.path.isfile", return_value=True)  # Мокируем os.path.isfile
    result = get_dict_transaction("fake_path.xlsx")  # Это не вызовет ошибку
    assert len(result) == 3  # Ожидаем 3 транзакции


def test_get_currency_rates(mocker: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    # Устанавливаем переменную окружения API_KEY
    monkeypatch.setenv("API_KEY", "fake_api_key")

    mocker.patch("src.utils.requests.get", return_value=MagicMock(status_code=200, json=lambda: {
        'rates': {
            'RUB': 73.21,
            'EUR': 87.08,
            'USD': 1.0
        }
    }))
    result = get_currency_rates(["EUR", "USD"])
    assert len(result) == 2  # Ожидаем 2 валюты


def test_get_stock_price(mocker: Any) -> None:
    mocker.patch("src.utils.requests.get", return_value=MagicMock(status_code=200, json=lambda: {
        "Global Quote": {
            "05. price": "150.12"
        }
    }))
    result = get_stock_price(["AAPL"])
    assert len(result) == 1  # Ожидаем 1 акцию
    assert result[0]["stock"] == "AAPL"  # Проверяем, что акция - это AAPL


if __name__ == "__main__":
    pytest.main()
