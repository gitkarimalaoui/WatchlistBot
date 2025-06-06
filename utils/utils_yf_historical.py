"""Helpers to retrieve historical prices.

The module tries to rely on ``yfinance`` if available and falls back to the
Finnhub API otherwise.  Importing ``yfinance`` is optional so that the rest of
the application keeps working even when the package is absent (which is the
case in the test environment).
"""

import pandas as pd
import time
import random

try:
    # Standard package import when ``utils`` is a package
    from .advanced_logger import safe_api_call
except Exception:  # pragma: no cover - fallback when executed as a script
    from advanced_logger import safe_api_call

try:  # yfinance is optional in the execution environment
    import yfinance as yf
except Exception:  # pragma: no cover - informational print only
    yf = None
    print("[YF WARNING] yfinance package not available")

try:
    from .utils_finnhub import fetch_finnhub_historical_data
except Exception:  # pragma: no cover - fallback when executed as a script
    from utils_finnhub import fetch_finnhub_historical_data


def _handle_rate_limit_delay(attempt: int = 1):
    """Handle rate limiting with exponential backoff and jitter."""
    base_delay = 30  # Base delay of 30 seconds for rate limits
    jitter = random.uniform(0.5, 1.5)  # Add randomness to avoid thundering herd
    delay = base_delay * (2 ** (attempt - 1)) * jitter
    max_delay = 300  # Cap at 5 minutes
    actual_delay = min(delay, max_delay)
    
    print(f"[YF INFO] Rate limit encountered, waiting {actual_delay:.1f} seconds (attempt {attempt})")
    time.sleep(actual_delay)


@safe_api_call(retries=3, delay=1.5, backoff=2.0)
def fetch_yf_historical_data(
    ticker: str,
    period: str = "5y",
    interval: str = "1d",
    threads: bool = False,
    max_rate_limit_retries: int = 3,
) -> pd.DataFrame:
    """Download historical prices from Yahoo Finance and fall back to Finnhub.

    Parameters are exposed so they can easily be tuned if the default call
    returns empty dataframes. ``threads`` is disabled by default as it sometimes
    causes connection issues in constrained environments.
    
    Args:
        ticker: Stock ticker symbol
        period: Period to download (e.g., "5y", "1y", "6mo")
        interval: Data interval (e.g., "1d", "1h", "1m")
        threads: Whether to use threading for downloads
        max_rate_limit_retries: Maximum retries for rate limit errors
    """
    if yf is None:
        print(f"[YF ERROR] yfinance not available for {ticker}")
        return None

    rate_limit_attempt = 0
    
    while rate_limit_attempt <= max_rate_limit_retries:
        try:
            # Try the main download method first
            df = yf.download(
                tickers=ticker,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True,
                threads=threads,
                group_by="ticker",
            )

            if df.empty:
                print(f"[YF WARNING] Empty data for {ticker} via download, trying history API")
                try:
                    df = yf.Ticker(ticker).history(period=period, interval=interval)
                except Exception as e:
                    if _is_rate_limit_error(e):
                        rate_limit_attempt += 1
                        if rate_limit_attempt <= max_rate_limit_retries:
                            _handle_rate_limit_delay(rate_limit_attempt)
                            continue
                        else:
                            print(f"[YF ERROR] Max rate limit retries exceeded for {ticker}")
                            break
                    else:
                        print(f"[YF ERROR] History fetch failed for {ticker}: {e}")
                        df = pd.DataFrame()

            if df.empty:
                print(f"[YF WARNING] Empty data for {ticker}, falling back to Finnhub")
                df = fetch_finnhub_historical_data(ticker)
                if df is None or df.empty:
                    print(f"[YF ERROR] No data available from any source for {ticker}")
                    return None
                return df

            # Process the successful DataFrame
            return _process_yf_dataframe(df, ticker)

        except Exception as e:
            if _is_rate_limit_error(e):
                rate_limit_attempt += 1
                if rate_limit_attempt <= max_rate_limit_retries:
                    _handle_rate_limit_delay(rate_limit_attempt)
                    continue
                else:
                    print(f"[YF ERROR] Max rate limit retries exceeded for {ticker}")
                    break
            else:
                print(f"[YF ERROR] Unexpected error for {ticker}: {e}")
                return None

    # If we get here, we've exhausted rate limit retries
    print(f"[YF ERROR] Rate limit retries exhausted for {ticker}, trying Finnhub fallback")
    return None


def _is_rate_limit_error(error) -> bool:
    """Check if an error is related to rate limiting."""
    error_indicators = [
        "YFRateLimitError",
        "Too Many Requests",
        "Rate limited",
        "429",
        "rate limit"
    ]
    
    error_str = str(error).lower()
    error_type = type(error).__name__
    
    return any(indicator.lower() in error_str or indicator.lower() in error_type.lower() 
              for indicator in error_indicators)


