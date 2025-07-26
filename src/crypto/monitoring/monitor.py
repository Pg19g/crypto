from loguru import logger


class Monitor:
    def __init__(self) -> None:
        logger.add("trading.log", rotation="1 MB")

    def info(self, message: str) -> None:
        logger.info(message)

    def error(self, message: str) -> None:
        logger.error(message)
