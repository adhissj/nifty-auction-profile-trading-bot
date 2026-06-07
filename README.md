# NIFTY Auction Profile Trading Bot

This project is a Python-based research and backtesting framework for NIFTY intraday trading strategies.

The system uses 5-minute OHLC market data, previous-day reference levels, auction profile concepts, signal generation rules, and risk management logic to simulate trades and evaluate strategy performance.

## Features

- NIFTY 5-minute OHLC data processing
- Previous-day reference level calculation
- Auction profile based signal generation
- LONG / SHORT / NO TRADE decision engine
- End-of-day exit simulation
- Trade log generation
- Backtest summary with points, win rate, and trade count
- Single-file runner for easier understanding and interview explanation
- Simple configuration section inside the runner file

## Project Structure

```text
nifty-auction-profile-trading-bot/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── sample_nifty_5min.csv
│
├── src/
│   └── nifty_backtest_runner.py
│
├── results/
│   └── sample_backtest_results.csv
│
└── docs/
    ├── strategy_overview.md
    
