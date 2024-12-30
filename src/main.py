from src.config import file_path
from src.reports import spending_by_category
from src.services import get_transactions_ind
from src.utils import get_dict_transaction, reader_transaction_excel
from src.views import create_json_response, get_expenses_cards, greeting_by_time_of_day, top_transaction


def main() -> None:
    # 1. Получение текущего времени и приветствия
    greeting = greeting_by_time_of_day()
    print(greeting)  # Выводим приветствие

    # 2. Чтение транзакций из Excel
    try:
        transactions_df = reader_transaction_excel(str(file_path))
    except FileNotFoundError:
        print(f"Ошибка: файл '{file_path}' не найден.")
        return

    # 3. Преобразование DataFrame в словарь
    transactions_dict = get_dict_transaction(str(file_path))

    # 4. Генерация карт расходов
    expenses_cards = get_expenses_cards(transactions_df)

    # 5. Топ транзакции
    top_transactions = top_transaction(transactions_df)

    # 6. Формирование JSON-ответа
    json_response = create_json_response(expenses_cards, top_transactions)

    # 7. Вывод JSON-ответа
    print("JSON-ответ:")
    print(json_response)

    # 8. Остаток по счету (пример функции, требующей дополнительной реализации)
    account_balance = 1000  # Это число должно быть получено из ваших данных
    print(f"У вас на счету: {account_balance} рублей.")

    # 9. Кешбэк (пример функции, требующей дополнительной реализации)
    cashback = 0  # Это значение должно быть вычислено по вашим критериям
    print(f"Ваш кешбэк за месяц: {cashback} рублей.")

    # 10. Регистрация всех транзакций инд
    recent_transactions_json = get_transactions_ind(transactions_dict, "Физлицо")
    print("JSON со всеми транзакциями по физлицам:")
    print(recent_transactions_json)

    # 11. Пример: получение расходов по категории за последние 3 месяца
    category = "Продукты"  # Название категории, для которой вы хотите получить данные
    category_expenses = spending_by_category(transactions_df, category)
    print(f"Расходы по категории '{category}' за последние 3 месяца:")
    print(category_expenses)


if __name__ == "__main__":
    main()
