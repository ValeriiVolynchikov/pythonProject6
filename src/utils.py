import datetime as dt
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

from src.config import DATA_DIR

load_dotenv("..\\.env")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
file_path = DATA_DIR / "operations.xlsx"

log_directory = "../logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(os.path.join(log_directory, "utils.log"), encoding="utf-8")
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s", handlers=[file_handler]
)


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


def get_data(data: str) -> Tuple[datetime, datetime]:
    """Функция преобразования даты"""
    logger.info(f"Получена строка даты: {data}")
    try:
        data_obj = datetime.strptime(data, "%d.%m.%Y %H:%M:%S")
        logger.info(f"Преобразована в объект datetime: {data_obj}")
        start_date = data_obj.replace(day=1, hour=0, minute=0, second=0)
        fin_date = data_obj
        return start_date, fin_date
    except ValueError as e:
        logger.error(f"Ошибка преобразования даты: {e}")
        raise e


def top_transaction(df_transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Функция вывода топ 5 транзакций по сумме платежа."""
    logger.info("Начало работы функции top_transaction")

    # Убедитесь, что столбец "Дата операции" преобразован в datetime
    df_transactions.loc[:, 'Дата операции'] = pd.to_datetime(df_transactions['Дата операции'], dayfirst=True,
                                                             errors='coerce')

    # Удаляем транзакции с некорректными датами
    df_transactions = df_transactions.dropna(subset=["Дата операции"])

    # Сортируем по "Сумма платежа" (по убыванию) и выбираем топ 5
    top_transactions = df_transactions.sort_values(by="Сумма платежа", ascending=True).head(5)
    logger.info("Получен топ 5 транзакций по сумме платежа")

    result_top_transaction = top_transactions.to_dict(orient="records")
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

    # Фильтруем расходы только на платежи
    filtered_expenses = df_transactions[df_transactions["Сумма платежа"] < 0]

    # Группировка и суммирование расходов
    cards_dict = (
        filtered_expenses.loc[filtered_expenses["Сумма платежа"] < 0]
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
                "total_spent": round(abs(expenses), 2),
                "cashback": round(abs(expenses) * 0.01, 2),  # Расчет кэшбэка
            }
        )
        logger.info(f"Добавлен расход по карте {card}: {abs(expenses)}")

    # Добавлено: Проверка на уникальность карт
    unique_cards = {card[-4:] for card in cards_dict.keys()}
    logger.info(f"Уникальные карты: {unique_cards}")

    # Обновлено: Возвращаем только уникальные карты
    expenses_cards = [card for card in expenses_cards if card["last_digits"] in unique_cards]

    logger.info("Завершение выполнения функции get_expenses_cards")
    return expenses_cards


def get_dict_transaction(file_path: str) -> list[dict]:
    """Функция преобразовывающая датафрейм в словарь Python"""
    if not os.path.isfile(file_path):
        logger.error(f"Файл не найден: {file_path}")
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    logger.info(f"Вызвана функция get_dict_transaction с файлом {file_path}")
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Файл {file_path} прочитан")
        dict_transaction = df.to_dict(orient="records")
        logger.info("Датафрейм преобразован в список словарей")
        return dict_transaction
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        dict_transaction = get_dict_transaction(str(file_path))
        print(dict_transaction)
    except FileNotFoundError as e:
        logger.error(e)


def transaction_currency(df_transactions: pd.DataFrame, data: str) -> pd.DataFrame:
    """Функция, формирующая расходы в заданном интервале"""
    logger.info(f"Вызвана функция transaction_currency с аргументами: data={data}")
    start_date, fin_date = get_data(data)  # Распаковка значений
    logger.debug(f"Получены начальная дата: {start_date}, конечная дата: {fin_date}")

    transaction_currency = df_transactions.loc[
        (pd.to_datetime(df_transactions["Дата операции"], dayfirst=True) <= fin_date)
        & (pd.to_datetime(df_transactions["Дата операции"], dayfirst=True) >= start_date)
    ]
    logger.info(f"Получен DataFrame transaction_currency: {transaction_currency}")

    return transaction_currency if not transaction_currency.empty else pd.DataFrame(columns=df_transactions.columns)


def reader_transaction_excel(file_path: str) -> pd.DataFrame:
    """Функция принимает на вход путь до файла и возвращает датафрейм"""
    logger.info(f"Вызвана функция получения транзакций из файла {file_path}")
    try:
        df_transactions = pd.read_excel(file_path)
        logger.info(f"Файл {file_path} найден, данные о транзакциях получены")

        return df_transactions
    except FileNotFoundError:
        logger.info(f"Файл {file_path} не найден")
        raise FileNotFoundError("Файл не найден") from None  # Переподнятие с новым сообщением


def get_currency_rates(user_currencies: list) -> list:
    """Возвращает курсы валют относительно RUB."""
    logger.info("Поиск курсов валют")

    result_currencies: list[Any] = []
    api_key = os.environ.get("API_KEY")  # Получите ваш API ключ из переменных окружения

    # Проверка наличия API ключа
    if not api_key:
        logger.error("API ключ отсутствует. Убедитесь, что он установлен в переменных окружения.")
        return []

    # Получаем курс всех валют относительно USD

    response = requests.get(
        f"https://openexchangerates.org/api/latest.json?app_id={api_key}&base=USD"
    )
    # Проверка успешности запроса
    if response.status_code != 200:
        logger.error("Ошибка при получении данных с API: %s", response.text)
        return []

    # Извлечение данных из ответа
    data = response.json()

    # Получаем курс USD к RUB
    rub_to_usd = data['rates'].get("RUB")

    # Список для хранения результатов
    result_currencies = []

    # Добавляем курс USD к RUB в результаты
    if rub_to_usd is not None:
        result_currencies.append({"currency": "USD", "rate": round(rub_to_usd, 2)})

    # Обрабатываем все запрашиваемые валюты
    for currency in user_currencies:
        if currency == "USD":
            continue  # USD уже добавлен
        elif currency in data['rates']:
            currency_to_usd = data['rates'][currency]
            # Конвертируем валюту к RUB
            currency_to_rub = round(((1 / currency_to_usd) * rub_to_usd), 2) if rub_to_usd else None
            result_currencies.append({"currency": currency, "rate": currency_to_rub})

    return result_currencies


def get_stock_price(user_stocks: list) -> list[dict]:
    """Функция, возвращающая курсы акций"""
    logger.info("Вызвана функция возвращающая курсы акций")

    api_key_stock = os.environ.get("API_KEY_STOCK")
    stock_price = []

    for stock in user_stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key_stock}"
        response = requests.get(url)

        if response.status_code != 200:
            logger.error(f"Запрос не был успешным. Возможная причина: {response.reason}")
            continue  # Пропускаем неуспешные запросы

        data_ = response.json()
        if "Global Quote" not in data_ or not data_["Global Quote"]:
            logger.error(f"Нет данных о цене для акции {stock}. Ответ: {data_}")
            continue  # Пропускаем акции без данных

        price = round(float(data_["Global Quote"]["05. price"]), 2)
        stock_price.append({"stock": stock, "price": price})

    logger.info("Функция завершила свою работу")
    return stock_price
