import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Union

import pandas as pd

from src.config import file_path, load_user_currencies, load_user_stocks
from src.utils import get_currency_rates, get_expenses_cards, get_stock_price, greeting_by_time_of_day, top_transaction

# Настройка логирования
log_directory = "../logs"

# Проверка на существование директории для логов
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logger = logging.getLogger("logs")
logger.setLevel(logging.INFO)

# Проверка на наличие обработчиков, чтобы избежать дублирования
if not logger.hasHandlers():
    file_handler = logging.FileHandler(os.path.join(log_directory, "views.log"), encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


def form_main_page_info(some_param: Union[str, dict], return_json: bool = False) -> Union[str, Dict[str, Any]]:
    """Принимает дату в формате строки YYYY-MM-DD HH:MM:SS и возвращает общую информацию в формате
    json о банковских транзакциях за период с начала месяца до этой даты"""
    logger.info(f"Запуск функции main с параметром: {some_param}")

    currencies = load_user_currencies()  # Загружаем валюты
    stocks = load_user_stocks()  # Загружаем акции
    date_obj = None

    # Проверка типа входного аргумента
    if isinstance(some_param, str):
        # Обработка строки
        try:
            date_obj = datetime.strptime(some_param, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            logger.error(f"Ошибка преобразования даты: {e}")
            return json.dumps({"error": "Некорректный формат даты."}, ensure_ascii=False)
    elif isinstance(some_param, dict) and 'date' in some_param:
        # Обработка JSON объекта
        try:
            date_obj = datetime.strptime(some_param['date'], "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            logger.error(f"Ошибка преобразования даты: {e}")
            return json.dumps({"error": "Некорректный формат даты."}, ensure_ascii=False)
    else:
        return json.dumps({"error": "Некорректный тип параметра. Ожидается строка или JSON."}, ensure_ascii=False)

    try:
        data = pd.read_excel(file_path)
        # Преобразование DataFrame
        data_df = pd.DataFrame(data)
        logger.info(f"Исходный DataFrame: {data_df}")  # контроль
        data_df["datetime"] = pd.to_datetime(
            data_df["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True, errors="coerce"
        )
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        return json.dumps({"error": "Не удалось прочитать данные."}, ensure_ascii=False)

    # Определяем диапазон дат
    start_date = date_obj.replace(day=1, hour=0, minute=0, second=0)
    fin_date = date_obj
    logger.debug(f"Диапазон дат: с {start_date} по {fin_date}")  # контроль

    json_data = data_df[data_df["datetime"].between(start_date, fin_date)]
    logger.info(f"Количество транзакций за период: {len(json_data)}")

    # Получаем приветствие
    greeting = greeting_by_time_of_day()

    # Формируем итоговый словарь
    agg_dict = {
        "greeting": greeting,
        "cards": get_expenses_cards(json_data) if not json_data.empty else [],
        "top_transactions": top_transaction(json_data) if not json_data.empty else [],
        "currency_rates": get_currency_rates(currencies),
        "stock_prices": get_stock_price(stocks),
    }
    logger.info(f"Filtered transactions: {json_data}")
    logger.info(f"Agg dict before serialization: {agg_dict}")

    # Если нет транзакций, добавляем сообщение об ошибке
    if json_data.empty:
        logger.warning("Нет транзакций за указанный период.")
        agg_dict["error"] = "Нет транзакций за указанный период."

    return json.dumps(agg_dict, ensure_ascii=False, indent=2) if return_json else agg_dict


if __name__ == "__main__":
    result_json = form_main_page_info('2021-12-17 14:52:09', return_json=True)
    print(result_json)
