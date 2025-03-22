# app/strategy.py

import pandas as pd
from typing import List, Dict

def calculate_moving_averages(
    records: List[Dict],
    short_window: int = 10,
    long_window: int = 30
):
    """
    Calculates short & long moving averages using 'close' prices.
    Expects a list of dicts with 'datetime' and 'close'.
    """
    df = pd.DataFrame(records)
    df.sort_values(by='datetime', inplace=True)

    # Calculate rolling means
    df['ma_short'] = df['close'].rolling(window=short_window).mean()
    df['ma_long'] = df['close'].rolling(window=long_window).mean()

    return df

def moving_average_crossover_strategy(df: pd.DataFrame):
    """
    Generates buy/sell signals when ma_short crosses ma_long.
    """
    df['signal'] = 0
    df['signal'] = (df['ma_short'] > df['ma_long']).astype(int)
    df['positions'] = df['signal'].diff()

    signals = []
    for _, row in df.iterrows():
        if row['positions'] == 1:
            signals.append((row['datetime'], 'BUY'))
        elif row['positions'] == -1:
            signals.append((row['datetime'], 'SELL'))
    return signals

def evaluate_strategy_performance(df: pd.DataFrame, signals: list) -> dict:
    """
    Simple performance metric:
    1. Count total buys & sells
    2. Estimate profit as difference from first BUY close to last SELL close
    """
    total_buys = sum(s[1] == 'BUY' for s in signals)
    total_sells = sum(s[1] == 'SELL' for s in signals)

    if total_buys == 0 or total_sells == 0:
        return {
            "total_buys": total_buys,
            "total_sells": total_sells,
            "profit_estimate": 0.0,
            "comment": "Not enough signals to compute PnL"
        }

    # find first BUY
    first_buy = next((s for s in signals if s[1] == 'BUY'), None)
    # find last SELL
    last_sell = next((s for s in reversed(signals) if s[1] == 'SELL'), None)

    if not first_buy or not last_sell:
        return {
            "total_buys": total_buys,
            "total_sells": total_sells,
            "profit_estimate": 0.0,
            "comment": "No final SELL signal found"
        }

    first_buy_close = df.loc[df['datetime'] == first_buy[0], 'close'].iloc[0]
    last_sell_close = df.loc[df['datetime'] == last_sell[0], 'close'].iloc[0]
    profit_estimate = last_sell_close - first_buy_close

    return {
        "total_buys": total_buys,
        "total_sells": total_sells,
        "profit_estimate": float(profit_estimate),
        "comment": "Naive performance metric"
    }
