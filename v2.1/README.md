# NIFTY VP-OI V2.1 Research Engine

V2.1 is an isolated **paper/research engine** for studying NIFTY directional auction behaviour using price/volume profiles, options open interest, rolling OI trajectories and short-horizon microstructure. It runs alongside the production-oriented V2 logic without sharing position, equity, lock, decision or research state.

## What this project demonstrates

- Multi-timeframe market-state research: 5-minute thesis + 1-minute/3-minute micro context.
- Rolling OI trajectory across 15m/30m windows and broad Call-vs-Put positioning pressure.
- Auction-zone memory that tracks repeated acceptance/failure around objective profile locations.
- Expansion observer that distinguishes pressure, ignition, expansion, shock expansion and transition states.
- Trend-capture candidate ranking using volume, range, path, gap, OI persistence, space and novelty.
- Trade-health observer for checkpoint-aware protection and stalled/contradictory trade research.
- Strict separation between research observations and broker execution. V2.1 never sends live orders.

## Architecture

```text
Market data / broker adapter
        |
        +--> 5m NIFTY OHLC + profile context
        +--> option-chain OI / Greeks snapshots
        |
        v
Rolling OI + candle observer + completed profiles
        |
        v
V2.1 research runner
        |
        +--> auction-zone memory
        +--> expansion observer
        +--> location/novelty research
        +--> trend-capture lane
        +--> trade-health observer
        |
        v
Paper decisions + research JSONL/CSV outputs
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the component-level design and [`docs/RESEARCH_NOTES.md`](docs/RESEARCH_NOTES.md) for current findings and limitations.

## Safety / scope

This repository is a research showcase, not financial advice and not a ready-to-run live trading product. Broker authentication code, credentials, Telegram identifiers, account information, raw live states and private research datasets are intentionally excluded.

## Running locally

1. Create a virtual environment and install `requirements.txt`.
2. Copy `.env.example` to `.env`.
3. Provide your own `f3.get_fyers()` compatible broker/data adapter, or replace that import with your own market-data client.
4. Provide historical/live NIFTY OHLC and option-chain access.
5. Run `python src/runner_vp_oi_v21_paper.py`.

The runner writes research artifacts under `v21_research/`, which is ignored by Git.
