from __future__ import annotations

from typing import Dict, Any

import ccxt
from loguru import logger


class ExecutionService:
    def __init__(self, api_key: str, secret: str, sandbox: bool = False) -> None:
        self.exchange = ccxt.whitebit({
            'apiKey': api_key,
            'secret': secret,
        })
        if sandbox:
            self.exchange.set_sandbox_mode(True)

    def create_order(self, symbol: str, side: str, amount: float, price: float | None = None) -> Dict[str, Any]:
        logger.info("Placing %s order for %s %s", side, amount, symbol)
        try:
            if price:
                return self.exchange.create_limit_order(symbol, side, amount, price)
            return self.exchange.create_market_order(symbol, side, amount)
        except Exception as exc:  # pragma: no cover - network
            logger.error("Order failed: %s", exc)
            raise
