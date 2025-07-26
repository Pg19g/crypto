import asyncio
from pathlib import Path

import pandas as pd
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from crypto.strategy.engine import StrategyEngine, StrategyConfig
from crypto.backtesting.service import BacktestingService
import pytest


@pytest.mark.asyncio
async def test_full_backtest_integration():
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    prices = 100 + np.cumsum(np.random.randn(100) * 0.01)
    df = pd.DataFrame({
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)

    config = StrategyConfig(rsi_period=14, galaxy_score_threshold=70)
    engine = StrategyEngine(config)
    backtester = BacktestingService(fee=0.001, slippage=0.0005)

    result = backtester.run_backtest(df, engine, galaxy_score=75.0)

    assert isinstance(result.sharpe, float)
    assert isinstance(result.total_return, float)
    assert len(result.equity_curve) == len(df) - config.rsi_period
    assert 0 <= result.win_rate <= 1
