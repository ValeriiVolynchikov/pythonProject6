import unittest
import pandas as pd
import json
from src.views import (
    greeting_by_time_of_day,
    create_json_response,
    top_transaction,
    get_expenses_cards,
    transaction_currency,
)

class TestViews(unittest.TestCase):

    def setUp(self):
        """Метод для настройки тестовых данных"""
        # Пример тестового DataFrame
        self.df_transactions = pd.DataFrame({
            "Дата операции": ["25.11.2021 21:29:17", "25.11.2021 20:47:27", "25.11.2021 20:29:13",
                              "25.11.2021 19:02:06", "25.11.2021 18:46:44"],
            "Номер карты": ["1234567890123456", "1234567890123456", "6543210987654321",
                            "6543210987654321", "1234567890123456"],
            "Сумма платежа": [-300.00, -151.90, -681.00, -132.70, -143.41],
            "Категория": ["Еда", "Транспорт", "Развлечения", "Шопинг", "Еда"],
            "Описание": ["Обед", "Такси", "Билет в кино", "Одежда", "Ужин"],
        })
        # Преобразуем даты
        self.df_transactions["Дата операции"] = pd.to_datetime(self.df_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors='coerce')

    def test_greeting_by_time_of_day(self):
        """Тест функции приветствия"""
        greeting = greeting_by_time_of_day()
        self.assertIn(greeting, ["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"])

    def test_create_json_response(self):
        """Тест создания JSON-ответа"""
        expenses_cards = [{"last_digits": "3456", "total_spent": 300.00, "cashback": 3.00}]
        top_transaction_list = [{"date": "25.11.2021", "amount": -300.00, "category": "Еда", "description": "Обед"}]
        response = create_json_response(expenses_cards, top_transaction_list)
        response_dict = json.loads(response)
        self.assertEqual(response_dict["greeting"], greeting_by_time_of_day())
        self.assertEqual(len(response_dict["cards"]), 1)
        self.assertEqual(len(response_dict["top_transactions"]), 1)

    def test_top_transaction(self):
        """Тест функции получения топ 5 транзакций"""
        top_transactions = top_transaction(self.df_transactions)

        # Проверяем, что мы получили 5 транзакций
        self.assertEqual(len(top_transactions), 5)

        # Проверяем, что первая транзакция имеет максимальную сумму
        max_amount = self.df_transactions["Сумма платежа"].max()
        self.assertEqual(top_transactions[0]["amount"], max_amount)

    def test_get_expenses_cards(self):
        """Тест функции получения расходов по картам"""
        expenses_cards = get_expenses_cards(self.df_transactions)
        self.assertEqual(len(expenses_cards), 2)  # Две карты с расходами
        self.assertAlmostEqual(expenses_cards[0]["total_spent"], 595.31, places=2)  # Проверка суммы расходов

    def test_transaction_currency(self):
        """Тест функции получения транзакций в заданном интервале"""
        filtered_transactions = transaction_currency(self.df_transactions, "25.11.2021 21:29:17")
        self.assertEqual(len(filtered_transactions), 5)  # Все транзакции должны быть возвращены

