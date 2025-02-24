import json
from typing import Any, Dict, List

import pytest

from src.services import get_transactions_ind

# Пример данных для тестов с необходимыми полями
transactions_data: List[Dict[str, Any]] = [
    {
        "Дата операции": "03.06.2018 14:19:08",
        "Дата платежа": "03.06.2018",
        "Номер карты": float("nan"),  # Используем NaN для обозначения отсутствия значения
        "Статус": "OK",
        "Сумма операции": -22000.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -22000.0,
        "Валюта платежа": "RUB",
        "Кэшбэк": float("nan"),
        "Категория": "Переводы",
        "MCC": float("nan"),
        "Описание": "Константин Ф.",
        "Бонусы (включая кэшбэк)": 0,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 22000.0,
    },
    {
        "Дата операции": "04.06.2018 10:15:30",
        "Дата платежа": "04.06.2018",
        "Номер карты": float("nan"),
        "Статус": "OK",
        "Сумма операции": -5000.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -5000.0,
        "Валюта платежа": "RUB",
        "Кэшбэк": float("nan"),
        "Категория": "Переводы",
        "MCC": float("nan"),
        "Описание": "Иванов И.И.",
        "Бонусы (включая кэшбэк)": 0,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 5000.0,
    },
    {
        "Дата операции": "05.06.2018 12:30:00",
        "Дата платежа": "05.06.2018",
        "Номер карты": float("nan"),
        "Статус": "OK",
        "Сумма операции": -3000.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -3000.0,
        "Валюта платежа": "RUB",
        "Кэшбэк": float("nan"),
        "Категория": "Переводы",
        "MCC": float("nan"),
        "Описание": "Петров П.П.",
        "Бонусы (включая кэшбэк)": 0,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 3000.0,
    },
    {
        "Дата операции": "06.06.2018 15:45:00",
        "Дата платежа": "06.06.2018",
        "Номер карты": float("nan"),
        "Статус": "OK",
        "Сумма операции": -1500.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -1500.0,
        "Валюта платежа": "RUB",
        "Кэшбэк": float("nan"),
        "Категория": "Коммунальные",
        "MCC": float("nan"),
        "Описание": "Оплата за свет",
        "Бонусы (включая кэшбэк)": 0,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 1500.0,
    },
]


def test_get_transactions_ind_success() -> None:
    """Тестируем успешный случай, когда есть соответствующие транзакции"""
    pattern: str = r"\b[А-Я][а-я]+\s[А-Я]\."  # Паттерн для поиска физических лиц
    expected_result: str = json.dumps(
        [
            {
                "Дата операции": "03.06.2018 14:19:08",
                "Дата платежа": "03.06.2018",
                "Номер карты": float("nan"),
                "Статус": "OK",
                "Сумма операции": -22000.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -22000.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": float("nan"),
                "Категория": "Переводы",
                "MCC": float("nan"),
                "Описание": "Константин Ф.",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 22000.0,
            },
            {
                "Дата операции": "04.06.2018 10:15:30",
                "Дата платежа": "04.06.2018",
                "Номер карты": float("nan"),
                "Статус": "OK",
                "Сумма операции": -5000.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -5000.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": float("nan"),
                "Категория": "Переводы",
                "MCC": float("nan"),
                "Описание": "Иванов И.И.",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 5000.0,
            },
            {
                "Дата операции": "05.06.2018 12:30:00",
                "Дата платежа": "05.06.2018",
                "Номер карты": float("nan"),
                "Статус": "OK",
                "Сумма операции": -3000.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -3000.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": float("nan"),
                "Категория": "Переводы",
                "MCC": float("nan"),
                "Описание": "Петров П.П.",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 3000.0,
            },
        ],
        ensure_ascii=False,
        indent=2,
    )

    result: str = get_transactions_ind(transactions_data, pattern)
    assert result == expected_result


def test_get_transactions_ind_no_matches() -> None:
    """Тестируем случай, когда нет соответствующих транзакций"""
    pattern: str = r"Не соответствует паттерну"
    result: str = get_transactions_ind(transactions_data, pattern)
    assert result == "[]"


def test_get_transactions_ind_empty_input() -> None:
    """Тестируем случай, когда входные данные пустые"""
    pattern: str = r"\b[А-Я][а-я]+\s[А-Я]\."
    result: str = get_transactions_ind([], pattern)
    assert result == "[]"


def test_get_transactions_ind_missing_fields() -> None:
    """Тестируем случай, когда транзакции не содержат нужных полей"""
    pattern: str = r"\b[А-Я][а-я]+\s[А-Я]\."
    transactions_with_missing_fields: List[Dict[str, Any]] = [
        {"Описание": "Перевод Иванов И.И."},  # Нет категории
        {"Категория": "Переводы"},  # Нет описания
    ]
    result: str = get_transactions_ind(transactions_with_missing_fields, pattern)
    assert result == "[]"


if __name__ == "__main__":
    pytest.main()
