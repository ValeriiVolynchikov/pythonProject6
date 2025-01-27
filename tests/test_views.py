import json
import logging
import os
import unittest
from unittest.mock import patch

import pandas as pd

from src.views import form_main_page_info

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


class TestFormMainPageInfo(unittest.TestCase):

    @patch("src.views.greeting_by_time_of_day")
    @patch("src.views.get_expenses_cards")
    @patch("src.views.pd.read_excel")
    def test_form_main_page_info(self, mock_read_excel, mock_get_expenses_cards, mock_greeting_by_time_of_day):

        mock_read_excel.return_value = pd.DataFrame(
            {
                "Дата операции": ["10.12.2021 16:02:10", "15.12.2021 13:01:22", "26.12.2021 01:12:25"],
                "Сумма платежа": [-200, -300, -150],
                "Категория": ["Еда", "Транспорт", "Развлечения"],  # Добавьте этот столбец
                "Описание": ["Ужин", "Такси", "Фильм"],  # И этот
            }
        )

        # Настройка mock для get_expenses_cards, чтобы возвращал реальные данные
        mock_get_expenses_cards.return_value = [{"cards": "1234", "amount": 100}, {"cards": "6789", "amount": 200}]

        # Настройка mock для greeting_by_time_of_day
        mock_greeting_by_time_of_day.return_value = "Добрый день"

        # Вызываем тестируемую функцию
        result_data = form_main_page_info("2021-12-25 14:52:20")  # Или ваш тестовый параметр
        # Проверяем результаты
        self.assertEqual(result_data["greeting"], "Добрый день")
        self.assertEqual(len(result_data["cards"]), 2)  # Ожидаем 2 карточки

    def test_invalid_date_format(self) -> None:
        with patch("src.views.pd.read_excel"):
            result = form_main_page_info("invalid_date")
            result_data = json.loads(result)
            self.assertEqual(result_data["error"], "Некорректный формат даты.")

    def test_read_excel_error(self) -> None:
        with patch("src.views.pd.read_excel", side_effect=FileNotFoundError):
            result = form_main_page_info("2021-12-17 14:52:20")
            result_data = json.loads(result)
            self.assertEqual(result_data["error"], "Не удалось прочитать данные.")


if __name__ == "__main__":
    unittest.main()
