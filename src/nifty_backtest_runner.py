"""
NIFTY Auction Profile Backtest Runner

This is a simplified public research version of a NIFTY intraday backtesting runner.

The runner:
1. Loads 5-minute OHLC market data.
2. Calculates previous-day reference levels.
3. Generates simple auction-profile inspired signals.
4. Simulates end-of-day exits.
5. Saves trade results and prints summary metrics.

Disclaimer:
This project is for educational and research purposes only.
It does not provide financial advice and should not be used for live trading.
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd


# =========================
# Configuration
# =========================

DATA_FILE = "data/sample_nifty_5min.csv"
RESULT_FILE = "results/sample_backtest_results.csv"

ENTRY_TIME = "09:20"
EXIT_TIME = "15:20"

ONE_TRADE_PER_DAY = True


# =========================
# Utility Functions
# =========================

def load_market_data(file_path: str) -> pd.DataFrame:
    """
    Load NIFTY 5-minute OHLC data from CSV.

    Expected columns:
    datetime, open, high, low, close

    The datetime column should be parseable by pandas.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Data file not found: {file_path}. "
            "Please add sample_nifty_5min.csv inside the data folder."
        )

    df = pd.read_csv(file_path)

    required_columns = {"datetime", "open", "high", "low", "close"}
    missing_columns = required_columns - set(df.columns.str.lower())

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. "
            "CSV must contain datetime, open, high, low, close."
        )

    # Normalize column names to lowercase
    df.columns = [col.lower().strip() for col in df.columns]

    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = df["datetime"].dt.date
    df["time"] = df["datetime"].dt.strftime("%H:%M")

    df = df.sort_values("datetime").reset_index(drop=True)

    return df


def calculate_previous_day_levels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate previous-day reference levels.

    For each trading day, we calculate:
    - previous day high
    - previous day low
    - previous day close
    - previous day range
    """

    daily = (
        df.groupby("date")
        .agg(
            day_high=("high", "max"),
            day_low=("low", "min"),
            day_close=("close", "last"),
        )
        .reset_index()
    )

    daily["prev_day_high"] = daily["day_high"].shift(1)
    daily["prev_day_low"] = daily["day_low"].shift(1)
    daily["prev_day_close"] = daily["day_close"].shift(1)
    daily["prev_day_range"] = daily["prev_day_high"] - daily["prev_day_low"]

    df = df.merge(
        daily[
            [
                "date",
                "prev_day_high",
                "prev_day_low",
                "prev_day_close",
                "prev_day_range",
            ]
        ],
        on="date",
        how="left",
    )

    return df


def generate_signal(entry_row: pd.Series) -> str:
    """
    Generate a simple auction-profile inspired signal.

    Logic:
    - If price opens above previous-day high, consider LONG continuation.
    - If price opens below previous-day low, consider SHORT continuation.
    - If price opens inside previous-day range, return NO_TRADE.

    This is intentionally simplified for public portfolio demonstration.
    """

    open_price = entry_row["open"]
    prev_high = entry_row["prev_day_high"]
    prev_low = entry_row["prev_day_low"]

    if pd.isna(prev_high) or pd.isna(prev_low):
        return "NO_TRADE"

    if open_price > prev_high:
        return "LONG"

    if open_price < prev_low:
        return "SHORT"

    return "NO_TRADE"


def calculate_points(direction: str, entry_price: float, exit_price: float) -> float:
    """
    Calculate points gained or lost based on trade direction.
    """

    if direction == "LONG":
        return exit_price - entry_price

    if direction == "SHORT":
        return entry_price - exit_price

    return 0.0


def run_backtest(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run one-trade-per-day EOD backtest.
    """

    trades = []

    for trade_date, day_data in df.groupby("date"):
        day_data = day_data.sort_values("datetime")

        entry_candidates = day_data[day_data["time"] >= ENTRY_TIME]
        exit_candidates = day_data[day_data["time"] <= EXIT_TIME]

        if entry_candidates.empty or exit_candidates.empty:
            continue

        entry_row = entry_candidates.iloc[0]
        exit_row = exit_candidates.iloc[-1]

        signal = generate_signal(entry_row)

        if signal == "NO_TRADE":
            continue

        entry_price = float(entry_row["open"])
        exit_price = float(exit_row["close"])
        points = calculate_points(signal, entry_price, exit_price)

        trades.append(
            {
                "date": trade_date,
                "direction": signal,
                "entry_time": entry_row["time"],
                "entry_price": entry_price,
                "exit_time": exit_row["time"],
                "exit_price": exit_price,
                "points": round(points, 2),
                "result": "WIN" if points > 0 else "LOSS",
                "prev_day_high": round(float(entry_row["prev_day_high"]), 2),
                "prev_day_low": round(float(entry_row["prev_day_low"]), 2),
                "prev_day_close": round(float(entry_row["prev_day_close"]), 2),
            }
        )

        if ONE_TRADE_PER_DAY:
            continue

    return pd.DataFrame(trades)


def print_summary(trades: pd.DataFrame) -> None:
    """
    Print backtest summary metrics.
    """

    if trades.empty:
        print("No trades generated.")
        return

    total_trades = len(trades)
    winning_trades = len(trades[trades["points"] > 0])
    losing_trades = len(trades[trades["points"] <= 0])
    total_points = trades["points"].sum()
    average_points = trades["points"].mean()
    win_rate = (winning_trades / total_trades) * 100

    print("\n========== Backtest Summary ==========")
    print(f"Total Trades   : {total_trades}")
    print(f"Winning Trades : {winning_trades}")
    print(f"Losing Trades  : {losing_trades}")
    print(f"Win Rate       : {win_rate:.2f}%")
    print(f"Total Points   : {total_points:.2f}")
    print(f"Average Points : {average_points:.2f}")
    print("======================================\n")


def main() -> None:
    """
    Main execution function.
    """

    print("Loading market data...")
    df = load_market_data(DATA_FILE)

    print("Calculating previous-day levels...")
    df = calculate_previous_day_levels(df)

    print("Running backtest...")
    trades = run_backtest(df)

    Path("results").mkdir(exist_ok=True)
    trades.to_csv(RESULT_FILE, index=False)

    print(f"Trade results saved to: {RESULT_FILE}")
    print_summary(trades)


if __name__ == "__main__":
    main()
