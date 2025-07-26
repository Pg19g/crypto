from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

import numpy as np
import pandas as pd
try:
    import talib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    talib = None
import talib


@dataclass
class StrategyConfig:
    rsi_period: int = 14
    galaxy_score_threshold: int = 70


class StrategyEngine:
    def __init__(self, config: StrategyConfig) -> None:
        self.config = config

    def generate_signals(self, df: pd.DataFrame, galaxy_score: float) -> Dict[str, Any]:
        close = df['close'].astype(float)
        if talib:
            rsi = talib.RSI(close, timeperiod=self.config.rsi_period)
        else:
            delta = close.diff().fillna(0)
            gain = delta.clip(lower=0).ewm(alpha=1 / self.config.rsi_period, adjust=False).mean()
            loss = (-delta.clip(upper=0)).ewm(alpha=1 / self.config.rsi_period, adjust=False).mean()
            rs = gain / loss
            rsi = 100 - 100 / (1 + rs)
        rsi = talib.RSI(close, timeperiod=self.config.rsi_period)
        last_rsi = rsi.iloc[-1]
        signal = None
        if last_rsi < 30 and galaxy_score > self.config.galaxy_score_threshold:
            signal = 'buy'
        elif last_rsi > 70:
            signal = 'sell'
        return {
            'rsi': float(last_rsi),
            'galaxy_score': galaxy_score,
            'signal': signal,
        }
