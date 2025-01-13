import json
import unittest
from unittest.mock import Mock, patch

import pandas as pd

from src.views import form_main_page_info


class TestFormMainPageInfo(unittest.TestCase):

    @patch("src.views.pd.read_excel")
    @patch("src.views.get_currency_rates")
    @patch("src.views.get_expenses_cards")
    @patch("src.views.top_transaction")
    @patch("src.views.get_stock_price")
    @patch("src.views.greeting_by_time_of_day")
    def test_form_main_page_info(
        self,
        mock_greeting: Mock,
        mock_get_stock_price: Mock,
        mock_top_transaction: Mock,
        mock_get_expenses_cards: Mock,
        mock_get_currency_rates: Mock,
        mock_read_excel: Mock,
    ) -> None:
        # Настройка фиктивных данных
        mock_greeting.return_value = "Добрый день"
        mock_get_currency_rates.return_value = {"USDRUB": 73.5, "USDEUR": 0.85}
        mock_get_expenses_cards.return_value = [{"card_name": "Visa", "amount": 1000}]
        mock_top_transaction.return_value = [{"transaction": "Buy", "amount": 200}]
        mock_get_stock_price.return_value = [{"stock": "AAPL", "price": 150}]

        # Создаем фиктивный датафрейм
        mock_read_excel.return_value = pd.DataFrame(
            {"Дата операции": ["2021-12-01", "2021-12-15", "2021-12-17"], "Сумма": [200, 300, 150]}
        )

        # Параметры для тестирования
        date_input = "2021-12-17 14:52:20"

        # Выполнение тестируемой функции
        result = form_main_page_info(date_input)
        result_data = json.loads(result)

        self.assertEqual(result_data["greetings"], "Добрый день")
        self.assertEqual(len(result_data["cards"]), 1)
        self.assertEqual(result_data["currency_rates"]["USDRUB"], 73.5)
        self.assertEqual(result_data["top_transactions"], mock_top_transaction.return_value)
        self.assertEqual(result_data["stock_prices"], mock_get_stock_price.return_value)

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
