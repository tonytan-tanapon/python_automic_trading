class StrategyProtocol:
    name = "base"

    def evaluate(self, symbol: str) -> dict:
        raise NotImplementedError
