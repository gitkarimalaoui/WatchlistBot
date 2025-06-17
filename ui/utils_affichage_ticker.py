
from simulation.execution_simulee import enregistrer_trade_simule

import streamlit as st
from utils_graph import (
    plot_dual_chart,
    charger_historique_intelligent,
    charger_intraday_intelligent,
)
from utils.order_executor import executer_ordre_reel_direct


def _enregistrer_trade(ticker: str, prix: float, quantite: int = 1, sl=None, tp=None, exit_price=None):
    """Enregistre un trade simulé dans la base de données."""
    enregistrer_trade_simule(
        ticker=ticker,
        entry_price=prix,
        quantity=quantite,
        sl=sl,
        tp=tp,
        exit_price=exit_price,
    )

def afficher_ticker_panel(ticker, stock, index):
    label = f"{index + 1}. {ticker}"
    with st.expander(label, expanded=False):
        st.markdown(f"**Score IA :** {stock.get('score', 'N/A')}")
        st.markdown(f"**Score global :** {stock.get('global_score', 'N/A')}")
        st.markdown(f"**Score GPT :** {stock.get('score_gpt', 'N/A')}")
        st.markdown(f"**Sentiment :** {stock.get('sentiment', 'N/A')}")
        st.markdown(f"**Source :** {stock.get('source', 'N/A')}")
        st.markdown(f"**Date :** {stock.get('date', 'N/A')}")
        st.markdown(f"**Description :** {stock.get('description', 'N/A')}")
        if stock.get('has_fda'):
            st.markdown("🧬 **FDA match**", unsafe_allow_html=True)
        st.markdown(f"**Dernier prix :** {stock.get('price', 'N/A')}")
        st.markdown(f"**Volume :** {stock.get('volume', 'N/A')}")
        st.markdown(
            f"**% Gain :** {stock.get('percent_gain', stock.get('change_percent', 'N/A'))}"
        )
        st.markdown(f"**Float :** {stock.get('float', 'N/A')}")

        details_key = f"details_{ticker}_{index}"
        details_state_key = f"{details_key}_state"
        if st.button("Afficher détails", key=details_key):
            st.session_state[details_state_key] = not st.session_state.get(details_state_key, False)

        if st.session_state.get(details_state_key, False):
            df_hist = charger_historique_intelligent(ticker)
            df_intraday = charger_intraday_intelligent(ticker)
            if df_hist is not None and not df_hist.empty:
                plot_dual_chart(ticker, df_hist, df_intraday)
            else:
                st.warning("Données historiques indisponibles.")

        prix = st.number_input(
            "💵 Prix", min_value=0.0, step=0.01, key=f"prix_{ticker}_{index}"
        )
        quantite = st.number_input(
            "🔢 Quantité", min_value=1, step=1, value=1, key=f"qty_{ticker}_{index}"
        )
        stop_loss = st.number_input(
            "❗ Stop loss", min_value=0.0, step=0.01, key=f"sl_{ticker}_{index}"
        )
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Simuler l'achat", key=f"sim_buy_{ticker}_{index}"):
            _enregistrer_trade(ticker, prix, int(quantite), sl=stop_loss)
            st.success(f"Achat simulé enregistré pour {ticker} à {prix:.2f} $")
        if c2.button("Simuler la vente", key=f"sim_sell_{ticker}_{index}"):
            _enregistrer_trade(ticker, prix, int(quantite), exit_price=prix)
            st.success(f"Vente simulée enregistrée pour {ticker} à {prix:.2f} $")
        if c3.button("Achat réel", key=f"real_buy_{ticker}_{index}"):
            ok, msg = executer_ordre_reel_direct(ticker, prix, int(quantite), stop_loss)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
        if c4.button("Vente réelle", key=f"real_sell_{ticker}_{index}"):
            st.warning("Fonction vente réelle non implémentée")
