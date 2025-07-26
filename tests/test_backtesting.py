import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from crypto.backtesting.service import BacktestingService


class DummyEngine:
    def __init__(self, signals):
        self.signals = signals

    def generate_signals(self, df: pd.DataFrame, galaxy_score: float):
        idx = len(df) - 1
        return {"signal": self.signals[idx]}


def test_backtest_basic():
    prices = [100, 105, 110, 108, 120]
    df = pd.DataFrame({"close": prices}, index=pd.date_range("2024-01-01", periods=len(prices)))
    engine = DummyEngine(["buy", None, "sell", "buy", "sell"])
    service = BacktestingService(fee=0.0, slippage=0.0)
    result = service.run_backtest(df, engine)
    assert result.total_return != 0
    assert len(result.trades) == 2
