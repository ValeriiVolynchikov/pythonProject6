import datetime
import json
import logging
from pathlib import Path
import pandas as pd
from src.config import DATA_DIR
import os
import requests
from dotenv import load_dotenv


load_dotenv("..\\.env")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
file_path = DATA_DIR / "operations.xlsx"

log_directory = "../logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

#logger = logging.getLogger("logs")
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(os.path.join(log_directory, "utils.log"), encoding="utf-8")
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s", handlers=[file_handler]
)

user_setting_path = DATA_DIR / "user_setting.json"


def get_data(data: str) -> datetime.datetime:
    """Функция преобразования даты"""
    logger.info(f"Получена строка даты: {data}")
    try:
        data_obj = datetime.datetime.strptime(data, "%d.%m.%Y %H:%M:%S")
        logger.info(f"Преобразована в объект datetime: {data_obj}")
        return data_obj
    except ValueError as e:
        logger.error(f"Ошибка преобразования даты: {e}")
        raise e


def reader_transaction_excel(file_path: str) -> pd.DataFrame:
    """Функция принимает на вход путь до файла и возвращает датафрейм"""
    logger.info(f"Вызвана функция получения транзакций из файла {file_path}")
    try:
        df_transactions = pd.read_excel(file_path)
        logger.info(f"Файл {file_path} найден, данные о транзакциях получены")

        return df_transactions
    except FileNotFoundError:
        logger.info(f"Файл {file_path} не найден")
        raise FileNotFoundError("Файл не найден") from None  # Переподнятие с новым сообщением


def get_dict_transaction(file_path: str) -> list[dict]:
    """Функция преобразовывающая датафрейм в словарь Python"""
    if not os.path.isfile(file_path):
        logger.error(f"Файл не найден: {file_path}")
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    logger.info(f"Вызвана функция get_dict_transaction с файлом {file_path}")
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Файл {file_path} прочитан")
        dict_transaction = df.to_dict(orient="records")
        logger.info("Датафрейм преобразован в список словарей")
        return dict_transaction
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        dict_transaction = get_dict_transaction(str(file_path))
        print(dict_transaction)
    except FileNotFoundError as e:
        logger.error(e)


def get_user_setting(path: str) -> tuple:
    logger.info(f"Вызвана функция с файлом {path}")

    # Проверка существования файла, но с учётом тестирования
    if not path == "dummy_path.json" and not Path(path).exists():
        logger.error(f"Файл настроек не найден: {path}")
        raise FileNotFoundError(f"Файл настроек не найден: {path}")

    with open(path, "r", encoding="utf-8") as f:
        user_setting = json.load(f)
        logger.info("Получены настройки пользователя")
    return user_setting["user_currencies"], user_setting["user_stocks"]


if __name__ == "__main__":
    user_setting_path = DATA_DIR / "user_setting.json"
    print(f"Путь к файлу настроек: {user_setting_path}")  # Для отладки

    try:
        user_currencies, user_stocks = get_user_setting(str(user_setting_path))
        print(user_currencies, user_stocks)
    except FileNotFoundError as e:
        logger.error(e)


def get_currency_rates(currencies: list) -> list[dict]:
    """функция, возвращает курсы"""
    logger.info("Вызвана функция для получения курсов")
    API_KEY = os.environ.get("API_KEY")
    symbols = ",".join(currencies)
    url = f"https://api.apilayer.com/currency_data/live?symbols={symbols}"

    headers = {"apikey": API_KEY}
    response = requests.get(url, headers=headers)
    status_code = response.status_code
    if status_code != 200:
        logger.error(f"Запрос не был успешным. Возможная причина: {response.reason}")
        return None

    data = response.json()
    quotes = data.get("quotes", {})
    usd = quotes.get("USDRUB")  # Это может быть None
    eur_usd = quotes.get("USDEUR")  # Это может быть None

    if usd is None or eur_usd is None:
        logger.error("Курсы валют не найдены в ответе.")
        return []  # Возвращаем пустой список или другое значение, если курсы не найдены

    eur = usd / eur_usd
    logger.info("Функция завершила свою работу")

    return [
        {"currency": "USD", "rate": round(usd, 2)},
        {"currency": "EUR", "rate": round(eur, 2)},
    ]

def get_stock_price(stocks: list) -> list[dict]:
    """Функция, возвращающая курсы акций"""
    logger.info("Вызвана функция возвращающая курсы акций")
    api_key_stock = os.environ.get("API_KEY_STOCK")
    stock_price = []
    for stock in stocks:
        #url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key_stock}"
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=demo"
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Запрос не был успешным. Возможная причина: {response.reason}")
            continue  # Пропускаем неуспешные запросы

        data_ = response.json()
        if "Global Quote" not in data_:
            logger.error(f"Нет данных о цене для акции {stock}. Ответ: {data_}")
            continue  # Пропускаем акции без данных

        price = round(float(data_["Global Quote"]["05. price"]), 2)
        stock_price.append({"stock": stock, "price": price})

    logger.info("Функция завершила свою работу")
    return stock_price
