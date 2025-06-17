from __future__ import annotations

import asyncio
import heapq
from datetime import datetime
from typing import Optional

try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pyttsx3 = None  # type: ignore

from automation.orchestrateur_evenements import EVENT_QUEUE, Event


class ProactiveVoiceNotifier:
    """Announce events from the orchestrator queue using TTS."""

    def __init__(self, check_interval: float = 2.0) -> None:
        self.check_interval = check_interval
        self.engine = pyttsx3.init() if pyttsx3 else None

    def _speak(self, text: str) -> None:
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
        else:  # pragma: no cover - fallback when pyttsx3 missing
            print(f"[VOICE] {text}")

    def run_pending(self) -> None:
        """Speak all events whose time_to_run has passed."""
        now_ts = datetime.now().timestamp()
        while EVENT_QUEUE and EVENT_QUEUE[0][0] <= now_ts:
            _, event = heapq.heappop(EVENT_QUEUE)
            self._speak(event.title)

    async def run(self) -> None:
        """Start the proactive loop."""
        while True:
            self.run_pending()
            await asyncio.sleep(self.check_interval)
