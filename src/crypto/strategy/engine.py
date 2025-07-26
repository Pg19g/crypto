from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

import numpy as np
import pandas as pd
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
