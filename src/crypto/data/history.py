from __future__ import annotations

"""Historical data management utilities."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiohttp
import pandas as pd
from loguru import logger


@dataclass
class OHLCVConfig:
    symbol: str
    timeframe: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    limit: int = 1000
    cache_dir: Path = Path("./data_cache")


class HistoricalDataManager:
    """Download and cache OHLCV data from WhiteBIT."""

    BASE_URL = "https://whitebit.com/api/v4/public/kline"

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def _fetch_chunk(self, cfg: OHLCVConfig, start_ts: int, end_ts: int) -> pd.DataFrame:
        params = {
            "market": cfg.symbol,
            "interval": cfg.timeframe,
            "start": start_ts,
            "end": end_ts,
            "limit": cfg.limit,
        }
        logger.debug("Fetching OHLCV chunk: %s", params)

        try:
            async with self.session.get(self.BASE_URL, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()

            if not data or not isinstance(data, list):
                logger.warning("Empty or invalid response from API")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            if df.empty:
                return df

            expected_cols = ["timestamp", "open", "high", "low", "close", "volume"]
            if len(df.columns) < len(expected_cols):
                logger.error(f"Unexpected data format: {df.columns}")
                return pd.DataFrame()

            df.columns = expected_cols[: len(df.columns)]
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
            df.set_index("timestamp", inplace=True)
            
            # Convert to numeric and handle errors
            for col in ["open", "high", "low", "close", "volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                    
            return df.dropna()
            
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return pd.DataFrame()

    async def fetch_ohlcv(self, cfg: OHLCVConfig) -> pd.DataFrame:
        """Load OHLCV data, using cached files when possible."""
        cfg.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cfg.cache_dir / f"{cfg.symbol}_{cfg.timeframe}.parquet"

        if cache_file.exists():
            logger.debug("Loading OHLCV from cache %s", cache_file)
            df = pd.read_parquet(cache_file)
        else:
            df = pd.DataFrame()

        start = cfg.start or (df.index.max().to_pydatetime() if not df.empty else None)
        end = cfg.end
        if start is None:
            start = datetime.utcnow()  # default start - no data
        if end is None:
            end = datetime.utcnow()

        if df.empty or df.index.max() < end:
            new_df = await self._fetch_chunk(cfg, int(start.timestamp()), int(end.timestamp()))
            df = pd.concat([df, new_df]).sort_index().drop_duplicates()
            if not df.empty:
                df.to_parquet(cache_file)
        return df.loc[(df.index >= start) & (df.index <= end)]
