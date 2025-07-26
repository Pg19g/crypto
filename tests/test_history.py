import sys
import pandas as pd
import pytest
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from crypto.data.history import HistoricalDataManager, OHLCVConfig


@pytest.mark.asyncio
async def test_history_cache(tmp_path, monkeypatch):
    df_stub = pd.DataFrame(
        {
            "open": [1, 2],
            "high": [2, 3],
            "low": [0.5, 1.5],
            "close": [1.5, 2.5],
            "volume": [100, 200],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    async def fake_fetch(self, cfg, start_ts, end_ts):
        return df_stub

    async with asyncio.timeout(5):
        async with __import__("aiohttp").ClientSession() as session:
            mgr = HistoricalDataManager(session)
            monkeypatch.setattr(mgr, "_fetch_chunk", fake_fetch)
            cfg = OHLCVConfig(symbol="BTC_USDT", timeframe="1d", cache_dir=tmp_path)
            df = await mgr.fetch_ohlcv(cfg)
            assert not df.empty
            # second call should hit cache
            df2 = await mgr.fetch_ohlcv(cfg)
            pd.testing.assert_frame_equal(df, df2)
