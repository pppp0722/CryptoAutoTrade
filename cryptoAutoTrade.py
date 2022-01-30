import time
import pyupbit
import datetime
import numpy as np

access_key = "access_key"
secret_key = "secret_key"
crypto_name = "KRW-BORA"

# 7일동안 최대 수익 k값 찾기
def get_best_k():
    max_k = 0
    max_ror = 0

    for k in np.arange(0.1, 1, 0.1):
        df = pyupbit.get_ohlcv(crypto_name, count = 7)
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                            df['close'] / df['target'],
                            1)

        ror = df['ror'].cumprod()[-2]

        if ror > max_ror:
            max_k = k
            max_ror = ror

    return max_k

# 변동성 돌파 전략으로 매수 목표가 조회
def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval = "day", count = 2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

# 시작 시간 조회
def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval = "day", count = 1)
    start_time = df.index[0]
    return start_time

#  15일 이동 평균선 조회
#  def get_ma15(ticker):
#     df = pyupbit.get_ohlcv(ticker, interval = "day", count = 15)
#     ma15 = df['close'].rolling(15).mean().iloc[-1]
#     return ma15

# 잔고 조회
def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

# 현재가 조회
def get_current_price(ticker):
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access_key, secret_key)

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(crypto_name)
        end_time = start_time + datetime.timedelta(days = 1)

        # 9:00 ~ 8:59:50
        if start_time < now < end_time - datetime.timedelta(seconds = 10):
            target_price = get_target_price(crypto_name, get_best_k())
            current_price = get_current_price(crypto_name)
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(crypto_name, krw * 0.9995)
        else:
            number_of_crypto = get_balance(crypto_name.split("-")[1])
            if number_of_crypto > 10000 / pyupbit.get_current_price(crypto_name):
                upbit.sell_market_order(crypto_name, number_of_crypto * 0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)