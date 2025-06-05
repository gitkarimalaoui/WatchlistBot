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