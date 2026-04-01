from app.config import AUTO_TRADING_STRATEGY
from app.strategies.mean_reversion import MeanReversionStrategy
from app.strategies.momentum import MomentumStrategy
from app.strategies.sma_crossover import MovingAverageCrossoverStrategy


STRATEGY_REGISTRY = {
    MovingAverageCrossoverStrategy.name: MovingAverageCrossoverStrategy,
    MomentumStrategy.name: MomentumStrategy,
    MeanReversionStrategy.name: MeanReversionStrategy,
}


def build_strategy(strategy_name: str | None = None):
    selected_name = (strategy_name or AUTO_TRADING_STRATEGY).strip().lower()
    strategy_class = STRATEGY_REGISTRY.get(selected_name)
    if strategy_class is None:
        supported = ", ".join(sorted(STRATEGY_REGISTRY))
        raise ValueError(f"Unknown strategy '{selected_name}'. Supported: {supported}")
    return strategy_class()


def list_strategies():
    return sorted(STRATEGY_REGISTRY)
