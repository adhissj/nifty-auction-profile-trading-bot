# Research outputs

The runner can generate the following classes of artifacts locally. They are ignored in the public repository because they can contain private market/account context or become very large.

- 5-minute and 1-minute OHLC caches
- OI/Greeks snapshots and contract observations
- paper decisions and paper trades
- market frames and frozen profile state
- micro-story observations
- enhanced V2.1 research observations
- trade-health and shadow-execution state
- training-feature CSV files for later ML research

Example trend-candidate fields include:

```text
event, eff_rank, vol_rank, range_rank, path_rank, gap_rank,
immediate_flow, oi15, oi30, space, location, novelty, micro_state
```

These fields are designed to preserve *why* a candidate existed so later analysis can distinguish directional strength from auction acceptance and execution timing.
