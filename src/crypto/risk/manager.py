from dataclasses import dataclass


@dataclass
class RiskConfig:
    max_position_size: float = 0.05  # 5% of portfolio
    stop_loss: float = 0.02  # 2%
    take_profit: float = 0.04  # 4%


class RiskManager:
    def __init__(self, config: RiskConfig) -> None:
        self.config = config

    def position_size(self, balance: float, price: float) -> float:
        return (balance * self.config.max_position_size) / price

    def stop_loss_price(self, entry: float) -> float:
        return entry * (1 - self.config.stop_loss)

    def take_profit_price(self, entry: float) -> float:
        return entry * (1 + self.config.take_profit)
