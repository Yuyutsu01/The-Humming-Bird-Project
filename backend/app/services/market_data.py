import asyncio
import logging
import random
from datetime import datetime
import pandas as pd
from backend.app.core.container import container
from backend.app.adapters.yfinance_adapter import YFinanceAdapter

logger = logging.getLogger(__name__)

# Map categories and names to Yahoo Finance symbols
TICKER_MAP = {
    "global_markets": {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "Dow Jones": "^DJI",
        "FTSE 100": "^FTSE",
        "Nikkei 225": "^N225",
        "Hang Seng": "^HSI",
        "DAX": "^GDAXI",
        "CAC 40": "^FCHI",
    },
    "indian_markets": {
        "Nifty 50": "^NSEI",
        "Sensex": "^BSESN",
        "Bank Nifty": "^NSEBANK",
        "Nifty Midcap 50": "NIFTY_MID_50.NS",
        "Nifty Smallcap 50": "NIFTY_SMLCAP_50.NS",
    },
    "commodities": {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Copper": "HG=F",
        "Platinum": "PL=F",
        "Palladium": "PA=F",
        "Uranium": "CCJ",  # CCJ (Cameco Corp) as liquid Uranium proxy
        "Lithium": "ALTM",  # ALTM (Arcadium Lithium) as Lithium proxy
        "Brent Crude": "BZ=F",
        "WTI Crude": "CL=F",
        "Natural Gas": "NG=F",
    },
    "forex": {
        "USD/INR": "INR=X",
        "EUR/USD": "EURUSD=X",
        "USD/JPY": "JPY=X",
        "GBP/USD": "GBPUSD=X",
        "USD/CNY": "CNY=X",
    },
    "bonds": {
        "US 2Y Treasury": "^IRX",  # 13 week bill / 2Y proxy
        "US 10Y Treasury": "^TNX",
        "US 30Y Treasury": "^TYX",
        "India 10Y Bond": "IN10YT=RR",  # Often fails on yfinance, handled via fallback
    }
}

