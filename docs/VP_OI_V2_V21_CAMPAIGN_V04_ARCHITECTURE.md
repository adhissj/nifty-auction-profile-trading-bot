# VP–OI V2 / V2.1 / Campaign V0.4 Architecture

> Status: research / paper-trading architecture  
> Last updated: 8 September 2026  
> Scope: NIFTY intraday VP–OI ensemble and Campaign V0.4 supervisory layer

## 1. Purpose

The system is split into three decision layers:

1. **V2** — primary VP–OI signal engine.
2. **V2.1** — enhanced VP–OI engine with additional microstructure context.
3. **Campaign V0.4** — supervisory ensemble that decides whether a candidate should become a trade and how an open trade should be managed.

The design goal is to avoid treating one signal engine as the final authority. V2 and V2.1 generate local trading evidence; Campaign V0.4 combines that evidence with market regime, OI, auction context, price acceptance and order flow before taking or exiting a trade.

---

## 2. High-level flow

```text
                    MARKET DATA
                         |
        +----------------+----------------+
        |                                 |
   NIFTY 5m OHLC                     Options / OI
        |                                 |
        +----------------+----------------+
                         |
              +----------+----------+
              |                     |
             V2                   V2.1
              |                     |
              | candidate signals   |
              +----------+----------+
                         |
                         v
                CAMPAIGN V0.4
                         |
       +-----------------+------------------+
       |                                    |
 Entry Arbitration                    Trade Management
       |                                    |
 Regime + OI +                     Trend Health warning
 price acceptance                       |
 + engine agreement                     v
       |                          CVD / Order Flow Arbiter
       v                                    |
 Option execution                 Hold / Watch / Exit
```

---

## 3. Core data inputs

### Price / auction data

- NIFTY 5-minute OHLCV
- previous-day profile references
- previous-week profile references
- developing intraday market-profile levels
- swing / structural references
- current auction state

Typical auction states:

- `BULLISH`
- `BEARISH`
- `BALANCED`

### Options / OI data

The engines use rolling OI context such as:

- immediate OI bias
- 15-minute OI score
- 30-minute OI score
- fresh positioning
- broad unwinding
- call / put OI changes
- premium response around ATM

OI is treated as **confirmation**, not as the sole regime detector.

### Microstructure

V2.1 additionally uses 1-minute / 3-minute microstructure observations such as:

- short-term directional persistence
- balance noise
- bullish expansion
- bearish expansion
- transitions
- price / premium effectiveness

### Futures order flow

Campaign trade management can consume futures order-flow / CVD features:

- executed delta / CVD direction
- aggressive buying vs aggressive selling
- 5-minute flow state
- 15-minute persistence
- price response to aggressive flow
- flow effectiveness

Only completed bars may be used. The system must never use the final state of a still-forming candle.

---

## 4. V2 architecture

V2 is the main VP–OI signal engine.

Its job is to answer:

> Is there a locally valid directional opportunity right now?

### V2 processing stages

```text
NIFTY / option data
      |
      v
Location and profile context
      |
      v
Price-event classification
      |
      v
OI interpretation
      |
      v
Trend-candidate scoring
      |
      v
ENTER / HOLD / EXIT evidence
```

Important signal concepts include:

- bullish breakout
- bearish breakdown
- failed breakout
- failed breakdown
- profile / location context
- trend-capture qualification

The engine calculates quality features such as:

- efficiency rank
- volume rank
- range rank
- path rank
- gap rank
- distance / space to checkpoints

### Trend Capture

For Campaign V0.4, the highest-priority V2 signal type is `TREND_CAPTURE`.

A Trend Capture candidate represents a stronger directional continuation setup than a generic contextual entry.

Campaign should not blindly inherit every normal V2 entry. The current ensemble design gives priority to qualified Trend Capture signals.

---

## 5. V2.1 architecture

V2.1 uses the same broad VP–OI framework as V2, but adds a microstructure layer.

Its role is:

> Confirm or challenge the V2 interpretation using shorter-horizon market behaviour.

Examples of V2.1 micro states:

- `BULLISH_EXPANSION`
- `BEARISH_EXPANSION`
- `TRANSITION`
- `BALANCE_NOISE`

V2.1 can therefore distinguish between:

- a structurally good setup with supporting short-term flow,
- a structurally good setup occurring in noisy microstructure,
- and a setup whose short-horizon behaviour is already contradicting it.

