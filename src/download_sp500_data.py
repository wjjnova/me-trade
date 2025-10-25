"""Utility script to download popular S&P 500 constituents plus selected ETFs."""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from src.data.stocks import StockDataManager

START_DATE = "2019-01-01"
EXTRA_SYMBOLS = [
    "VOO",  # Vanguard S&P 500 ETF
    "QQQ",  # Invesco QQQ Trust
    "SPY",  # SPDR S&P 500 ETF
    "ARKK",  # ARK Innovation ETF
    "ARKW",  # ARK Next Generation Internet ETF
    "ARKG",  # ARK Genomic Revolution ETF
    "ARKF",  # ARK Fintech Innovation ETF
    "ARKQ",  # ARK Autonomous Technology & Robotics ETF
    "DIA",  # SPDR Dow Jones Industrial Average ETF
    "IWM",  # iShares Russell 2000 ETF
    "EFA",  # iShares MSCI EAFE ETF
    "EEM",  # iShares MSCI Emerging Markets ETF
    "VTI",  # Vanguard Total Stock Market ETF
    "VT",   # Vanguard Total World Stock ETF
    "IWV",  # iShares Russell 3000 ETF
    "^GSPC",  # S&P 500 Index
    "^NDX",   # NASDAQ-100 Index
    "^DJI",   # Dow Jones Industrial Average
    "^RUT",   # Russell 2000 Index
    "^VIX",   # CBOE Volatility Index
]
POPULAR_SP500_SYMBOLS: List[str] = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOG",
    "GOOGL",
    "TSLA",
    "AVGO",
    "LLY",
    "JPM",
    "UNH",
    "V",
    "MA",
    "XOM",
    "JNJ",
    "PG",
    "HD",
    "KO",
    "PEP",
    "MRK",
    "ABBV",
    "COST",
    "CRM",
    "ADBE",
    "ORCL",
    "PFE",
    "BAC",
    "WMT",
    "LIN",
    "MCD",
    "CSCO",
    "AMD",
    "NFLX",
    "ACN",
    "TMO",
    "DHR",
    "ABT",
    "TXN",
    "NKE",
    "MS",
    "CAT",
    "HON",
    "IBM",
    "AMAT",
    "PM",
    "QCOM",
    "MDT",
    "UNP",
    "COP",
    "AMGN",
    "LMT",
    "GS",
    "NOW",
    "BLK",
    "SPGI",
    "BKNG",
    "INTU",
    "CME",
    "C",
    "T",
    "MU",
    "PANW",
    "ZTS",
    "ADI",
    "DE",
    "UPS",
    "TGT",
    "PGR",
    "ADP",
    "CHTR",
    "PLD",
    "SCHW",
    "SBUX",
    "GILD",
    "CVS",
    "LOW",
    "USB",
    "MO",
    "SO",
    "D",
    "MET",
    "AON",
    "BK",
    "CL",
    "BMY",
    "LRCX",
    "EOG",
    "EQIX",
    "SNPS",
    "CDNS",
    "REGN",
    "MMC",
    "ICE",
    "KMB",
    "MMM",
    "GM",
    "F",
    "BA",
    "GE",
]


def _normalize_symbol(symbol: str) -> str:
    """Normalize Wikipedia ticker entries for yfinance."""
    return symbol.strip().upper().replace(".", "-")


def fetch_sp500_symbols(extra_symbols: Optional[List[str]] = None) -> List[str]:
    """Return a curated list of popular S&P 500 symbols plus optional extras."""

    base_symbols = [_normalize_symbol(sym) for sym in POPULAR_SP500_SYMBOLS]
    extras = extra_symbols if extra_symbols is not None else EXTRA_SYMBOLS

    seen = set()
    unique_symbols: List[str] = []
    for sym in base_symbols + [_normalize_symbol(sym) for sym in extras]:
        if sym and sym not in seen:
            seen.add(sym)
            unique_symbols.append(sym)

    return unique_symbols


def download_sp500_data(
    start_date: str = START_DATE,
    extra_symbols: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Download curated S&P 500 symbols plus ETFs into the local cache."""

    symbols = fetch_sp500_symbols(extra_symbols)
    end_date = date.today().isoformat()

    manager = StockDataManager()
    results = manager.download_stocks(symbols, start_date, end_date, interval="1d")

    return {
        "symbols": symbols,
        "results": results,
        "start": start_date,
        "end": end_date,
    }


def main() -> None:
    payload = download_sp500_data()
    results = payload["results"]
    symbols = payload["symbols"]

    print("=== Download Complete ===")
    print(f"Symbols requested: {len(symbols)}")
    print(f"Preview (top 5): {symbols[:5]}")
    print(f"Success: {len(results['success'])} symbols")
    print(f"Failures: {len(results['failed'])} symbols")
    print(f"Total rows inserted: {results['total_rows']}")

    if results["failed"]:
        print("\nFailed symbols:")
        for item in results["failed"]:
            print(f"- {item['symbol']}: {item['error']}")


if __name__ == "__main__":
    main()
