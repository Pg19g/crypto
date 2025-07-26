import asyncio
from pathlib import Path

import aiohttp
import pandas as pd
from loguru import logger
from datetime import datetime, timedelta

from crypto.config.loader import load_config
from crypto.data.collector import DataCollector
from crypto.data.history import HistoricalDataManager, OHLCVConfig
from crypto.execution.service import ExecutionService
from crypto.monitoring.monitor import Monitor
from crypto.risk.manager import RiskConfig, RiskManager
from crypto.strategy.engine import StrategyConfig, StrategyEngine
from crypto.backtesting.service import BacktestingService


async def run(config_path: str) -> None:
    config = load_config(config_path)
    strategy_conf = StrategyConfig(**config.get('strategies', {}))
    risk_conf = RiskConfig(**config.get('risk', {}))
    monitor = Monitor()
    async with aiohttp.ClientSession() as session:
        collector = DataCollector(session)
        data = await collector.collect(symbol='BTC', api_key=config['lunarcrush']['api_key'])

    df = pd.DataFrame(data['markets']) if isinstance(data['markets'], list) else pd.DataFrame()
    galaxy_score = data['lunarcrush'].get('data', [{}])[0].get('galaxy_score', 0)

    engine = StrategyEngine(strategy_conf)
    signals = engine.generate_signals(df, galaxy_score)
    monitor.info(f"Generated signals: {signals}")

    risk_mgr = RiskManager(risk_conf)
    exec_service = ExecutionService(
        api_key=config['exchange']['api_key'],
        secret=config['exchange']['secret'],
        sandbox=config['exchange'].get('sandbox', False),
    )

    if signals['signal'] == 'buy':
        amount = risk_mgr.position_size(balance=1000, price=df['close'].astype(float).iloc[-1])
        exec_service.create_order('BTC/USDT', 'buy', amount)
    elif signals['signal'] == 'sell':
        amount = risk_mgr.position_size(balance=1000, price=df['close'].astype(float).iloc[-1])
        exec_service.create_order('BTC/USDT', 'sell', amount)


async def run_backtest_example(config_path: str) -> None:
    """Example usage of the backtesting service."""
    config = load_config(config_path)
    async with aiohttp.ClientSession() as session:
        hist_mgr = HistoricalDataManager(session)
        ohlcv_cfg = OHLCVConfig(
            symbol="BTC_USDT",
            timeframe="1h",
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
        )
        df = await hist_mgr.fetch_ohlcv(ohlcv_cfg)

        if df.empty:
            logger.error("No historical data available")
            return

        strategy_conf = StrategyConfig(**config.get("strategies", {}))
        engine = StrategyEngine(strategy_conf)
        backtester = BacktestingService(fee=0.001, slippage=0.0005)
        result = backtester.run_backtest(df, engine, galaxy_score=75.0)

        logger.info("Backtest Results:")
        logger.info(f"Total Return: {result.total_return:.2%}")
        logger.info(f"Sharpe Ratio: {result.sharpe:.2f}")
        logger.info(f"Max Drawdown: {result.max_drawdown:.2%}")
        logger.info(f"Win Rate: {result.win_rate:.2%}")
        logger.info(f"Number of Trades: {len(result.trades)}")


if __name__ == "__main__":
    asyncio.run(run_backtest_example(str(Path(__file__).with_name('config.yaml'))))
