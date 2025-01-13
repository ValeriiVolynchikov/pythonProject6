import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import file_path
from src.utils import (get_currency_rates, get_data, get_expenses_cards, get_stock_price, greeting_by_time_of_day,
                       reader_transaction_excel, top_transaction, transaction_currency)

# Настройка логирования
logger = logging.getLogger("logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("../logs/views.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"  # Путь к директории с данными


def form_main_page_info(str_time: str) -> str:
    """Принимает дату в формате строки YYYY-MM-DD HH:MM:SS и возвращает общую информацию в формате
    json о банковских транзакциях за период с начала месяца до этой даты"""
    logger.info(f"Запуск функции main с параметром: {str_time}")

    try:
        data = pd.read_excel(file_path)
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        return json.dumps({"error": "Не удалось прочитать данные."}, ensure_ascii=False)

    try:
        date_obj = datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logger.error(f"Ошибка преобразования даты: {e}")
        return json.dumps({"error": "Некорректный формат даты."}, ensure_ascii=False)

    data_df = pd.DataFrame(data)
    data_df["datetime"] = pd.to_datetime(
        data_df["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True, errors="coerce"
    )

    json_data = data_df[data_df["datetime"].between(date_obj.replace(day=1), date_obj)]
    logger.info(f"Количество транзакций за период: {len(json_data)}")

    agg_dict = {
        "greetings": greeting_by_time_of_day(),
        "cards": get_expenses_cards(data_df, f"{date_obj.replace(day=1).date()} - {date_obj.date()}"),
        "top_transactions": top_transaction(json_data, date_obj.replace(day=1), date_obj),
        "currency_rates": get_currency_rates(["user_settings.json"]),
        "stock_prices": get_stock_price(["user_settings.json"]),
    }
    return json.dumps(agg_dict, ensure_ascii=False)

    # Логирование результатов
    logger.info("Собраны данные для JSON ответа")
    logger.info(f"Greetings: {agg_dict['greetings']}")
    logger.info(f"Карты: {agg_dict['cards']}")
    logger.info(f"Топ транзакции: {agg_dict['top_transactions']}")
    logger.info(f"Курсы валют: {agg_dict['currency_rates']}")
    logger.info(f"Цены на акции: {agg_dict['stock_prices']}")

    # Вывод в столбик
    print("\nРезультаты:")
    for key, value in agg_dict.items():
        print(f"{key.capitalize()}:")
        if isinstance(value, list):
            for item in value:
                # Преобразуем каждый элемент в строку и выводим
                print(f"  - {json.dumps(item, ensure_ascii=False)}")
        else:
            print(f"  - {value}")

    return json.dumps(agg_dict, ensure_ascii=False)


if __name__ == "__main__":
    df_transactions = reader_transaction_excel(str(file_path))
    # Определяем дату для фильтрации
    date_input = "17.12.2021 14:52:20"
    start_date, fin_date = get_data(date_input)

    top_transaction_list = top_transaction(df_transactions, start_date, fin_date)
    expenses_cards = get_expenses_cards(df_transactions, date_input)

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
    transaction_currency_df = transaction_currency(df_transactions, date_input)
    print(transaction_currency_df)
