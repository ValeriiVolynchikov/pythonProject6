import json
import os
from typing import Any, Dict, List, TypeVar

import pandas as pd
import pytest

from src.decorators import decorator_spending_by_category

# Define a type variable for clarity
T = TypeVar('T', bound=Dict[str, Any])


# Создание тестового набора данных для транзакций
@pytest.fixture
def transactions() -> pd.DataFrame:
    return pd.DataFrame({
        'category': ['food', 'entertainment', 'food', 'clothing'],
        'amount': [10.0, 20.0, 15.0, 5.0]
    })


# Тестирование декоратора без параметров
def test_spending_by_category_default_filename(transactions: pd.DataFrame) -> None:
    @decorator_spending_by_category()
    def spending_by_category(transactions: pd.DataFrame, category: str) -> List[Dict[str, Any]]:
        return transactions[transactions['category'] == category].to_dict(orient='records')

    result = spending_by_category(transactions, 'food')
    assert result == [{'category': 'food', 'amount': 10.0}, {'category': 'food', 'amount': 15.0}]

    # Проверяем, что файл был создан
    assert os.path.exists('spending_by_category.json')

    with open('spending_by_category.json', 'r', encoding='utf-8') as f:
        saved_result = json.load(f)

    assert saved_result == result

    # Удаляем файл после теста
    os.remove('spending_by_category.json')


# Тестирование декоратора с параметром
def test_spending_by_category_custom_filename(transactions: pd.DataFrame) -> None:
    @decorator_spending_by_category('test_report.json')
    def spending_by_category(transactions: pd.DataFrame, category: str) -> List[Dict[str, Any]]:
        return transactions[transactions['category'] == category].to_dict(orient='records')

    result = spending_by_category(transactions, 'clothing')
    assert result == [{'category': 'clothing', 'amount': 5.0}]

    # Проверяем, что файл был создан с нужным именем
    assert os.path.exists('test_report.json')

    with open('test_report.json', 'r', encoding='utf-8') as f:
        saved_result = json.load(f)

    assert saved_result == result

    # Удаляем файл после теста
    os.remove('test_report.json')


if __name__ == "__main__":
    pytest.main()