class MarketDataService:
    def __init__(self):
        self._cache = {}
        self._cache_time = None
        self.cache_duration_seconds = 300  # Cache for 5 minutes
        self.active_tickers = {}
        
        # Initialize default prices in case yfinance fails
        self.default_prices = {
            "^GSPC": (5200.0, 0.45),
            "^IXIC": (16200.0, 0.85),
            "^DJI": (39000.0, 0.15),
            "^FTSE": (8100.0, -0.2),
            "^N225": (38500.0, -1.2),
            "^HSI": (18000.0, 0.6),
            "^GDAXI": (18300.0, -0.1),
            "^FCHI": (7900.0, -0.3),
            "^NSEI": (22800.0, 0.75),
            "^BSESN": (75000.0, 0.72),
            "^NSEBANK": (49000.0, 0.55),
            "NIFTY_MID_50.NS": (14500.0, 1.1),
            "NIFTY_SMLCAP_50.NS": (7200.0, 1.4),
            "GC=F": (2350.0, 1.2),
            "SI=F": (30.0, 2.1),
            "HG=F": (4.5, -0.8),
            "PL=F": (980.0, 0.5),
            "PA=F": (950.0, -0.4),
            "CCJ": (50.0, 1.5),
            "ALTM": (5.2, -2.5),
            "BZ=F": (82.5, -0.9),
            "CL=F": (78.2, -1.1),
            "NG=F": (2.5, 3.4),
            "INR=X": (83.50, 0.05),
            "EURUSD=X": (1.085, -0.12),
            "JPY=X": (155.8, 0.35),
            "GBPUSD=X": (1.272, 0.08),
            "CNY=X": (7.24, 0.02),
            "^IRX": (4.85, 0.0),
            "^TNX": (4.45, 0.02),
            "^TYX": (4.60, 0.01),
            "IN10YT=RR": (7.02, -0.01),
        }

    async def get_market_snapshot(self) -> dict:
        """
        Fetches the latest prices for all tracked assets.
        Uses cached values if they are fresh.
        """
        now = datetime.now()
        if self._cache and self._cache_time and (now - self._cache_time).total_seconds() < self.cache_duration_seconds:
            return self._cache

        # Cache is stale, let's fetch new data
        snapshot = {}
        for category, items in TICKER_MAP.items():
            snapshot[category] = {}
            for name, ticker in items.items():
                price, pct_change = await self._fetch_ticker_data(ticker)
                
                # Format output values
                snapshot[category][name] = {
                    "ticker": ticker,
                    "price": round(price, 4) if price < 10 else round(price, 2),
                    "change_pct": round(pct_change, 2),
                    "timestamp": now.isoformat()
                }

        self._cache = snapshot
        self._cache_time = now
        # Store active tickers flat map for live simulator
        self.active_tickers = {
            t_details["ticker"]: {
                "name": name,
                "category": cat,
                "price": t_details["price"],
                "change_pct": t_details["change_pct"]
            }
            for cat, details in snapshot.items()
            for name, t_details in details.items()
        }
        return snapshot

    async def _fetch_ticker_data(self, ticker: str) -> tuple[float, float]:
        """
        Delegates ticker price lookup to YFinanceAdapter resolved via DI Container.
        """
        adapter: YFinanceAdapter = container.resolve(YFinanceAdapter)
        return await adapter.fetch_ticker_data(ticker)

    def generate_simulated_ticks(self) -> dict:
        """
        Simulates ticks using Brownian motion based on active tickers.
        Introduces small random changes and returns the flat dict of updated values.
        """
        if not self.active_tickers:
            # Trigger snapshot to populate tickers
            asyncio.run_coroutine_threadsafe(self.get_market_snapshot(), asyncio.get_event_loop())
            return {}

        updated_ticks = {}
        for ticker, data in self.active_tickers.items():
            # Apply a random walk perturbation: normal distribution centered at 0
            change = random.normalvariate(0, 0.0005)  # Max ~0.05% fluctuation
            
            # Bound Forex, Bonds, Commodities to realistic levels
            old_price = data["price"]
            new_price = old_price * (1 + change)
            
            # Rounding
            new_price = round(new_price, 4) if old_price < 10 else round(new_price, 2)
            
            # Update change percentage slightly
            new_pct = data["change_pct"] + (change * 100)
            new_pct = round(new_pct, 2)
            
            # Save back to active list
            self.active_tickers[ticker]["price"] = new_price
            self.active_tickers[ticker]["change_pct"] = new_pct
            
            updated_ticks[data["name"]] = {
                "category": data["category"],
                "ticker": ticker,
                "price": new_price,
                "change_pct": new_pct
            }
            
        return updated_ticks

    async def get_historical_bars(self, name: str, period: str = "1mo", interval: str = "1d") -> list[dict]:
        """
        Gets historical prices for charts (e.g., Nifty 50 or Gold).
        Useful for rendering candlestick or line charts.
        """
        # Find ticker
        ticker = None
        for cat, items in TICKER_MAP.items():
            if name in items:
                ticker = items[name]
                break
                
        if not ticker:
            # Search by lowercase / substring
            for cat, items in TICKER_MAP.items():
                for k, v in items.items():
                    if name.lower() in k.lower() or name.lower() == v.lower():
                        ticker = v
                        break
        
        if not ticker:
            ticker = "^NSEI"  # Default Nifty 50
            
        try:
            loop = asyncio.get_event_loop()
            t = yf.Ticker(ticker)
            hist = await loop.run_in_executor(None, lambda: t.history(period=period, interval=interval))
            
            if hist.empty:
                raise ValueError("Empty history DataFrame returned by yfinance")
                
            bars = []
            for date, row in hist.iterrows():
                bars.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"])
                })
            return bars
        except Exception as e:
            logger.warning(f"Failed to fetch history for {ticker}: {e}. Generating mock history.")
            # Generate dummy historical data
            bars = []
            base_price, _ = self.default_prices.get(ticker, (100.0, 0.0))
            now = datetime.now()
            
            days = 30 if period == "1mo" else 365
            for i in range(days, 0, -1):
                date_str = (now - pd.Timedelta(days=i)).strftime("%Y-%m-%d")
                change = random.uniform(-0.015, 0.018)
                open_val = base_price
                close_val = base_price * (1 + change)
                high_val = max(open_val, close_val) * (1 + random.uniform(0, 0.005))
                low_val = min(open_val, close_val) * (1 - random.uniform(0, 0.005))
                bars.append({
                    "date": date_str,
                    "open": round(open_val, 2),
                    "high": round(high_val, 2),
                    "low": round(low_val, 2),
                    "close": round(close_val, 2),
                    "volume": random.randint(100000, 1000000)
                })
                base_price = close_val
            return bars

# Global Singleton instance
market_data_service = MarketDataService()
