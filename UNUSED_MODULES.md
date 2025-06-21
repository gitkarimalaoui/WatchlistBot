# Unused or Out-of-Scope Modules

The following directories and files appear unrelated to the core WatchlistBot project. They either originate from other experiments or are empty placeholders. They are not referenced in documentation or the main application modules.

| Path | Notes | Remove or Merge? |
|------|-------|-----------------|
| `JobAutomationAssistant/` | Standalone Streamlit scripts for job searching. No references from main code. | Recommend removal or move to separate repo. |
| `cafe/` | Small cafe management demo with separate requirements. Not used by WatchlistBot. | Recommend removal or archival. |
| `Llama` (empty file) | Zero‑byte placeholder file at project root. | Safe to delete. |

These modules can likely be removed to reduce repository size and confusion. If any pieces are still useful, consider merging them into appropriate packages with tests and documentation.
