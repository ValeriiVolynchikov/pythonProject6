import json
import logging
import re
from src.utils import get_dict_transaction

# Настройка логирования
logger = logging.getLogger("logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("..\\logs\\services.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_transactions_ind(dict_transaction: list[dict], pattern: str) -> str:
    """Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам."""
    logger.info("Вызвана функция get_transactions_ind")
    list_transactions_fl = []

    for trans in dict_transaction:
        # Проверяем, что "Описание" соответствует паттерну и категория равна "Переводы"
        if ("Описание" in trans and
                re.match(pattern, trans["Описание"]) and
                trans.get("Категория") == "Переводы"):
            list_transactions_fl.append(trans)

    logger.info(f"Найдено {len(list_transactions_fl)} транзакций, соответствующих паттерну и категории 'Переводы'")

    if list_transactions_fl:
        list_transactions_fl_json = json.dumps(list_transactions_fl, ensure_ascii=False, indent=2)
        logger.info(f"Возвращен JSON со {len(list_transactions_fl)} транзакциями")
        return list_transactions_fl_json
    else:
        logger.info("Возвращен пустой список")
        return "[]"


if __name__ == "__main__":
    # Вызываем функцию, передавая данные и паттерн для поиска физических лиц
    list_transactions_fl_json = get_transactions_ind(
        get_dict_transaction("..\\data\\operations.xlsx"),
        pattern=r"\b[А-Я][а-я]+\s[А-Я]\."  # Паттерн для поиска физических лиц
    )
    print(list_transactions_fl_json)
