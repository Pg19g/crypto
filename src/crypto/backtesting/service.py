from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class BacktestResult:
    sharpe: float
    max_drawdown: float
    win_rate: float


class BacktestingService:
    def run_backtest(self, strategy: str, data_path: Path) -> BacktestResult:
        # Placeholder for integration with freqtrade or backtrader
        # In a real implementation this would run the backtest and parse results
        return BacktestResult(sharpe=1.0, max_drawdown=0.1, win_rate=0.55)
