import asyncio
from pathlib import Path

import aiohttp
import pandas as pd
from loguru import logger

from crypto.config.loader import load_config
from crypto.data.collector import DataCollector
from crypto.execution.service import ExecutionService
from crypto.monitoring.monitor import Monitor
from crypto.risk.manager import RiskConfig, RiskManager
from crypto.strategy.engine import StrategyConfig, StrategyEngine


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


if __name__ == "__main__":
    asyncio.run(run(str(Path(__file__).with_name('config.yaml'))))