def _process_yf_dataframe(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Process and standardize Yahoo Finance DataFrame."""
    try:
        # Convert index to a dedicated timestamp column regardless of its name
        df.index = pd.to_datetime(df.index)
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: "timestamp"}, inplace=True)

        # Handle multi-indexed columns if present
        if isinstance(df.columns, pd.MultiIndex):
            # drop the outer ticker level
            df.columns = df.columns.get_level_values(1)

        # Standardize column names
        column_map = {
            "timestamp": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "close",  # Prefer adjusted close over regular close
            "Volume": "volume",
        }
        
        available_cols = [c for c in column_map.keys() if c in df.columns]
        
        # Check for required columns
        has_timestamp = "timestamp" in available_cols
        has_close = "Close" in df.columns or "Adj Close" in df.columns
        
        if not has_timestamp or not has_close:
            print(f"[YF ERROR] Missing required columns for {ticker}. Available: {list(df.columns)}")
            return None

        # Select and rename columns
        df = df[available_cols]
        df.rename({k: column_map[k] for k in available_cols}, axis=1, inplace=True)
        
        # Ensure final column order
        ordered = [column_map[c] for c in column_map if c in available_cols]
        df = df[ordered]
        
        # Basic data validation
        if df.empty or df['close'].isna().all():
            print(f"[YF ERROR] No valid price data for {ticker}")
            return None
            
        print(f"[YF SUCCESS] Retrieved {len(df)} records for {ticker}")
        return df

    except Exception as e:
        print(f"[YF ERROR] Failed to process DataFrame for {ticker}: {e}")
        return None


def fetch_historical_with_fallback(ticker: str, max_retries: int = 2) -> pd.DataFrame:
    """Attempt to fetch data from Yahoo Finance then fall back to Finnhub.
    
    Args:
        ticker: Stock ticker symbol
        max_retries: Maximum number of retry attempts for each data source
    """
    print(f"[INFO] Fetching historical data for {ticker}")
    
    # Try Yahoo Finance first
    for attempt in range(max_retries + 1):
        if attempt > 0:
            print(f"[INFO] Retry attempt {attempt} for Yahoo Finance data for {ticker}")
            time.sleep(2 ** attempt)  # Exponential backoff
            
        df = fetch_yf_historical_data(ticker)
        if df is not None and not df.empty:
            return df

    # Fall back to Finnhub
    print(f"[INFO] Yahoo Finance failed, trying Finnhub fallback for {ticker}")
    
    for attempt in range(max_retries + 1):
        if attempt > 0:
            print(f"[INFO] Retry attempt {attempt} for Finnhub data for {ticker}")
            time.sleep(2 ** attempt)
            
        try:
            df = fetch_finnhub_historical_data(ticker)
            if df is None or df.empty:
                continue
                
            # Standardize Finnhub data format
            df = _process_finnhub_dataframe(df, ticker)
            if df is not None and not df.empty:
                print(f"[INFO] Successfully retrieved {len(df)} records from Finnhub for {ticker}")
                return df
                
        except Exception as e:
            print(f"[FINNHUB ERROR] Attempt {attempt + 1} failed for {ticker}: {e}")
            if attempt == max_retries:
                break

    print(f"[ERROR] All data sources failed for {ticker}")
    return None


def _process_finnhub_dataframe(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Process and standardize Finnhub DataFrame."""
    try:
        # Handle different possible column names from Finnhub
        if "Date" in df.columns:
            df = df.rename(columns={"Date": "timestamp"})
        elif "t" in df.columns:  # Finnhub sometimes uses 't' for timestamp
            df = df.rename(columns={"t": "timestamp"})
        
        if "Close" in df.columns:
            df = df.rename(columns={"Close": "close"})
        elif "c" in df.columns:  # Finnhub sometimes uses 'c' for close
            df = df.rename(columns={"c": "close"})

        # Ensure timestamp column exists
        if "timestamp" not in df.columns:
            df.reset_index(inplace=True)
            df.rename(columns={df.columns[0]: "timestamp"}, inplace=True)

        # Ensure close column exists
        if "close" not in df.columns and "Close" in df.columns:
            df.rename(columns={"Close": "close"}, inplace=True)

        # Validate required columns
        if "timestamp" not in df.columns or "close" not in df.columns:
            print(f"[FINNHUB ERROR] Missing required columns for {ticker}. Available: {list(df.columns)}")
            return None

        # Select only the columns we need
        df = df[["timestamp", "close"]]
        
        # Convert timestamp to datetime if it's not already
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Basic data validation
        if df.empty or df['close'].isna().all():
            print(f"[FINNHUB ERROR] No valid price data for {ticker}")
            return None
            
        return df
        
    except Exception as e:
        print(f"[FINNHUB ERROR] Failed to process DataFrame for {ticker}: {e}")
        return None