class TestTransactionFunctions(unittest.TestCase):

    def setUp(self):
        """Метод для настройки тестовых данных"""
        self.df_transactions = pd.DataFrame({
            "Дата операции": ["25.11.2021 21:29:17", "25.11.2021 20:47:27", "25.11.2021 20:29:13",
                              "25.11.2021 19:02:06", "25.11.2021 18:46:44", "01.01.2022 10:00:00",
                              "02.01.2022 11:00:00", "03.01.2022 12:00:00"],
            "Номер карты": ["1234567890123456", "1234567890123456", "6543210987654321",
                            "6543210987654321", "1234567890123456", "1234567890123456",
                            "9876543210123456", "9876543210123456"],
            "Сумма платежа": [-300.00, -151.90, -681.00, -132.70, -143.41, 100, 200, -250],
            "Категория": ["Еда", "Транспорт", "Развлечения", "Шопинг", "Еда", "Еда", "Транспорт", "Развлечения"],
            "Описание": ["Обед", "Такси", "Билет в кино", "Одежда", "Ужин", "Завтрак", "Поездка", "Концерт"]
        })
        self.df_transactions["Дата операции"] = pd.to_datetime(self.df_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors='coerce')

    def test_top_transaction_invalid_date(self):
        # Проверка на неверный формат даты
        self.df_transactions.loc[0, "Дата операции"] = pd.NaT  # Устанавливаем NaT
        result = top_transaction(self.df_transactions)
        self.assertEqual(len(result), 5)  # Должно вернуть 5 валидных транзакций

    def test_top_transaction_amounts(self):
        # Проверка правильности сумм платежей
        result = top_transaction(self.df_transactions)
        self.assertEqual(len(result), 5)# Проверяем, что вернулось 8 транзакций
        self.assertEqual(result[0]['amount'], 200)  # Проверяем, что первая транзакция по сумме - 100
        self.assertEqual(result[1]['amount'], 100)  # Вторая - 200

    # def test_get_expenses_cards(self):
    #     # Проверка получения расходов по картам
    #     result = get_expenses_cards(self.df_transactions)
    #     self.assertIn({"last_digits": "3456", "total_spent": 596.31, "cashback": 5.96}, result)
    #     #result = get_expenses_cards(self.df_transactions)

    # def setUp(self):
    #     # Создаем тестовые данные
    #     data = {
    #         "Номер карты": ["1234567890123456", "1234567890123456", "9876543210987654", "1234567890123456"],
    #         "Сумма платежа": [-100.00, -200.00, -300.00, -296.31],  # Общая сумма для 1234...3456 = -596.31
    #         "Дата операции": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]),
    #     }
    #     self.df_transactions = pd.DataFrame(data)

    def test_get_expenses_cards(self):
        # Проверка получения расходов по картам
        result = get_expenses_cards(self.df_transactions)

        # Ожидаемый результат
        expected_result = [
            {"last_digits": "4321", "total_spent": 813.70, "cashback": 8.14}
        ]
        # Проверяем, что результат содержит ожидаемый элемент
        self.assertIn({"last_digits": "4321", "total_spent": 813.70, "cashback": 8.14}, result)

        # Дополнительно, можно проверить, что все элементы в expected_result присутствуют в result
        for expected in expected_result:
            self.assertIn(expected, result)


    def test_transaction_currency_date_boundaries(self):
        # Проверка на пограничные даты
        data = "01.01.2022 00:00:00"  # Обновите дату с учетом времени
        result = transaction_currency(self.df_transactions, data)
        self.assertEqual(len(result), 1)  # Ожидаем 1 транзакцию в этом диапазоне

class TestTopTransaction(unittest.TestCase):

    def setUp(self):
        # Создаем тестовый DataFrame
        self.df_transactions = pd.DataFrame({
            "Дата операции": ["01.01.2022 10:00:00", "02.01.2022 11:00:00", "03.01.2022 12:00:00"],
            "Сумма платежа": [100, 200, 150],
            "Категория": ["Food", "Transport", "Entertainment"],
            "Описание": ["Lunch", "Taxi", "Movie"]
        })
        self.df_transactions["Дата операции"] = pd.to_datetime(self.df_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors='coerce')

    def test_invalid_date_format(self):
        # Проверка на неверный формат даты
        self.df_transactions.loc[0, "Дата операции"] = pd.NaT
        result = top_transaction(self.df_transactions)
        self.assertEqual(len(result), 2)  # Должно вернуть только 2 валидные транзакции

    def test_transaction_amounts(self):
        # Проверка правильности сумм платежей
        result = top_transaction(self.df_transactions)
        self.assertEqual(result[0]['amount'], 200)  # Проверяем, что первая транзакция по сумме - 200
        self.assertEqual(result[1]['amount'], 150)  # Вторая - 150

    def test_transaction_categories(self):
        # Проверка правильности категорий
        result = top_transaction(self.df_transactions)
        self.assertEqual(result[0]['category'], "Transport")  # Первая категория должна быть "Transport"
        self.assertEqual(result[1]['category'], "Entertainment")  # Вторая - "Entertainment"

class TestGetExpensesCards(unittest.TestCase):

    def setUp(self):
        # Создаем тестовый DataFrame
        self.df_transactions = pd.DataFrame({
            "Номер карты": ["1234567890123456", "1234567890123456", "9876543210123456"],
            "Сумма платежа": [-100, -150, -200]
        })

    def test_last_digits_of_card(self):
        # Проверка получения последних четырех цифр карты
        result = get_expenses_cards(self.df_transactions)
        self.assertIn({"last_digits": "3456", "total_spent": 250, "cashback": 2.5}, result)

    def test_cashback_calculation(self):
        # Проверка правильности вычисления кэшбэка
        result = get_expenses_cards(self.df_transactions)
        self.assertAlmostEqual(result[0]['cashback'], 2.5, places=2)  # Кэшбэк для первой карты



if __name__ == "__main__":
    unittest.main()

