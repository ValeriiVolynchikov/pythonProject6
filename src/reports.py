import datetime
import json
import pandas as pd
from typing import Optional, Any
import logging
import os
from pathlib import Path
from src.decorators import decorator_spending_by_category
from src.utils import get_dict_transaction, reader_transaction_excel


# Определяем пути
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Выйти на уровень выше, чтобы достичь корня
DATA_DIR = PROJECT_ROOT / 'data'  # Путь к директории с данными
file_path = DATA_DIR / 'operations.xlsx'  # Путь к вашему файлу Excel

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
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> Any:
    """Функция возвращающая траты за последние 3 месяца по заданной категории"""

    final_list = []

    # Определяем начальную дату
    if date is None:
        date_start = datetime.datetime.now() - datetime.timedelta(days=90)
    else:
        day, month, year = date.split(".")
        date_obj = datetime.datetime(int(year), int(month), int(day))
        date_start = date_obj - datetime.timedelta(days=90)

    for index, transaction in transactions.iterrows():
        if transaction['Категория'] == category:
            if pd.isna(transaction["Дата платежа"]) or isinstance(transaction["Дата платежа"], float):
                continue
            try:
                transaction_date = datetime.datetime.strptime(str(transaction["Дата платежа"]), "%d.%m.%Y")
                if date_start <= transaction_date <= date_start + datetime.timedelta(days=90):
                    final_list.append({
                        "date": transaction["Дата платежа"],
                        "amount": transaction["Сумма платежа"]
                    })
            except ValueError:
                continue

    return json.dumps(final_list, indent=4, ensure_ascii=False)

if __name__ == "__main__":
         try:
             f = pd.DataFrame(get_dict_transaction(file_path))
             print(spending_by_category(f, 'Каршеринг', '25.12.2021'))
         except FileNotFoundError as e:
             logging.error(e)
         except Exception as e:  # Ловим все остальные ошибки
             logging.error(f"Произошла ошибка: {e}")

# if __name__ == "__main__":
#     print("Запуск модуля reports.py...")
#
#     try:
#         # Получение данных из файла
#         data_dict = get_dict_transaction(file_path)
#         print(f"Полученные данные: {data_dict}")  # Отладочный вывод
#
#         # Создание DataFrame
#         f = pd.DataFrame(data_dict)
#         print(f"DataFrame: {f}")  # Показываем DataFrame
#
#         if f.empty:
#             print("DataFrame пустой, нет данных для обработки.")
#         else:
#             # Вызов функции для получения расходов по категории
#             result = spending_by_category(f, 'Супермаркеты', '25.12.2021')
#             print("Результат:", result)  # Выводим результат работы функции
#
#     except FileNotFoundError as e:
#         logging.error(e)
#         print(f"Ошибка: {e}")
#     except Exception as e:  # Ловим все остальные ошибки
#         logging.error(f"Произошла ошибка: {e}")
#         print(f"Ошибка: {e}")
