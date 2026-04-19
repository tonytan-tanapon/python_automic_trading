from ib_insync import Forex, Stock

FX_CURRENCIES = {"USD", "EUR", "JPY", "GBP", "CHF", "CAD", "AUD", "NZD"}


def _clean_symbol(symbol: str) -> str:
    return symbol.strip().upper().replace(" ", "")


def normalize_symbol(symbol: str) -> str:
    cleaned = _clean_symbol(symbol)
    if "/" in cleaned:
        base, quote = cleaned.split("/", 1)
        return f"{base}{quote}"
    return cleaned


def is_forex_symbol(symbol: str) -> bool:
    cleaned = normalize_symbol(symbol)
    if len(cleaned) != 6 or not cleaned.isalpha():
        return False
    base = cleaned[:3]
    quote = cleaned[3:]
    return base in FX_CURRENCIES and quote in FX_CURRENCIES


def format_symbol(symbol: str) -> str:
    cleaned = normalize_symbol(symbol)
    if is_forex_symbol(cleaned):
        return f"{cleaned[:3]}/{cleaned[3:]}"
    return cleaned


def contract_symbol(contract) -> str:
    if getattr(contract, "secType", "") == "CASH":
        return format_symbol(f"{contract.symbol}{contract.currency}")
    return format_symbol(contract.symbol)


def build_contract(symbol: str):
    cleaned = normalize_symbol(symbol)
    if is_forex_symbol(cleaned):
        return Forex(cleaned)
    return Stock(cleaned, "SMART", "USD")
