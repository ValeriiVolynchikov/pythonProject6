import json
import logging
import os
from typing import Any, Callable, Optional

# Настройка логирования
log_directory = "logs"  # Или любое другое место
os.makedirs(log_directory, exist_ok=True)  # Создаем директорию для логов, если не существует

logging.basicConfig(
    filename=os.path.join(log_directory, "spending_by_category.log"),  # Файл для логирования
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат сообщений
)


def decorator_spending_by_category(report_filename: Optional[str] = None) -> Callable:
    """Декоратор, который логирует результат функции в файл по умолчанию spending_by_category.json,
    а также записывает сообщения в лог-файл."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            # Определяем имя файла для записи
            filename = report_filename if report_filename else "spending_by_category.json"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                logging.info(f"Результат функции {func.__name__} успешно записан в {filename}")
            except Exception as e:
                logging.error(f"Произошла ошибка при записи в файл: {e}")
            return result

        return wrapper

    return decorator