Campaign does not simply rank V2.1 above V2 in every case. Instead, agreement between both engines is treated as stronger evidence than a single-engine signal.

---

## 6. Campaign V0.4 entry architecture

Campaign V0.4 is the decision brain.

V2 and V2.1 are **candidate providers**.

Campaign decides:

1. whether the current market regime permits the trade,
2. whether OI confirms the direction,
3. whether price accepts the move,
4. whether the second engine reinforces or contradicts the candidate,
5. whether execution is allowed.

### 6.1 Regime

The Campaign regime framework is intentionally simple:

- `TRENDING_BULL`
- `TRENDING_BEAR`
- `FLAT`
- `UNKNOWN`

In a trending regime, Campaign prefers Trend Capture signals aligned with the dominant direction.

In a flat regime, range / profile-extreme logic is conceptually different and should not be mixed with trend-continuation logic.

### 6.2 Dual-engine confirmation

If V2 and V2.1 produce the same-direction candidate within the configured confirmation window:

```text
V2 PE candidate
      +
V2.1 PE candidate
      |
      v
DUAL_ENGINE_CONFIRM
```

This can release a candidate quickly when higher-level alignment is not contradictory.

### 6.3 Single-engine candidate

If only one engine fires, Campaign keeps the candidate pending and waits for directional price acceptance.

```text
Single-engine candidate
        |
        v
Pending state
        |
        v
5m price acceptance
        |
   +----+----+
   |         |
accept     reject
   |         |
 trade      drop
```

### 6.4 Contradiction

Campaign can reject or delay entries when higher-level evidence is contradictory.

Examples:

- auction opposes signal
- Top-5 contribution strongly opposes signal
- OI15 / OI30 oppose the proposed direction
- opposite engine evidence appears
- price acceptance fails

A strong contradiction should not be overridden merely because one local engine generated a candidate.

---

## 7. Entry hierarchy

The intended hierarchy is:

```text
1. Regime
2. Location / auction context
3. V2 / V2.1 Trend Capture candidate
4. OI confirmation
5. Price acceptance
6. Option execution
```

This ordering matters.

OI does not define the regime.  
A signal does not override the regime.  
Option execution occurs only after the directional thesis is accepted.

---

## 8. Campaign V0.4 trade-management architecture

The current exit architecture separates **warnings** from **exit authority**.

This is a key design choice.

### 8.1 Trend Health

Trend Health evaluates:

- price progress
- OI behaviour
- volume / efficiency
- auction context
- short-horizon microstructure

Trend Health can classify a trade as weakening or exhausted.

However:

> **Trend Health is now a warning generator, not a standalone soft-exit authority.**

This avoids premature exits caused by one temporary deterioration signal.

### 8.2 Exit Arbiter V1

The frozen research architecture is:

```text
Trend Health warning
        |
        v
5m CVD / order flow
        |
        v
15m persistence
        |
        v
Price effectiveness
        |
        v
Auction + OI + price acceptance
        |
   +----+----+
   |         |
control     no control
flipped     flip
   |         |
 EXIT       HOLD
```

The intended trade states are:

- `HEALTHY`
- `WATCH`
- `DETERIORATING`
- `REVERSED`

### HEALTHY

Flow, OI and price action remain compatible with the open position.

Action: **HOLD**

### WATCH

Opposite 5-minute flow appears or Trend Health raises a soft warning.

Action: **Do not exit yet.**

### DETERIORATING

Opposite flow persists across the completed 15-minute context and starts becoming effective.

Action: intensify monitoring.

### REVERSED

A genuine control change requires several layers to agree.

Typical evidence:

- persistent opposite CVD / order flow
- opposite auction / regime
- opposite OI confirmation
- adverse price progress / price acceptance

Action: **EXIT**

---

## 9. Order-flow effectiveness

Direction alone is not enough.

Example for an open PE:

```text
Aggressive buyers appear
        |
        v
Does price actually rise?
        |
   +----+----+
   |         |
  yes        no
   |         |
warning   buying absorbed /
stronger   ineffective
```

Therefore:

- rising CVD + rising price = buyers effective
- rising CVD + flat / falling price = buyers ineffective / possible absorption
- falling CVD + falling price = sellers effective
- falling CVD + flat / rising price = sellers ineffective / possible absorption

