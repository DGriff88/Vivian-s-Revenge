# Monday Morning SmallCapPopStrategy

## Filter Conditions (All four must be TRUE)
1. Low Float / Small Cap
   - Float < 50M shares (or Market Cap < $1B)
   - Price range: $1 – $20

2. Fresh News Catalyst
   - SEC filing (8-K, PR, FDA approval, merger, analyst upgrade, contract win)
   - Must be within the last ≤ 48 hours

3. Former Runner
   - Stock has previously run ≥ +100% in a single day/week within past year
   - OR belongs to a "hot sector" with history of repeat runners (biotech, EV, AI small caps)

4. Unusual Volume
   - Relative Volume (RVOL) ≥ 2.0
   - Today's volume ≥ 2 × 30-day average volume

## Execution Notes
- Only consider tickers that satisfy ALL four filters
- Preferred time: Pre-market Monday (05:45 – 06:30 PT)
- Setup intent: Catch high-risk / high-reward small-cap momentum pops
- Risk management: Tight stop under VWAP or pre-market low
- Take profits fast; scale out into strength

## Output Tag
setup: "SmallCap_Pop"

---

# Monday SmallCap Pop Scan Routine

## Instructions for Bot / ChatGPT
When web access or API access is ON, run this scan:

1. **Universe**
   - U.S.-listed equities priced $1–$20
   - Market cap < $1B or float < 50M shares

2. **Catalyst Filter**
   - Pull SEC filings (8-K, PR, FDA approvals, M&A, analyst upgrades)
   - Must be ≤ 48 hours old
   - Include news headlines from major wires (Reuters, Bloomberg, PRNewswire)

3. **Former Runner Check**
   - Confirm ticker has spiked ≥ 100% intraday or intraweek within the past year
   - OR belongs to a repeat-runner sector (biotech, EV, AI small caps)

4. **Unusual Volume**
   - Relative Volume (RVOL) ≥ 2.0
   - Today's volume ≥ 2 × 30-day average volume
   - Pre-market scans acceptable if after-hours catalyst triggered

5. **Output Format**
   - JSON array of tickers that meet ALL four filters:
     {
       "ticker": "XXXX",
       "setup": "SmallCap_Pop",
       "why_now": "Meets all 4 filters: low float, fresh news catalyst, former runner, unusual volume",
       "do_not_trade_if": "VWAP lost; volume fades below avg; spreads illiquid"
     }

6. **Skip Reasons**
   - If a ticker fails, list skip_reason (e.g. "No fresh catalyst" / "RVOL <2" / "Not low float")

## Timing
- Run Sunday evening and again Monday pre-market (05:45–06:15 PT)
- Only include candidates fresh as of the last 48 hours

---

# Data Sources (Endpoints Wired)

SEC Filings (Search):
- Endpoint: https://api.sec-api.io
- Example: https://api.sec-api.io?type=8-K&timeframe=last-2-days&apikey=YOUR_SEC_API_KEY

SEC Insider Trading:
- Endpoint: https://api.sec-api.io/insider-trading
- Scope: Insider buying/selling activity for small-cap tickers

Alpha Vantage:
- Endpoint: https://mcp.alphavantage.co/mcp?apikey=YOUR_ALPHA_API_KEY
- Scope: Unusual stock/ETF volume, relative volume, momentum data
- Fields: Symbol, Price, Volume, Relative Volume, Sector

Optional: News Feeds
- PRNewswire / GlobeNewswire / Reuters APIs or RSS feeds
- Use for scanning fresh catalysts (≤48h)
