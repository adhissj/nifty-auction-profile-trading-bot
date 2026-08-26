# NIFTY Auction Profile Trading Bot

This project is an AI-assisted Python research and backtesting framework for NIFTY intraday trading strategies.

The system uses sample 5-minute OHLC market data, previous-day reference levels, auction-profile inspired signal logic, and end-of-day exit simulation to understand how a trading idea can be converted into a structured backtesting workflow.

## V2.1 research showcase

A newer research branch of the project is documented under [`v2.1/`](v2.1/README.md).

V2.1 explores a more advanced NIFTY VP-OI architecture with:

* 5-minute thesis + 1-minute/3-minute microstructure research
* rolling 15m/30m options OI trajectories
* auction-zone memory for repeated acceptance/failure
* pressure, ignition, expansion and shock-expansion states
* early-execution shadow arming
* trade-health and no-progress/contradiction research
* isolated paper state so experiments cannot affect the production-oriented V2 engine

The public V2.1 showcase is intentionally sanitized: broker authentication, credentials, Telegram identifiers, account information, raw live state, private datasets and execution ledgers are excluded.

## Features

* NIFTY 5-minute OHLC data processing
* Previous-day reference level calculation
* Auction-profile inspired signal generation
* LONG / SHORT / NO TRADE decision engine
* End-of-day exit simulation
* Trade result generation
* Backtest summary with points, win rate, and trade count
* Single-file runner for easier understanding and explanation
* Simple configuration section inside the runner file

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
└── v2.1/
    ├── README.md
    ├── docs/
    └── src/
```

## How It Works

1. Load NIFTY 5-minute OHLC data.
2. Prepare date and time columns.
3. Calculate previous-day reference levels.
4. Generate LONG, SHORT, or NO TRADE signals.
5. Simulate entry and end-of-day exit.
6. Save trade results.
7. Generate performance summary.

## Strategy Logic

The first public version uses a simple auction-profile inspired logic.

The runner checks how the current trading day behaves around previous-day reference levels such as:

* Previous day high
* Previous day low
* Previous day close
* Previous day range

Based on the price action around these levels, the system generates a sample trading signal:

* If price opens above the previous-day high, the system considers a LONG continuation signal.
* If price opens below the previous-day low, the system considers a SHORT continuation signal.
* If price opens inside the previous-day range, the system returns NO TRADE.

The trade is exited at the configured end-of-day exit time.

## Sample Output Metrics

The backtest runner generates metrics such as:

* Total trades
* Winning trades
* Losing trades
* Win rate
* Total points
* Average points per trade

## Tech Stack

* Python
* Pandas
* NumPy
* CSV-based market data

## How to Run

1. Clone the repository:

```bash
git clone https://github.com/adhissj/nifty-auction-profile-trading-bot.git
```

2. Move into the project folder:

```bash
cd nifty-auction-profile-trading-bot
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the backtest runner:

```bash
python src/nifty_backtest_runner.py
```

5. Check the generated output:

```text
results/sample_backtest_results.csv
```

## Sample Input and Output

This repository includes a small sample dataset:

```text
data/sample_nifty_5min.csv
```

The runner processes this file and generates a sample backtest result:

```text
results/sample_backtest_results.csv
```

## Why I Built This

I built this project as an AI-assisted learning project to understand how a trading idea can be converted into a structured Python-based backtesting workflow.

I used AI support to help generate and organize the initial code. My focus was to understand the project flow, maintain the repository, document the logic, and learn how each part of the system works step by step.

This project helped me get exposure to:

* How a Python project is organized
* How CSV market data can be processed
* How a simple backtesting flow works
* How trading rules can be converted into code
* How output results can be stored and reviewed

The main flow of the first public version is:

```text
CSV data → previous-day levels → signal generation → entry → EOD exit → result CSV
```

The V2.1 research showcase extends that learning into multi-timeframe auction/OI state, causal research logging and isolated paper-trading architecture.

## Future Improvements

Planned improvements include:

* Add more detailed strategy rules
* Add configurable risk management
* Add visual backtest reports
* Add paper trading mode
* Add Docker setup
* Add cloud deployment notes
* Continue validating V2.1 timing and auction-acceptance research on more sessions

## Disclaimer

This project is for educational and research purposes only.

It does not provide financial advice and should not be used for live trading without proper testing and risk management.
