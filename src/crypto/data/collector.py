import asyncio
from typing import Dict, Any

import aiohttp
from loguru import logger


class DataCollector:
    """Fetch market and social data asynchronously."""

    WHITEBIT_URL = "https://whitebit.com/api/v4/public/markets"
    LUNARCRUSH_URL = "https://api.lunarcrush.com/v2"

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def fetch_whitebit_markets(self) -> Dict[str, Any]:
        logger.debug("Fetching WhiteBIT markets")
        async with self.session.get(self.WHITEBIT_URL) as resp:
            return await resp.json()

    async def fetch_lunarcrush_data(self, symbol: str, api_key: str) -> Dict[str, Any]:
        logger.debug("Fetching LunarCrush data for %s", symbol)
        params = {"symbol": symbol, "key": api_key}
        async with self.session.get(f"{self.LUNARCRUSH_URL}/assets", params=params) as resp:
            return await resp.json()

    async def collect(self, symbol: str, api_key: str) -> Dict[str, Any]:
        market_task = self.fetch_whitebit_markets()
        lunar_task = self.fetch_lunarcrush_data(symbol, api_key)
        results = await asyncio.gather(market_task, lunar_task, return_exceptions=True)
        return {"markets": results[0], "lunarcrush": results[1]}
