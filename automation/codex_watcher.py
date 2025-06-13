import json
import pickle
import time
from pathlib import Path
from typing import Callable, Any

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# --- Codex helper -----------------------------------------------------------

def open_codex_patch(data: Any, message: str) -> None:
    """Placeholder helper calling Codex to open a patch or PR.

    In production this function would trigger a Codex API call. In tests we
    simply record that it was called.
    """
    print(f"[CODEX] {message}: {str(data)[:60]}")


# --- Event handlers ---------------------------------------------------------

class FinRLModelHandler(FileSystemEventHandler):
    """Watch for new or updated FinRL model files."""

    def __init__(self, callback: Callable[[Any, str], None] = open_codex_patch):
        self.callback = callback

    def _process(self, path: Path) -> None:
        if path.suffix == ".json":
            try:
                data = json.loads(path.read_text())
            except Exception:
                data = path.read_text()
        elif path.suffix == ".pkl":
            try:
                with path.open("rb") as f:
                    data = pickle.load(f)
            except Exception:
                data = path.read_bytes()
        else:
            return
        self.callback(data, f"New model file {path.name}")

    def on_created(self, event):
        if event.is_directory:
            return
        self._process(Path(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            return
        self._process(Path(event.src_path))


class LogHandler(FileSystemEventHandler):
    """Watch for updates to log files."""

    def __init__(self, callback: Callable[[Any, str], None] = open_codex_patch):
        self.callback = callback

    def on_modified(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix != ".log":
            return
        if "local_llm" not in path.name and "finrl" not in path.name:
            return
        try:
            lines = path.read_text().splitlines()
            payload = "\n".join(lines[-20:])
        except Exception:
            payload = ""
        self.callback(payload, f"Log update {path.name}")


# --- Watcher startup --------------------------------------------------------

def start_watchers(models_dir: str = "models/finrl", logs_dir: str = "logs", callback: Callable[[Any, str], None] = open_codex_patch) -> Observer:
    models_path = Path(models_dir)
    logs_path = Path(logs_dir)
    models_path.mkdir(parents=True, exist_ok=True)
    logs_path.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(FinRLModelHandler(callback), str(models_path), recursive=False)
    observer.schedule(LogHandler(callback), str(logs_path), recursive=False)
    observer.start()
    return observer


def run_watchers(**kwargs) -> None:
    """Start watchers and block until interrupted."""
    observer = start_watchers(**kwargs)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:  # pragma: no cover - manual stop
        observer.stop()
    observer.join()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    run_watchers()
