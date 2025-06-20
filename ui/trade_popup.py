"""Streamlit helper to confirm trades.

This module exposes :func:`show_trade_popup_streamlit` used by
:mod:`realtime.pump_detector` and other real-time features.
"""

from __future__ import annotations

import streamlit as st

from utils.order_executor import executer_ordre_reel_direct


@st.dialog("Confirmation de trade")
def _trade_dialog(ticker: str, price: float, qty: int, stop_loss: float) -> None:
    """Internal dialog to display trade details."""
    st.write(f"**Ticker** : {ticker}")
    st.write(f"**Prix** : {price}")
    st.write(f"**Quantité** : {qty}")
    st.write(f"**Stop Loss** : {stop_loss:.2f}")
    col1, col2 = st.columns(2)
    if col1.button("Exécuter"):
        success, msg = executer_ordre_reel_direct(ticker, price, qty, stop_loss)
        st.session_state["trade_popup_msg"] = msg
        st.rerun()
    if col2.button("Annuler"):
        st.rerun()


def show_trade_popup_streamlit(
    ticker: str, price: float, qty: int, stop_loss: float
) -> None:
    """Open a Streamlit confirmation dialog with trade details."""
    _trade_dialog(ticker, price, qty, stop_loss)
    if "trade_popup_msg" in st.session_state:
        st.toast(st.session_state.pop("trade_popup_msg"))

