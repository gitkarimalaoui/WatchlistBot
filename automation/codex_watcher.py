import json
import pickle
import time
from pathlib import Path
from typing import Callable, Any

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# --- Codex helper -----------------------------------------------------------

def open_codex_patch(data: Any, message: str) -> None:
    """Send a payload to Codex for patch creation.

    This helper is a stub used during development. It merely prints a
    short preview of the data being sent. In production the implementation
    would forward the payload to the Codex API to open a pull request or
    patch.

    Args:
        data (Any): Serialized model or log content to transmit.
        message (str): Human readable description of the payload.

    Returns:
        None
    """

    print(f"[CODEX] {message}: {str(data)[:60]}")


# --- Event handlers ---------------------------------------------------------

class FinRLModelHandler(FileSystemEventHandler):
    """Watch for new or updated FinRL model files."""

    def __init__(self, callback: Callable[[Any, str], None] = open_codex_patch):
        """Initialize the handler.

        Args:
            callback (Callable[[Any, str], None]): Function called with the
                loaded model data and a short description.
        """

        self.callback = callback

    def _process(self, path: Path) -> None:
        """Load model data and forward it through the callback.

        Args:
            path (Path): File path that triggered the event.
        """

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
        """Handle new files detected by watchdog."""
        if event.is_directory:
            return
        self._process(Path(event.src_path))

    def on_modified(self, event):
        """Handle file modifications detected by watchdog."""
        if event.is_directory:
            return
        self._process(Path(event.src_path))


class LogHandler(FileSystemEventHandler):
    """Watch for updates to log files."""

    def __init__(self, callback: Callable[[Any, str], None] = open_codex_patch):
        """Initialize the log handler.

        Args:
            callback (Callable[[Any, str], None]): Function called with the
                tail of the log file and a short description.
        """

        self.callback = callback

    def on_modified(self, event):
        """Send the last log lines when a watched file changes."""
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

def start_watchers(
    models_dir: str = "models/finrl",
    logs_dir: str = "logs",
    callback: Callable[[Any, str], None] = open_codex_patch,
) -> Observer:
    """Create and start observers for model and log folders.

    Args:
        models_dir (str): Directory containing FinRL models to watch.
        logs_dir (str): Directory containing log files to watch.
        callback (Callable[[Any, str], None]): Function invoked when new
            data is detected.

    Returns:
        Observer: Active watchdog observer monitoring the folders.
    """

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
    """Run the filesystem watchers until manually stopped.

    This helper simply calls :func:`start_watchers` and keeps the main
    thread alive. It can be used as a CLI entry point during development
    to monitor model and log folders.

    Args:
        **kwargs: Forwarded to :func:`start_watchers`.

    Returns:
        None
    """

    observer = start_watchers(**kwargs)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:  # pragma: no cover - manual stop
        observer.stop()
    observer.join()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    run_watchers()
