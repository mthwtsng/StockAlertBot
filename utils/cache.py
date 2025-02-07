# utils/cache.py
import time
import asyncio
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

class PriceCache:
    def __init__(self, ttl: int = 30):
        self.ttl = ttl
        self.cache = {}

    async def get_price(self, ticker: str):
        ticker = ticker.upper()
        now = time.time()
        if ticker in self.cache:
            cached_time, price = self.cache[ticker]
            if now - cached_time < self.ttl:
                return price

        price = await asyncio.to_thread(self.fetch_price, ticker)
        if price is not None:
            self.cache[ticker] = (now, price)
        return price

    def fetch_price(self, ticker: str):
        try:
            info = yf.Ticker(ticker).info
            return info.get("regularMarketPrice", None)
        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {e}")
            return None