This distinction prevents the system from exiting merely because counter-aggression appeared.

---

## 10. Multi-timeframe timing rule

The order-flow layer must be causal.

Example:

- 12:45–13:00 order-flow candle closes at 13:00
- it may be used at 13:00, 13:05 and 13:10
- at 13:15, replace it with the newly completed 13:00–13:15 block

Never use a still-forming 15-minute candle's final CVD value.

---

## 11. Hard exits vs soft exits

### Hard exits

Hard safety exits remain authoritative and can bypass the soft arbiter.

Examples:

- catastrophic premium stop
- structural invalidation
- forced / operational exit
- time exit
- confirmed regime reversal with strong supporting evidence

### Soft exits

Examples:

- Trend Health exhaustion
- checkpoint rejection
- temporary adverse microstructure
- one opposite flow candle

These should normally enter `WATCH` or `DETERIORATING`, not immediately close the position.

---

## 12. Sep 8, 2026 research example

A Campaign PE trade entered around 13:30 and was originally closed by `TREND_HEALTH_EXHAUSTED_2X` around 13:56.

Immediately before that exit, futures order flow still showed strong sell aggression.

Under the Exit Arbiter architecture:

```text
Trend Health warning
        +
strong bearish order flow
        +
bearish auction context
        |
        v
       HOLD
```

Later bullish counterflow raised a warning, but it did not immediately prove that market control had changed.

The example motivated the architectural change, but it is **not sufficient validation by itself**.

---

## 13. Overfitting control

Historical CVD / executed order-flow coverage is currently limited.

Therefore the exit architecture must be treated as a frozen hypothesis and forward-tested.

Rules:

- do not tune thresholds after every trade,
- record every warning and arbiter decision,
- preserve causal bar timing,
- compare new exit vs existing exit in shadow mode,
- keep the rule hierarchy fixed for a meaningful forward sample.

Recommended validation window:

- at least 20–30 complete trading sessions for an initial read,
- preferably 30–60 sessions before production promotion.

Metrics to compare:

- net P&L
- profit factor
- maximum drawdown
- MFE capture ratio
- giveback from MFE
- premature exits prevented
- losers held too long
- average hold time
- per-regime performance

---

## 14. Research / live separation

The safest deployment pattern is:

```text
V2             -> paper / local evidence
V2.1           -> paper / local evidence
Campaign V0.4  -> paper ensemble
Exit Arbiter   -> shadow first
```

A new component should not replace the baseline merely because it improves a few hand-selected sessions.

---

## 15. Operational components

A typical deployment contains:

- V2 runner
- V2.1 runner
- Campaign V0.4 runner
- NIFTY / option-data collectors
- OI snapshot collector
- futures order-flow collector
- paper-trade ledgers
- event / audit logs
- PM2 process manager

Recommended operational rule:

- start trading services before market observation begins,
- stop trading PM2 processes after market hours,
- preserve logs and research data for replay.

Secrets, broker tokens and account credentials must never be committed to GitHub.

---

## 16. Architecture summary

```text
                 +-----------------------+
                 |   NIFTY / OPTIONS / OI|
                 +-----------+-----------+
                             |
                  +----------+----------+
                  |                     |
                 V2                   V2.1
          VP-OI local engine    VP-OI + micro layer
                  |                     |
                  +----------+----------+
                             |
                             v
                   CAMPAIGN V0.4
                   Supervisory Brain
                             |
          +------------------+------------------+
          |                                     |
   ENTRY ARBITER                         EXIT ARBITER V1
          |                                     |
Regime -> TC -> OI ->                 Trend Health warning
price acceptance -> execution                  |
                                                v
                                  5m CVD / order-flow warning
                                                |
                                                v
                                    completed 15m persistence
                                                |
                                                v
                                   price-flow effectiveness
                                                |
                                                v
                                  auction + OI + acceptance
                                                |
                                      HOLD / WATCH / EXIT
```

The main architectural principle is:

> **V2 and V2.1 discover opportunities. Campaign V0.4 decides whether the market context justifies acting on them. Once in a trade, Trend Health detects deterioration, while CVD, order-flow effectiveness, auction context, OI and price acceptance determine whether market control has truly changed.**

---

## Disclaimer

This architecture is for research and paper-trading purposes. It is not financial advice and is not considered production-validated until it has passed sufficient out-of-sample and forward testing.
