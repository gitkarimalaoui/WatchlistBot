import os
import requests
import streamlit as st
from typing import List, Dict

API_URL = os.getenv("API_URL", "http://localhost:8000")


def _inject_css() -> None:
    """Inject minimal CSS only once for watchlist styling."""
    if st.session_state.get("_watchlist_css_injected"):
        return
    st.markdown(
        """
        <style>
            .badge-pump {
                background: #ff4b4b;
                color: white;
                border-radius: 4px;
                padding: 0 4px;
                font-size: 0.75rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.session_state["_watchlist_css_injected"] = True


def _fetch_live() -> List[Dict]:
    try:
        resp = requests.get(f"{API_URL}/watchlist/live", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:  # pragma: no cover - best effort
        st.warning(f"Erreur chargement live: {e}")
    return []


def render_watchlist_panel() -> None:
    """Display the live watchlist sorted by score."""
    _inject_css()
    data = _fetch_live()
    st.markdown("### 📈 Watchlist Live")
    if not data:
        st.info("Aucune donnée")
        return

    def _score_key(row: Dict) -> float:
        score = row.get("score_global")
        if score is None:
            score = row.get("global_score")
        if score is None:
            score = 0
        return score

    data = sorted(data, key=_score_key, reverse=True)
    for itm in data:
        tic = itm.get("ticker") or itm.get("symbol")
        if not tic:
            continue
        badge = " [PUMP]" if itm.get("is_pump") or itm.get("isPump") else ""
        price = itm.get("price", "NA")
        pct = itm.get("percent_gain") or itm.get("change_percent") or 0
        vol_ratio = itm.get("volume_ratio", "NA")
        rsi = itm.get("rsi", "NA")
        ema_sig = itm.get("ema_signal") or itm.get("ema9")
        ema_sig = ema_sig if ema_sig is not None else "NA"
        score = itm.get("score_global", itm.get("global_score", "N/A"))
        label = (
            f"{tic} | {price} ({pct:+.2f}%) | Vol {vol_ratio} | RSI {rsi} | EMA {ema_sig} | Score {score}{badge}"
        )
        if st.button(label, key=f"watch_{tic}"):
            st.query_params["ticker"] = tic
            st.rerun()

