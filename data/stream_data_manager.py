import json
import os
import threading
from datetime import datetime

import websocket
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
WATCHLIST = ["TSLA", "AAPL", "NVDA"]

latest_data: dict[str, dict] = {}
connected = False
ws_app: websocket.WebSocketApp | None = None
_data_lock = threading.Lock()


def set_watchlist(tickers: list[str]) -> None:
    """Update the list of tickers subscribed to the WebSocket."""
    global WATCHLIST
    WATCHLIST = [t.upper() for t in tickers]
    if connected and ws_app is not None:
        for t in WATCHLIST:
            ws_app.send(json.dumps({"type": "subscribe", "symbol": t}))


def on_message(ws: websocket.WebSocketApp, message: str) -> None:
    data = json.loads(message)
    if "data" in data:
        for d in data["data"]:
            ticker = d["s"]
            with _data_lock:
                latest_data[ticker] = {
                    "price": d["p"],
                    "volume": d.get("v", 0),
                    "timestamp": datetime.utcfromtimestamp(d["t"] / 1000).isoformat(),
                    "source": "WS",
                    "status": "OK",
                }


def on_error(ws: websocket.WebSocketApp, error: Exception) -> None:
    print(f"[WS ERROR] {error}")


def on_close(ws: websocket.WebSocketApp, close_status_code, close_msg) -> None:
    global connected
    connected = False
    print("[WS CLOSED]")


def on_open(ws: websocket.WebSocketApp) -> None:
    global connected
    connected = True
    for ticker in WATCHLIST:
        ws.send(json.dumps({"type": "subscribe", "symbol": ticker}))
    print("[WS CONNECTED]")


def start_ws() -> None:
    """Start the Finnhub WebSocket in a background thread."""
    global ws_app
    url = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"
    ws_app = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    thread = threading.Thread(target=ws_app.run_forever, daemon=True)
    thread.start()


def fallback_data(ticker: str) -> dict:
    try:
        data = yf.download(ticker, period="1d", interval="1m")
        if not data.empty:
            last = data.iloc[-1]
            return {
                "price": round(last["Close"], 2),
                "volume": int(last["Volume"]),
                "timestamp": last.name.isoformat(),
                "source": "FALLBACK",
                "status": "WARN",
            }
        return {"status": "ERR"}
    except Exception as e:  # pragma: no cover - network errors
        print(f"[FALLBACK ERROR] {e}")
        return {"status": "ERR"}


def get_latest_data(ticker: str) -> dict:
    with _data_lock:
        data = latest_data.get(ticker)
    if data:
        ts = datetime.fromisoformat(data["timestamp"])
        if (datetime.utcnow() - ts).total_seconds() < 10:
            return data
    return fallback_data(ticker)


start_ws()
