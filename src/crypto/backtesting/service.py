from __future__ import annotations

"""Simple backtesting engine."""

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    profit_pct: float


@dataclass
class BacktestResult:
    sharpe: float
    max_drawdown: float
    win_rate: float
    total_return: float
    volatility: float
    calmar_ratio: float
    trades: List[Trade]
    equity_curve: pd.Series


class BacktestingService:
    def __init__(self, fee: float = 0.001, slippage: float = 0.0005) -> None:
        self.fee = fee
        self.slippage = slippage

    def run_backtest(
        self,
        df: pd.DataFrame,
        engine,
        galaxy_score: float = 0.0,
        initial_balance: float = 1000.0,
    ) -> BacktestResult:
        """Run backtest on dataframe using a strategy engine."""
        balance = initial_balance
        position = 0.0
        entry_price = 0.0
        equity_curve = []
        trades: List[Trade] = []

        for idx, row in df.iterrows():
            signal_data = engine.generate_signals(df.loc[:idx], galaxy_score)
            price = float(row["close"])

            if signal_data["signal"] == "buy" and position == 0:
                entry_price = price * (1 + self.slippage)
                position = balance / entry_price
                balance -= position * entry_price * (1 + self.fee)
                entry_time = idx
            elif signal_data["signal"] == "sell" and position > 0:
                exit_price = price * (1 - self.slippage)
                balance += position * exit_price * (1 - self.fee)
                profit_pct = (exit_price - entry_price) / entry_price
                trades.append(
                    Trade(
                        entry_time=entry_time,
                        exit_time=idx,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        profit_pct=profit_pct,
                    )
                )
                position = 0.0
            equity = balance + position * price
            equity_curve.append(equity)

        if position > 0:
            exit_price = float(df.iloc[-1]["close"])
            balance += position * exit_price * (1 - self.fee)
            profit_pct = (exit_price - entry_price) / entry_price
            trades.append(
                Trade(
                    entry_time=entry_time,
                    exit_time=df.index[-1],
                    entry_price=entry_price,
                    exit_price=exit_price,
                    profit_pct=profit_pct,
                )
            )
            position = 0.0
            equity_curve[-1] = balance

        equity_series = pd.Series(equity_curve, index=df.index)
        returns = equity_series.pct_change().fillna(0)
        volatility = returns.std() * np.sqrt(252)
        sharpe = (
            (returns.mean() / returns.std()) * np.sqrt(252)
            if returns.std()
            else 0.0
        )
        cumulative = equity_series.cummax()
        drawdown = equity_series / cumulative - 1
        max_dd = drawdown.min()
        total_return = (
            equity_series.iloc[-1] - initial_balance
        ) / initial_balance
        calmar = total_return / abs(max_dd) if max_dd < 0 else np.inf
        wins = sum(1 for t in trades if t.profit_pct > 0)
        win_rate = wins / len(trades) if trades else 0.0

        return BacktestResult(
            sharpe=sharpe,
            max_drawdown=float(max_dd),
            win_rate=win_rate,
            total_return=total_return,
            volatility=volatility,
            calmar_ratio=calmar,
            trades=trades,
            equity_curve=equity_series,
