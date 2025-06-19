import logging
import os
import sys
import platform
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "ChatGptErrorPromptGenrator.log"

# Start each run with a clean log file that includes a prompt
with open(LOG_FILE, "w", encoding="utf-8") as log:
    log.write(
        "I encountered an error while running WatchlistBot.\n\n"
        "Here is the stack trace and debug information from logs/ChatGptErrorPromptGenrator.log:\n\n"
        "<PASTE stack trace here>\n\n"
        "<PASTE lines starting with \"=== DEBUG INFO (copy below) ===\" down to \"===============================\">\n\n"
        "Please analyze this information and suggest how to resolve the issue.\n\n"
    )

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    handlers=[
        # Append after the initial prompt written above
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def debug_prompt() -> str:
    """Return a formatted debug block with environment information.

    This helper gathers basic runtime details to assist with error
    diagnostics. The resulting string is logged whenever an exception is
    captured so that developers can share the context when reporting an
    issue.

    Returns:
        str: Multi-line string containing version, OS and path details.
    """

    details = [
        "=== DEBUG INFO (copy below) ===",
        f"Python: {platform.python_version()}",
        f"OS: {platform.platform()}",
        f"Working dir: {os.getcwd()}",
        f"Script: {sys.argv[0]}",
        "Share this block when reporting issues",
        "==============================="
    ]
    return "\n".join(details)

logging.info(debug_prompt())

# Capture uncaught exceptions
def _handle_exception(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions with context information.

    This function is installed as ``sys.excepthook`` to intercept any
    unexpected errors. KeyboardInterrupt exceptions are ignored so that
    manual termination remains silent. All other exceptions are logged
    along with the debug prompt for easier troubleshooting.

    Args:
        exc_type (type): Exception class being handled.
        exc_value (BaseException): Exception instance.
        exc_traceback (TracebackType): Traceback object for the exception.
    """

    if issubclass(exc_type, KeyboardInterrupt):
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    logging.info(debug_prompt())

sys.excepthook = _handle_exception

# ---------------------------------------------------------------------------
# Streamlit watchlist auto-integration
# ---------------------------------------------------------------------------
try:
    ROOT = Path(__file__).parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    ui_path = ROOT / "ui"
    if str(ui_path) not in sys.path:
        sys.path.insert(0, str(ui_path))

    from streamlit.runtime.scriptrunner.script_runner import ScriptRunner
    from ui.watchlist_panel import render_watchlist_panel, _fetch_live
    from ui.utils_affichage_ticker import afficher_ticker_panel

    if not getattr(ScriptRunner, "_watchlist_patched", False):
        _orig_run_script = ScriptRunner._run_script

        def _run_script_with_watchlist(self, rerun_data):
            import streamlit as st

            main_col, watch_col = st.columns([7, 3])
            ticker = st.query_params.get("ticker")
            if ticker:
                st.session_state["ticker_focus"] = ticker
                try:
                    data = _fetch_live()
                    info = next((d for d in data if (d.get("ticker") or d.get("symbol")) == ticker), {})
                except Exception:
                    info = {}
                with main_col:
                    afficher_ticker_panel(ticker, info, 0)

            with main_col:
                _orig_run_script(self, rerun_data)

            with watch_col:
                render_watchlist_panel()

        ScriptRunner._run_script = _run_script_with_watchlist
        ScriptRunner._watchlist_patched = True
except Exception as e:  # pragma: no cover - best effort
    logging.warning(f"Watchlist auto patch failed: {e}")

