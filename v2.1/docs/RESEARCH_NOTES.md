# Research notes

## Why V2.1 exists

The original VP-OI engine can correctly identify directional pressure yet still react late or repeatedly re-enter a thesis after failed auction acceptance. V2.1 explores whether short-horizon OI and auction-memory information can improve timing and lifecycle decisions without weakening the 5-minute thesis.

## Current observations

- Strong movement ranking alone is not enough: a high-ranked breakout can still fail if the auction never develops sustained acceptance.
- Repeated breakout attempts around the same value region should not always be treated as independent fresh opportunities. Auction memory is intended to expose this churn.
- Micro states are best interpreted hierarchically. `IGNITION` is useful as an early warning; `EXPANSION` and `SHOCK_EXPANSION` provide stronger evidence that participation is broadening.
- A `TRANSITION` state can indicate that a move is changing phase; using it blindly as confirmation can delay entries.
- No-progress trades are a separate failure mode from hard-stop losses. A trade can remain near entry for a long time while consuming opportunity and option premium.
- The most promising timing architecture is: higher-timeframe NIFTY thesis -> early micro warning -> auction acceptance/progress -> execution.

## NIFTY50 constituent research

A separate NIFTY50 constituent collector is being studied as an index-participation layer. The current hypothesis is not to let constituent breadth replace the NIFTY trend. Instead it can describe participation inside the NIFTY structure: confirmation, pullback, broadening or contradiction.

## Limitations

- Historical intraday option OI is difficult to reconstruct perfectly; research must remain causal and must never fabricate unavailable OI.
- Paper fills and observed option quotes are not equivalent to production execution quality.
- One or a few sessions are insufficient to establish statistical robustness.
- Research states and thresholds remain experimental and should not be interpreted as a finished trading system.
