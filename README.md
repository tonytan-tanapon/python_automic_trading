# python_automic_trading

Auto trading backend with FastAPI and Interactive Brokers.

Key features:
- account summary endpoint
- current positions endpoint
- market data snapshot endpoint
- buy and sell market orders
- websocket price stream
- auto-trading engine with configurable strategies
- scheduler loop with start, stop, status, and run-once controls
- built-in risk limits for live mode, cooldown, daily trade cap, and max position size

Environment variables for auto trading:
- `AUTO_TRADING_STRATEGY=sma_crossover|momentum|mean_reversion`
- `AUTO_TRADING_SYMBOLS=AAPL,MSFT`
- `AUTO_TRADING_INTERVAL_SECONDS=60`
- `AUTO_TRADING_ORDER_SIZE=1`
- `AUTO_TRADING_STOP_LOSS_PCT=0.03`
- `AUTO_TRADING_TAKE_PROFIT_PCT=0.05`
