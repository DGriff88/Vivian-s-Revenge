# SCANNER LOGIC #

## THIS IS A MARKET WIDE PRO ACTIVE SCANNER ##

### DO NOT SCAN SPECIFIC TICKERS ONLY ###

### THIS FILE DEFINES A MARKET-WIDE DAILY SCANNER ###

The goal is to discover candidate tickers via: 

##SEC filings##

(Priority forms to monitor)----DEF 14A / DFAN14A / 14A — proxy/solicitation

(activist/control moves)---10-Q / 10-K — guidance, going-concern, liquidity

---- Form 4 / 3 / 5 — insider buys/sells

---- Schedule 13D / 13G — >5% ownership alerts

---- Form 13F — institutional interest (quarterly)

---- S-1 / S-3 / S-4 / 424(b) — offerings, dilution, shelf registrations

---- N-PORT / N-CSR — fund holdings (useful for income/fund plays)

---- Form D — private placements / PIPE activity

---- Form 6-K — major foreign issuer disclosures

---- Form 144 — restricted holdings sales intent)


### Keyword watchlist ###(flag inside filings)###

solicit |proxy |proxy contest |recommendation |merger |asset sale |spin-off |bankruptcy |restructuring |going concern |liquidity |shelf registration |prospectus |beneficial ownership |insider purchase |notice of delisting |redemption |portfolio  holdings |net asset value |covenant  default

### OPTIONAL (SEC_EDGAR_API) = 2ecd00df7e07a338e2f8eb3826e6449358f6d42b0f38491a38f808f7a5a3e239

**Endpoints to query:**

   https://api.sec-api.io/insider-trading
   https://data.sec.gov/submissions/CIK{CIK}.json
   https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json  
   https://data.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&owner=include&type=&output=json

**Look for:**

- `Form 4` → filter for `transactionCode: P` (Purchase), `transactionShares` ≥ 10,000
- `8-K` → flag sections containing:
  - Item 1.01 (Material Agreements)
  - Item 5.02 (Leadership changes)
  - Item 8.01 (Other important events)
- `13D`, `13G` → New stakes or activist moves

**If no API key is present**, fallback to scraping `https://www.sec.gov/edgar/searchedgar/currentevents`.

SCHWAB API =  GYrJyAw6IMCerLnnk0aZJpC9W4uSP8vc

SECRET= 1oyHXh9bNnU67bxr

CLIENT_ID: fcrJyAVeSMcertLmk6OaZjpCzW4uSPbxc

CLIENT_SECRET: 1oyHOf59bNk1U67bxr

REDIRECT_URL: https://127.0.0.1:8080/callback

BASE_URL: https://api.schwabapi.com




Unusual options activity (UOA)

Insider buys/sells

News catalysts before they’re widely known

Use these to generate a list of potential tickers

Then apply Rules.md to filter those tickers

Then apply the Gates (1–4) to rank their trade readiness




## Universe
- U.S.-listed equities with:
  - Price $10–$150
  - Market cap ≥ $1B
  - Avg daily stock volume ≥ 2M shares
  - Options: OI ≥ 1,000 per strike; bid/ask spread ≤ $0.20


## Sessions
- 06:10–06:25 PT: Pre-open prep
- 06:30–07:30 PT: First hour
- 12:00–13:00 PT: Last hour
- Midday scan optional (only if A+ setup)

## Freshness & Drift Filters
- Catalyst ≤ 4h old (PR, FDA, SEC filing, guidance, earnings, activism, unusual options flow)
- AH pop ≤ +10% unless:
  - RVOL still rising, AND
  - Price pulled back to VWAP/21EMA
- RVOL ≥ 1.5 and rising
- Not extended (last_price ≤ first_candle_high OR pullback to VWAP/21EMA)

> Any ticker failing these filters = dropped 

## Four Gates (Options Focus)
1. **Catalyst + Freshness**
   - SEC/PR/FDA/UOA skew/headlines
   - Must pass freshness filters
2. **Alignment**
   - 50 EMA slope in trade direction
   - Price near 21EMA/VWAP with 9 curling
3. **Momentum**
   - 2 of 3: RSI, Stoch, MACD confirm
4. **Profit Math (Options)**
   - Debit/credit spread risk ≤ $80
   - R:R ≥ 1:1 (prefer ≥ 1:2)
   - Daily max loss −$240; walk at +$200 or 3 red trades


## SCANNER ENGINE: What to Scan, Where, and Why

This scan SHOULD be run **after midnight Pacific Time (00:00 PT)** to capture global catalysts and overnight developments.OR PRE MARKET
 
It defines a **market-wide screener** — not a ticker-specific query. Focus only on **fresh, actionable leads.**

---

### ✅ SEC FILINGS (Material Events) SEC_EDGAR_API = 2ecd00df7e07a338e2f8eb3826e6449358f6d42b0f38491a38f808f7a5a3e239

**Scan:**

- [SEC EDGAR Current Filings](https://www.sec.gov/edgar/searchedgar/currentevents)
- Look for: `14A`, `DEF 14A`, `PREC14A`, `8-K`, `SC 13D/G`, `Form 4`
- Focus on:
  - Insider buys (not sales)
  - New M&A filings, board changes, proxy votes
  - Offerings, dilutions, SPAC deals
- Prioritize filings timestamped **in the past 24 hours**

---

### ✅ UNUSUAL OPTIONS ACTIVITY (UOA)

**Scan:**

- [Barchart UOA](https://www.barchart.com/options/unusual-activity)
- [OptionCharts](https://optioncharts.io/trending/unusual-options-activity-stock-contracts)

**Trigger filters:**
- Volume / Open Interest ratio > 3.0
- IV spike > 25%
- Total $flow > $200K
- Contract strike near ATM or recent range breakout

---

### ✅ UNUSUAL VOLUME + FLOAT ROTATION

**Scan:**

- [TradingView Unusual Volume Screener](https://www.tradingview.com/markets/stocks-usa/market-movers-unusual-volume)

**Filters:**
- Relative Volume (RVOL) > 3.0
- Current Day Volume > Float
- Breakout candle above EMA or range high

---

### ✅ NEWS CATALYSTS (OPTIONAL WITH RSS OR API)

- If enabled, scan for:

  - Press releases, FDA decisions, lawsuits, upgrades/downgrades
  - Prefer sources: PRNewswire, GlobeNewswire, Bloomberg headlines
- Trigger rules:
  - News under 4h old
  - Matches with price + volume move

---

### ✅ INSIDER BUYS (Optional — Based on Form 4)

**Scan:**

- Form 4 database / EDGAR
- Flag insider buys ≥ $100K
- Ignore Form 4 sales unless part of M&A exit

---

## POST-SCAN FLOW

After candidates are collected:

1. Run all tickers through `RULES.md`

2. If they pass, run through `GATES.md`

3. Only tickers that pass **3 of 4 Gates** are considered tradeable

---

## NOTES

- ##DO NOT HALUICINATE TICKERS##s — ONLY use results from LIVE data

- Skip any ticker with stale news (older than 24h) unless it's in follow-through phase

- Output should include:
  - `Ticker`
  - `Catalyst`
  - `Source`
  - `Volume/OI ratio`
  - `RVOL`
  - `Time found`

