import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import os
import logging
import json
from pathlib import Path
from src.decorators import decorator_spending_by_category
from src.utils import get_dict_transaction


# Определяем пути
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Выйти на уровень выше, чтобы достичь корня
DATA_DIR = PROJECT_ROOT / "data"  # Путь к директории с данными
file_path = DATA_DIR / "operations.xlsx"  # Путь к вашему файлу Excel

# Проверка пути
print(f"Путь к файлу: {file_path}")  # Выводим путь для отладки

# Проверка и создание директории для логов, если она не существует
log_directory = PROJECT_ROOT / "logs"
os.makedirs(log_directory, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    filename=os.path.join(log_directory, "reports.log"),
    filemode="w",
)
logger = logging.getLogger(__name__)

spending_by_category_logger = logging.getLogger()


@decorator_spending_by_category
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """Функция возвращающая траты за последние 90 дней по заданной категории."""

    logger.info(f"Запуск функции spending_by_category для категории: {category} и даты: {date}")

    final_list = []

    # Определяем конечную дату
    if date is None:
        date_end = pd.Timestamp.now()  # Используем Pandas Timestamp для согласованности
        logger.info("Дата окончания не указана, используется текущая дата.")
    else:
        date_end = pd.to_datetime(date, format="%d.%m.%Y %H:%M:%S", errors='coerce')  # Преобразуем дату
        if pd.isna(date_end):  # Проверяем на NaT
            logger.error(f"Неверный формат даты: {date}")
            raise ValueError(f"Неверный формат даты: {date}")

    # Начальная дата - 90 дней назад от конечной даты
    if date_end is not None:  # Убедитесь, что date_end не None
        date_start = date_end - pd.Timedelta(days=90)
    else:
        raise ValueError("date_end должен быть корректной временной меткой.")

    # Преобразуем даты операций и удаляем записи без дат
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], format="%d.%m.%Y %H:%M:%S",
                                                   errors='coerce')

    # Приводим тип к Timestamp
    transactions['Дата операции'] = transactions['Дата операции'].astype('datetime64[ns]')

    # Удаляем записи с NaT
    transactions = transactions.dropna(subset=['Дата операции'])

    filtered_transactions = transactions[
        (transactions["Категория"] == category) &
        (pd.notna(transactions["Дата операции"]) &
         transactions["Дата операции"].between(date_start, date_end)) &
        (transactions["Сумма операции с округлением"] > 0)
    ]

    logger.info(
        f"Найдено {len(filtered_transactions)} транзакций для категории '{category}' за период с {date_start} по {date_end}.")

    # Формируем результирующий список
    for _, transaction in filtered_transactions.iterrows():
        final_list.append({
            "date": transaction["Дата операции"].strftime("%d.%m.%Y %H:%M:%S"),
            "amount": transaction["Сумма операции с округлением"]
        })

    logger.info(f"Возвращаемый результат: {json.dumps(final_list, indent=4, ensure_ascii=False)}")

    # Возвращаем результат в формате JSON
    return json.dumps(final_list, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    try:
        f = pd.DataFrame(get_dict_transaction(str(file_path)))
        logger.info(f"Загруженные данные: \n{f}")  # Логируем загруженные данные
        result = spending_by_category(f, "Каршеринг", "30.12.2021 19:18:22")
        logger.info(f"Результат выполнения: {result}")
        print(result)
    except FileNotFoundError as e:
        logger.error("Файл не найден: %s", e)
    except Exception as e:  # Ловим все остальные ошибки
        logger.error("Произошла ошибка: %s", e)

# if __name__ == "__main__":
#     try:
#         f = pd.DataFrame(get_dict_transaction(str(file_path)))
#         print(f"Загруженные данные: \n{f}")  # Выводим загруженные данные для отладки
#         print(spending_by_category(f, "Супермаркеты", "31.12.2021 16:44:00"))
#     except FileNotFoundError as e:
#         logging.error(e)
#     except Exception as e:  # Ловим все остальные ошибки
#         logging.error(f"Произошла ошибка: {e}")
