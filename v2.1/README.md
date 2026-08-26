# NIFTY VP-OI V2.1 Research Engine

V2.1 is an isolated **paper/research engine** for studying NIFTY directional auction behaviour using price/volume profiles, options open interest, rolling OI trajectories and short-horizon microstructure. It runs alongside the production-oriented V2 logic without sharing position, equity, lock, decision or research state.

## What this project demonstrates

- Multi-timeframe market-state research: 5-minute thesis + 1-minute/3-minute micro context.
- Rolling OI trajectory across 15m/30m windows and broad Call-vs-Put positioning pressure.
- Auction-zone memory that tracks repeated acceptance/failure around objective profile locations.
- Expansion observer states such as pressure, ignition, expansion, shock expansion and transition.
- Trend-capture research using volume, range, path, gap, OI persistence, space and novelty.
- Trade-health research for stalled, weakening or contradictory positions.
- Strict separation between research observations and broker execution. V2.1 is paper/research only.

## Public showcase contents

The public folder contains **selected sanitized implementation modules** plus the full architecture, research-output, security and research-notes documentation. The broker-coupled orchestration runner, authentication adapter, raw snapshots, trade ledgers and runtime state are intentionally withheld because they contain operational/private context.

Published implementation examples currently include:

- `src/v21_oi_rolling.py` — causal rolling OI windows and OI velocity/acceleration research.
- `src/v21_execution_engine.py` — shadow arming and early-execution state machine.
- `src/v21_trade_health.py` — exact-strike and underlying thesis-health observer.

## Architecture

```text
Market data / broker adapter
        |
        +--> 5m NIFTY OHLC + profile context
        +--> option-chain OI / Greeks snapshots
        |
        v
Rolling OI + candle/profile observations
        |
        v
V2.1 research orchestration
        |
        +--> auction-zone memory
        +--> expansion / transition state
        +--> location / novelty research
        +--> trend-capture lane
        +--> trade-health observer
        |
        v
Paper decisions + causal research outputs
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/RESEARCH_NOTES.md`](docs/RESEARCH_NOTES.md), [`docs/OUTPUTS.md`](docs/OUTPUTS.md) and [`docs/SECURITY.md`](docs/SECURITY.md).

## Safety / scope

This is a research showcase, not financial advice and not a ready-to-run live trading product. Broker authentication code, credentials, Telegram identifiers, account information, raw live states and private research datasets are intentionally excluded.

## Configuration example

`.env.example` shows non-secret research configuration only. Real credentials should remain in a local environment or secret manager and should never be committed.

## Reproducing the architecture

To reproduce the full research environment, provide your own market-data/broker adapter, historical/live NIFTY OHLC, option-chain OI access and orchestration layer around the published modules. The public folder is intentionally designed to demonstrate the engineering and research approach without publishing private operational infrastructure.
