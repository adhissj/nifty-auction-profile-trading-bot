# Architecture

## Design principle

V2.1 was created as a shadow research engine rather than a modification of V2. Its state and outputs are isolated so experimental microstructure logic cannot affect the production-oriented engine.

## Core components

### `runner_vp_oi_v21_paper.py`
Coordinates the 5-minute thesis engine, 1-minute micro observer, profile manager, rolling OI research and paper-position lifecycle. It is explicitly paper-only.

### `v21_oi_rolling.py`
Builds corrected rolling OI trajectories and persistence measures from stored snapshots instead of relying only on single-snapshot change values.

### `v21_auction_zone_memory.py`
Tracks how price interacts with objective auction/profile locations. The purpose is to distinguish a genuinely new auction from repeated failed attempts around the same region.

### `v21_expansion_observer.py`
Classifies evolving microstructure into states such as pressure, ignition, expansion, shock expansion and transition. These states are research observations, not unconditional entry signals.

### `v21_execution_engine.py`
Shadow execution logic used to study whether early micro signals, 5-minute confirmation and lifecycle checkpoints can improve entry timing without weakening the higher-level thesis.

### `v21_trade_health.py`
Evaluates whether an open research position is progressing, stalling or developing persistent contradiction.

### `greeks_oi_intelligence.py` / `greeks_candle_observer.py`
Collect and transform option-chain OI/Greeks observations into market-state features usable by the research engine.

### `vp_completed_profiles.py` / `vp_oi_strategy.py`
Provide completed profile context and shared strategy utilities used by the V2/V2.1 family.

## State isolation

V2.1 uses its own output directory for positions, decisions, market frames, micro snapshots and training features. This makes side-by-side observation possible without cross-contaminating V2 state.

## External dependency

`f3.get_fyers()` is intentionally not included. In the original environment it is the local broker/data adapter. Any compatible replacement can be used.
