import json
from typing import Any, Dict, List
import pandas as pd
import pytest
from src.reports import spending_by_category


# Создаем фикстуру с тестовыми данными
@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    data = {
        "Категория": ["Супермаркеты", "Супермаркеты", "Рестораны", "Супермаркеты"],
        "Дата операции": ["01.01.2022 00:00:00", "15.01.2022 00:00:00", "20.01.2022 00:00:00", "28.02.2022 23:59:59"],
        "Сумма операции с округлением": [1000, 2000, 1500, 500]
    }
    return pd.DataFrame(data)


def test_spending_by_category_with_valid_category(sample_transactions: pd.DataFrame) -> None:
    expected_result: List[Dict[str, Any]] = [
        {"date": "01.01.2022 00:00:00", "amount": 1000},
        {"date": "15.01.2022 00:00:00", "amount": 2000},
        {"date": "28.02.2022 23:59:59", "amount": 500}
    ]

    # Изменяем диапазон на 90 дней перед 28.02.2022, чтобы все три транзакции включались
    result: str = spending_by_category(sample_transactions, "Супермаркеты", "28.02.2022 23:59:59")
    assert result == json.dumps(expected_result, indent=4, ensure_ascii=False)


def test_spending_by_category_with_invalid_category(sample_transactions: pd.DataFrame) -> None:
    expected_result: List[Dict[str, Any]] = []

    result: str = spending_by_category(sample_transactions, "Неправильная категория", "28.08.2022 23:59:59")
    assert result == json.dumps(expected_result, indent=4, ensure_ascii=False)


def test_spending_by_category_with_no_date(sample_transactions: pd.DataFrame) -> None:
    # Задаем фиксированную конечную дату
    fixed_date_end: str = "28.02.2022 23:59:59"  # Убедитесь, что эта дата соответствует вашим данным
    expected_result: List[Dict[str, Any]] = [
        {"date": "01.01.2022 00:00:00", "amount": 1000},
        {"date": "15.01.2022 00:00:00", "amount": 2000},
        {"date": "28.02.2022 23:59:59", "amount": 500}
    ]

    result: str = spending_by_category(sample_transactions, "Супермаркеты", fixed_date_end)
    assert result == json.dumps(expected_result, indent=4, ensure_ascii=False)


def test_spending_by_category_with_missing_date(sample_transactions: pd.DataFrame) -> None:
    # Проверка на случай отсутствия даты
    sample_transactions.loc[1, "Дата операции"] = None  # Установим значение None для теста
    expected_result: List[Dict[str, Any]] = [
        {"date": "01.01.2022 00:00:00", "amount": 1000},
        {"date": "28.02.2022 23:59:59", "amount": 500}
    ]

    result: str = spending_by_category(sample_transactions, "Супермаркеты", "28.02.2022 23:59:59")
    assert result == json.dumps(expected_result, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    pytest.main()
