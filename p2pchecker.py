import requests
import time

def get_p2p_offers_binance(asset, fiat, trade_type, payment_method=None, amount=None):
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
        "rows": 10,  # Number of offers
        "publisherType": None
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Binance error: {response.status_code}, {response.text}")
        return []

def get_best_offer(offers, trade_type):
    if not offers:
        return None

    if trade_type == "BUY":
        return min(offers, key=lambda o: float(o["adv"]["price"]))
    else:  # SELL
        return max(offers, key=lambda o: float(o["adv"]["price"]))

def display_offer(exchange_name, offer, trade_type):
    adv = offer["adv"]
    advertiser = offer["advertiser"]
    print(f"Биржа: {exchange_name}")
    print(f"Цена: {adv['price']} {adv['fiatUnit']}, Мин: {adv['minSingleTransAmount']}, Макс: {adv['maxSingleTransAmount']}")
    print(f"Продавец: {advertiser['nickName']} ({advertiser['userNo']})")
    print(f"Методы оплаты: {', '.join(m['tradeMethodName'] for m in adv['tradeMethods'])}")
    print("-" * 50)

def calculate_spread(buy_price, sell_price):
    return (sell_price - buy_price) / buy_price * 100

if __name__ == "__main__":
    exchanges = {
        "Binance": get_p2p_offers_binance
        # Сюда можно добавить другие биржи, например "Huobi": get_p2p_offers_huobi
    }

    asset = "USDT"
    fiats = ["RUB", "UAH", "USD"]
    trade_type_buy = "BUY"
    trade_type_sell = "SELL"
    payment_method = "Tinkoff"  # Optional
    amount = None  # Optional

    while True:
        for fiat in fiats:
            best_buy_offer = None
            best_sell_offer = None

            print(f"=== Анализ для {fiat} ===")

            for exchange_name, get_offers in exchanges.items():
                buy_offers = get_offers(asset, fiat, trade_type_buy, payment_method, amount)
                sell_offers = get_offers(asset, fiat, trade_type_sell, payment_method, amount)

                best_buy = get_best_offer(buy_offers, trade_type_buy)
                best_sell = get_best_offer(sell_offers, trade_type_sell)

                if best_buy:
                    display_offer(exchange_name, best_buy, trade_type_buy)
                    if not best_buy_offer or float(best_buy["adv"]["price"]) < float(best_buy_offer["adv"]["price"]):
                        best_buy_offer = best_buy

                if best_sell:
                    display_offer(exchange_name, best_sell, trade_type_sell)
                    if not best_sell_offer or float(best_sell["adv"]["price"]) > float(best_sell_offer["adv"]["price"]):
                        best_sell_offer = best_sell

            if best_buy_offer and best_sell_offer:
                buy_price = float(best_buy_offer["adv"]["price"])
                sell_price = float(best_sell_offer["adv"]["price"])
                spread = calculate_spread(buy_price, sell_price)

                print(f"Лучший курс покупки: {buy_price} {fiat}")
                print(f"Лучший курс продажи: {sell_price} {fiat}")
                print(f"Спред: {spread:.2f}%")
            else:
                print("Не удалось найти подходящие предложения.")

            print("=" * 50)

        print("Обновление через 60 секунд...")
        time.sleep(5)
