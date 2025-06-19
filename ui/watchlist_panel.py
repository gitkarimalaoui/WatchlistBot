import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")


def _inject_css() -> None:
    if st.session_state.get("_watchlist_css_injected"):
        return
    st.markdown(
        """
        <style>
            #right-watchlist {
                position: fixed;
                top: 0;
                right: 0;
                width: 320px;
                height: 100vh;
                overflow-y: auto;
                background-color: #f5f5f5;
                padding: 0.5rem;
                border-left: 1px solid #ddd;
                z-index: 1000;
            }
            div.block-container {
                margin-right: 330px;
            }
            #right-watchlist .badge-pump {
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


def _fetch_live() -> list[dict]:
    try:
        resp = requests.get(f"{API_URL}/watchlist/live", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:  # pragma: no cover - best effort
        st.warning(f"Erreur chargement live: {e}")
    return []


def render_watchlist_panel() -> None:
    """Affiche la watchlist live dans un panneau à droite."""
    _inject_css()
    params = st.query_params
    if "focus" in params:
        st.session_state["ticker_focus"] = params.get_all("focus")[0]
        st.query_params.clear()
        st.rerun()

    data = _fetch_live()
    st.markdown('<div id="right-watchlist">', unsafe_allow_html=True)
    st.markdown("### 📈 Watchlist Live")
    if data:
        data = sorted(
            data,
            key=lambda d: d.get("score_global", d.get("global_score", 0)),
            reverse=True,
        )
        for itm in data:
            tic = itm.get("ticker") or itm.get("symbol")
            if not tic:
                continue
            badge = "<span class='badge-pump'>PUMP</span>" if itm.get("isPump") else ""
            pct = itm.get("percent_gain") or itm.get("change_percent") or 0
            rsi = itm.get("rsi", "NA")
            ema = itm.get("ema", itm.get("ema9"))
            ema_str = str(ema) if ema is not None else "NA"
            upd = itm.get("updated_at") or itm.get("timestamp", "")
            url = f"?focus={tic}"
            st.markdown(
                f"**[ {tic} ]({url})** {badge}<br>"
                f"Score: {itm.get('score_global', itm.get('global_score','N/A'))} | %Gain: {pct} | "
                f"Vol: {itm.get('volume','N/A')} | RSI: {rsi} | EMA: {ema_str} | {upd}",
                unsafe_allow_html=True,
            )
    else:
        st.info("Aucune donnée")
    st.markdown('</div>', unsafe_allow_html=True)
