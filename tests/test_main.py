# # Тест для функции main
# import json
# import re  # Импортируем модуль re
# from unittest.mock import MagicMock, Mock, patch
#
# import pytest
#
# # from typing import Any
# # import json
# # from unittest.mock import patch, MagicMock
# from src.main import main  # Предположим, что ваш код находится в src/main.py
#
#
# @patch('src.views.create_json_response')
# @patch('src.views.get_expenses_cards')
# @patch('src.views.top_transaction')
# @patch('src.utils.get_dict_transaction')
# @patch('src.utils.reader_transaction_excel')
# @patch('src.views.greeting_by_time_of_day')
# @patch('src.services.get_transactions_ind')
# def test_main(
#     mock_get_transactions_ind: Mock,
#     mock_greeting_by_time_of_day: Mock,
#     mock_reader_transaction_excel: Mock,
#     mock_get_dict_transaction: Mock,
#     mock_top_transaction: Mock,
#     mock_get_expenses_cards: Mock,
#     mock_create_json_response: Mock,
#     capfd: pytest.CaptureFixture
# ) -> None:
#     # Настройка замокированных функций
#     mock_greeting_by_time_of_day.return_value = "Добрый день"
#     mock_reader_transaction_excel.return_value = MagicMock()  # Имитация DataFrame
#     mock_get_dict_transaction.return_value = {"transaction": "data"}
#
#     # Измените здесь на реальные данные, которые вы ожидаете
#     mock_get_expenses_cards.return_value = [
#         {"last_digits": "1112", "total_spent": 46207.08, "cashback": 462.07},
#         {"last_digits": "4556", "total_spent": 1780150.21, "cashback": 17801.5},
#         {"last_digits": "5091", "total_spent": 17367.5, "cashback": 173.68},
#         {"last_digits": "5441", "total_spent": 470854.8, "cashback": 4708.55},
#         {"last_digits": "5507", "total_spent": 84000.0, "cashback": 840.0},
#         {"last_digits": "6002", "total_spent": 69200.0, "cashback": 692.0},
#         {"last_digits": "7197", "total_spent": 2487419.56, "cashback": 24874.2}
#     ]
#
#     mock_top_transaction.return_value = [
#         {"date": "21.03.2019", "amount": 190044.51, "category": "Переводы",
#          "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
#         {"date": "23.10.2018", "amount": 177506.03, "category": "Переводы",
#          "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
#         {"date": "30.12.2021", "amount": 174000.0, "category": "Пополнения",
#          "description": "Пополнение через Газпромбанк"},
#         {"date": "30.07.2018", "amount": 150000.0, "category": "Пополнения",
#          "description": "Пополнение. Перевод средств с торгового счета"},
#         {"date": "31.07.2020", "amount": 150000.0, "category": "Пополнения",
#          "description": "Перевод с карты"}
#     ]
#
#     mock_get_transactions_ind.return_value = [{"amount": 1000}]  # Пример значения
#
#     mock_create_json_response.return_value = {
#         "greeting": "Добрый день",
#         "cards": [
#             {"last_digits": "1112", "total_spent": 46207.08, "cashback": 462.07},
#             {"last_digits": "4556", "total_spent": 1780150.21, "cashback": 17801.5},
#             {"last_digits": "5091", "total_spent": 17367.5, "cashback": 173.68},
#             {"last_digits": "5441", "total_spent": 470854.8, "cashback": 4708.55},
#             {"last_digits": "5507", "total_spent": 84000.0, "cashback": 840.0},
#             {"last_digits": "6002", "total_spent": 69200.0, "cashback": 692.0},
#             {"last_digits": "7197", "total_spent": 2487419.56, "cashback": 24874.2}
#         ],
#         "top_transactions": [
#             {"date": "21.03.2019", "amount": 190044.51, "category": "Переводы",
#              "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
#             {"date": "23.10.2018", "amount": 177506.03, "category": "Переводы",
#              "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
#             {"date": "30.12.2021", "amount": 174000.0, "category": "Пополнения",
#              "description": "Пополнение через Газпромбанк"},
#             {"date": "30.07.2018", "amount": 150000.0, "category": "Пополнения",
#              "description": "Пополнение. Перевод средств с торгового счета"},
#             {"date": "31.07.2020", "amount": 150000.0, "category": "Пополнения", "description": "Перевод с карты"}
#         ]
#     }
#
#     # Запуск тестируемой функции
#     main()
#
#     # Перехват вывода
#     captured = capfd.readouterr()
#
#     # Вывод содержимого для отладки
#     print(captured.out)
#
#     # Проверка ожидаемого вывода
#     assert "Добрый день" in captured.out
#     assert "JSON-ответ:" in captured.out
#
#     # Извлечение JSON-ответа с помощью регулярного выражения
#     json_match = re.search(r'{.*}', captured.out, re.DOTALL)
#     if json_match:
#         json_response = json_match.group(0)
#     else:
#         raise ValueError("JSON не найден в выводе")
#
#         # Проверка, что фактический вывод включает ожидаемую строку
#     expected_json = json.dumps(mock_create_json_response.return_value, indent=4, ensure_ascii=False)
#
#     # Сравнение JSON
#     assert json.loads(expected_json) == json.loads(json_response)
#
#
# if __name__ == "__main__":
#     pytest.main()
