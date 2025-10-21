import os
import random
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import talib
from typing import List, Dict, Any

# --- CONFIGURATION ---
# List of symbols to scan. You can expand this based on your 'Warrior Gates' or other lists.
SCAN_UNIVERSE = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "AMD", "SPY"]

# --- DATA STRUCTURE ---
# Matches the format the frontend expects for signals
class Signal(Dict):
    id: str
    strategy: str
    symbol: str
    signal: str
    price: float
    entry: float
    target: float
    notes: str

# --- APP SETUP ---
app = FastAPI(
    title="Custom Trading Scanner API",
    description="Backend for the Intellectia Clone - runs strategies and returns signals."
)

# This is CRITICAL for the HTML file to be able to talk to the Python server.
# It allows requests from your local browser (where the HTML is running) to hit this API.
origins = [
    "http://127.0.0.1",
    "http://localhost",
    "file:///",  # Allows running the HTML file directly from your system
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Simple health check."""
    return {"status": "ok", "message": "Scanner API is running."}

# --- STRATEGY IMPLEMENTATION ---

def scan_rsi_reversal(symbol: str) -> Optional[Signal]:
    """
    Implements a simple RSI Reversal strategy:
    Buy Signal: RSI(14) crosses above 30 (oversold)
    """
    try:
        # Fetch 30 days of 1-day (1d) historical data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="30d", interval="1d")

        if df.empty:
            return None

        # 1. Calculate RSI
        df['RSI'] = talib.RSI(df['Close'], timeperiod=14)

        # 2. Check for signal on the latest, complete candle
        # We need at least two candles to check for a cross
        if len(df) < 2:
            return None

        current_close = df['Close'].iloc[-1]
        previous_rsi = df['RSI'].iloc[-2]
        current_rsi = df['RSI'].iloc[-1]
        
        # Simple Reversal Logic: Was oversold, is now moving out of oversold
        if previous_rsi <= 30 and current_rsi > 30:
            
            # --- CALCULATE ENTRY/TARGET/STOP (Placeholder for now) ---
            # Using simple, realistic placeholders based on your rules (e.g., $20-50 min profit)
            # This needs to be replaced by dynamic logic using your FVG or Zone rules
            entry_price = round(current_close * 1.002, 2)
            target_price = round(entry_price + (random.uniform(0.50, 1.50) * 1), 2) # $0.50-$1.50 gain
            
            # Create the signal object for the frontend
            return Signal(
                id=f"rsi-{symbol}-{int(time.time())}",
                strategy="RSI Reversal",
                symbol=symbol,
                signal="Buy",
                price=current_close,
                entry=entry_price,
                target=target_price,
                notes=f"RSI crossed above 30 ({round(current_rsi, 2)}) from oversold. Entry @ {entry_price}.",
            )
            
        return None

    except Exception as e:
        print(f"Error scanning {symbol}: {e}")
        return None


@app.get("/scan/rsi", response_model=List[Signal])
async def run_rsi_scan():
    """
    Endpoint to run the RSI Reversal scan across the defined universe.
    """
    print(f"Starting RSI scan on {len(SCAN_UNIVERSE)} symbols...")
    signals = []
    
    # Run the strategy on all symbols
    for symbol in SCAN_UNIVERSE:
        signal = scan_rsi_reversal(symbol)
        if signal:
            signals.append(signal)
            
    print(f"Scan complete. Found {len(signals)} signals.")
    return signals


# --- FUTURE STRATEGY SKELETON (For your next steps) ---

# @app.get("/scan/warrior_gates", response_model=List[Signal])
# async def run_warrior_gates_scan():
#     """
#     Endpoint for the Warrior 5-Gate Scan (from WARRIORGATES.md).
#     This will require a different data source (real-time pre-market data, news API).
#     """
#     # Implementation for Gate 1-5 logic goes here
#     return []

# @app.get("/scan/fvg", response_model=List[Signal])
# async def run_fvg_scan():
#     """
#     Endpoint for the FVG/100-to-1000 Strategy (from 100INTO1000.md).
#     This will require 15m/4h data and complex candle pattern recognition.
#     """
#     # Implementation for FVG trend analysis goes here
#     return []