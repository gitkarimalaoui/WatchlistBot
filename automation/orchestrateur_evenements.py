from __future__ import annotations

import asyncio
import heapq
import json
import logging
import os
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, time, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

import requests

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "project_tracker.db"
VOCAL_HOURS = (8, 22)

logger = logging.getLogger(__name__)


class Priority(Enum):
    CRITICAL = 0
    URGENT = 1
    IMPORTANT = 2
    INFO = 3
    BACKGROUND = 4


@dataclass(order=True)
class Event:
    sort_index: int = field(init=False, repr=False)
    event_id: str
    source: str
    title: str
    priority: Priority
    time_to_run: datetime
    output_channel: str = "vocal"
    context_tags: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.sort_index = self.priority.value


EVENT_QUEUE: List[tuple[float, Event]] = []


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def send_telegram(text: str) -> None:
    """Send a Telegram message if credentials are available."""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as exc:  # pragma: no cover - network error
        logger.warning("Telegram notification failed: %s", exc)


def trigger_trading_action(event: Event) -> None:
    """Placeholder for a trading API call."""
    if "trading" in event.context_tags:
        logger.info("[TRADING] Action triggered for %s", event.title)


# ---------------------------------------------------------------------------
# Event collection and analysis
# ---------------------------------------------------------------------------

def collect_events(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Load raw events from the project tracker database."""
    if not db_path.exists():
        return []

    events: List[Dict[str, Any]] = []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        for row in conn.execute(
            "SELECT id, description, due_date, importance_score FROM tasks WHERE done = 0"
        ):
            events.append(
                {
                    "event_id": f"task_{row['id']}",
                    "source": "tasks",
                    "title": row["description"],
                    "due_date": row["due_date"],
                    "importance": row.get("importance_score", 3),
                }
            )
        for row in conn.execute(
            "SELECT id, story, priority, status FROM user_stories WHERE LOWER(status) != 'done'"
        ):
            events.append(
                {
                    "event_id": f"story_{row['id']}",
                    "source": "user_stories",
                    "title": row["story"],
                    "priority_field": row["priority"],
                    "status": row["status"],
                }
            )
        for row in conn.execute(
            "SELECT id, goal, category, target_date FROM personal_goals WHERE completed = 0"
        ):
            events.append(
                {
                    "event_id": f"goal_{row['id']}",
                    "source": "personal_goals",
                    "title": row["goal"],
                    "target_date": row["target_date"],
                    "category": row["category"],
                }
            )
    finally:
        conn.close()
    return events


def analyze_event_priority(event: Dict[str, Any]) -> Priority:
    """Return the priority for the provided raw event."""
    now = datetime.now()

    if event["source"] == "tasks":
        due = event.get("due_date")
        importance = event.get("importance", 3)
        if due:
            try:
                due_date = datetime.fromisoformat(due)
                delta = due_date - now
                if delta.total_seconds() < 0:
                    return Priority.CRITICAL
                if delta <= timedelta(hours=2):
                    return Priority.URGENT
                if delta <= timedelta(days=1) or importance >= 4:
                    return Priority.IMPORTANT
            except ValueError:
                pass
        return Priority.INFO

    if event["source"] == "user_stories":
        field = event.get("priority_field", "").lower()
        if field == "critical":
            return Priority.CRITICAL
        if field == "high":
            return Priority.URGENT
        if field == "medium":
            return Priority.IMPORTANT
        return Priority.INFO

    if event["source"] == "personal_goals":
        target = event.get("target_date")
        if target:
            try:
                target_date = datetime.fromisoformat(target)
                if target_date - now <= timedelta(days=7):
                    return Priority.IMPORTANT
            except ValueError:
                pass
        return Priority.INFO

    return Priority.BACKGROUND


class SmartScheduler:
    """Simple scheduler returning the next time slot for an event."""

    def get_slot(self, priority: Priority, now: datetime) -> datetime:
        if priority in {Priority.CRITICAL, Priority.URGENT}:
            return now
        if priority == Priority.IMPORTANT:
            slot = now.replace(hour=12, minute=0, second=0, microsecond=0)
            return slot if slot > now else now + timedelta(minutes=30)
        slot = now.replace(hour=18, minute=0, second=0, microsecond=0)
        return slot if slot > now else now + timedelta(hours=1)


def schedule_events(events: List[Event], scheduler: SmartScheduler | None = None) -> List[Event]:
    now = datetime.now()
    scheduler = scheduler or SmartScheduler()
    for ev in events:
        ev.time_to_run = scheduler.get_slot(ev.priority, now)
    events.sort(key=lambda e: (e.time_to_run, e.sort_index))
    return events


def dispatch_event(event: Event) -> None:
    """Push an event into the shared queue and notify if needed."""
    if (
        event.priority == Priority.CRITICAL
        and not (VOCAL_HOURS[0] <= datetime.now().hour <= VOCAL_HOURS[1])
    ):
        send_telegram(f"CRITICAL: {event.title}")
    heapq.heappush(EVENT_QUEUE, (event.time_to_run.timestamp(), event))


# ---------------------------------------------------------------------------
# Demo / CLI
# ---------------------------------------------------------------------------

async def main() -> None:  # pragma: no cover - manual run
    raw_events = collect_events()
    events: List[Event] = []
    for ev in raw_events:
        prio = analyze_event_priority(ev)
        event_obj = Event(
            event_id=ev["event_id"],
            source=ev["source"],
            title=ev["title"],
            priority=prio,
            time_to_run=datetime.now(),
            context_tags=[ev.get("category", "")],
            payload=ev,
        )
        events.append(event_obj)

    schedule_events(events)
    for ev in events:
        dispatch_event(ev)

    while EVENT_QUEUE:
        _, ev = heapq.heappop(EVENT_QUEUE)
        print(json.dumps(asdict(ev), ensure_ascii=False, default=str))
        trigger_trading_action(ev)


if __name__ == "__main__":
    asyncio.run(main())
