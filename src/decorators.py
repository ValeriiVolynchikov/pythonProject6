import json
import logging
from typing import Any, Callable

# Настройка логирования
logging.basicConfig(
    filename="spending_by_category.log",  # Файл для логирования
    level=logging.INFO,  # Уровень логирования (можно использовать DEBUG, WARNING и другие)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат сообщений
)


def decorator_spending_by_category(func: Callable) -> Callable:
    """Логирует результат функции в файл по умолчанию spending_by_category.json,
    а также записывает сообщения в лог-файл."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        try:
            with open("spending_by_category.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            logging.info(f"Результат функции {func.__name__} успешно записан в spending_by_category.json")
        except Exception as e:
            logging.error(f"Произошла ошибка при записи в файл: {e}")
        return result

    return wrapper
