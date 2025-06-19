import streamlit as st
import pandas as pd
from pathlib import Path

def app():
    st.title("🤖 IA Backtest Qlib")
    report_file = Path("reports/ai_backtest_report.csv")
    if report_file.exists():
        df = pd.read_csv(report_file, index_col=0)
        st.dataframe(df)
    else:
        st.warning("Aucun rapport AI backtest trouvé. Exécutez le runner d'abord.")
