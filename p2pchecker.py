import requests
import time

def get_p2p_offers(asset, fiat, trade_type, payment_method=None, amount=None):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {
        "asset": asset,  # "USDT", "BTC", etc.
        "fiat": fiat,  # "RUB", "USD", etc.
        "tradeType": trade_type,  # "BUY" or "SELL"
        "transAmount": amount if amount else "",
        "payTypes": [payment_method] if payment_method else [],
        "page": 1,
        "rows": 10,  # Количество объявлений
        "publisherType": None
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")
        return []

def display_offers(offers):
    for offer in offers:
        adv = offer["adv"]
        advertiser = offer["advertiser"]
        print(f"Цена: {adv['price']} {adv['fiatUnit']}, Мин: {adv['minSingleTransAmount']}, Макс: {adv['maxSingleTransAmount']}")
        print(f"Продавец: {advertiser['nickName']} ({advertiser['userNo']})")
        print(f"Методы оплаты: {', '.join(adv['tradeMethods'][0]['tradeMethodName'] for _ in adv['tradeMethods'])}")
        print("-" * 50)

if __name__ == "__main__":
    while True:
        asset = "USDT"  # Выберите актив
        fiat = "RUB"  # Фиатная валюта
        trade_type = "BUY"  # Тип сделки
        payment_method = "Tinkoff"  # Метод оплаты (опционально)
        amount = None  # Сумма сделки (опционально)

        offers = get_p2p_offers(asset, fiat, trade_type, payment_method, amount)
        display_offers(offers)

        print("Обновление через 60 секунд...")
        time.sleep(60)
