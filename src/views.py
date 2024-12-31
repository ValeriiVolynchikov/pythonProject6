import datetime as dt
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.config import file_path
from src.utils import get_currency_rates, get_data, get_stock_price, reader_transaction_excel

# Настройка логирования
logger = logging.getLogger("logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("../logs/views.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# ROOT_PATH = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent.parent / "data"  # Путь к директории с данными


def greeting_by_time_of_day() -> str:
    """Функция-приветствие"""
    hour = dt.datetime.now().hour
    if 4 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def create_json_response(expenses_cards: List[Any], top_transaction_list: List[Dict[str, Any]]) -> str:
    """Создает JSON-ответ с приветствием, картами расходов и топ-транзакциями"""
    greeting = greeting_by_time_of_day()
    response = {"greeting": greeting, "cards": expenses_cards, "top_transactions": top_transaction_list}
    return json.dumps(response, ensure_ascii=False, indent=2)


def top_transaction(df_transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Функция вывода топ 5 транзакций по сумме платежа"""
    logger.info("Начало работы функции top_transaction")

    # Убедитесь, что столбец "Дата операции" преобразован в datetime
    df_transactions["Дата операции"] = pd.to_datetime(
        df_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )
    # Удаляем транзакции с некорректными датами
    df_transactions = df_transactions.dropna(subset=["Дата операции"])

    top_transaction = df_transactions.sort_values(by="Сумма платежа", ascending=False).head(5)
    logger.info("Получен топ 5 транзакций по сумме платежа")

    result_top_transaction = top_transaction.to_dict(orient="records")
    top_transaction_list = []

    for transaction in result_top_transaction:
        if isinstance(transaction["Дата операции"], dt.datetime):  # Проверка на тип
            top_transaction_list.append(
                {
                    "date": transaction["Дата операции"].strftime("%d.%m.%Y"),
                    "amount": transaction["Сумма платежа"],
                    "category": transaction["Категория"],
                    "description": transaction["Описание"],
                }
            )
        else:
            logger.warning(f"Неверный формат даты: {transaction['Дата операции']}")

    logger.info("Сформирован список топ 5 транзакций")
    return top_transaction_list


def get_expenses_cards(df_transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Функция, возвращающая расходы по каждой карте"""
    logger.info("Начало выполнения функции get_expenses_cards")

    # Группировка и суммирование расходов
    cards_dict = (
        df_transactions.loc[df_transactions["Сумма платежа"] < 0]
        .groupby(by="Номер карты")["Сумма платежа"]
        .sum()
        .to_dict()
    )
    logger.debug(f"Получен словарь расходов по картам: {cards_dict}")

    expenses_cards = []
    for card, expenses in cards_dict.items():
        expenses_cards.append(
            {
                "last_digits": card[-4:],
                "total_spent": abs(expenses),
                "cashback": round(abs(expenses) * 0.01, 2),  # Расчет кэшбэка
            }
        )
        logger.info(f"Добавлен расход по карте {card}: {abs(expenses)}")

    logger.info("Завершение выполнения функции get_expenses_cards")
    return expenses_cards


def transaction_currency(df_transactions: pd.DataFrame, data: str) -> pd.DataFrame:
    """Функция, формирующая расходы в заданном интервале"""
    logger.info(f"Вызвана функция transaction_currency с аргументами: data={data}")
    fin_data = get_data(data)
    logger.debug(f"Получена конечная дата: {fin_data}")
    start_data = fin_data.replace(day=1)
    logger.debug(f"Получена начальная дата: {start_data}")
    fin_data = fin_data.replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=1)
    logger.debug(f"Обновлена конечная дата: {fin_data}")

    transaction_currency = df_transactions.loc[
        (pd.to_datetime(df_transactions["Дата операции"], dayfirst=True) <= fin_data)
        & (pd.to_datetime(df_transactions["Дата операции"], dayfirst=True) >= start_data)
    ]
    logger.info(f"Получен DataFrame transaction_currency: {transaction_currency}")

    return transaction_currency


if __name__ == "__main__":
    df_transactions = reader_transaction_excel(str(file_path))

    top_transaction_list = top_transaction(df_transactions)
    expenses_cards = get_expenses_cards(df_transactions)

    # Получаем данные о курсах валют и акциях
    currency_data = get_currency_rates(["USDRUB", "USDEUR"])
    stock_data = get_stock_price(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])

    # Создаем JSON-ответ
    json_response = {
        "greeting": "Добрый день",
        "cards": expenses_cards,
        "top_transactions": top_transaction_list,
        "currency_rates": currency_data,
        "stock_prices": stock_data,
    }

    # Преобразуем словарь в строку JSON
    json_response_str = json.dumps(json_response, ensure_ascii=False, indent=2)

    print(json_response_str)

    # Пример использования функции transaction_currency
    transaction_currency_df = transaction_currency(df_transactions, "25.11.2021 21:29:17")
    print(transaction_currency_df)
