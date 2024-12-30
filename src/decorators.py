import json
from typing import Any


def decorator_spending_by_category(func: Any) -> Any:
    """Логирует результат функции в файл по умолчанию decorator_spending_by_category.json"""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        try:
            with open("spending_by_category.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Произошла ошибка при записи в файл: {e}")
        return result

    return wrapper