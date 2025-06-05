import logging
import os
import sys
import platform
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "ChatGptErrorPromptGenrator.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    handlers=[
        # Overwrite previous log on each run so old errors are cleared
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def debug_prompt() -> str:
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
    if issubclass(exc_type, KeyboardInterrupt):
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    logging.info(debug_prompt())

sys.excepthook = _handle_exception
