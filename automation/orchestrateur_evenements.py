from __future__ import annotations

import asyncio
import heapq
import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, time, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from utils.db_access import (
    PROJECT_DB_PATH,
    TRADES_DB_PATH,
    fetch_tasks,
    fetch_user_stories,
    fetch_personal_goals,
    fetch_trade_alerts,
)
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
    """Send a Telegram message if credentials are available.

    Args:
        text (str): Message body to send.
    """
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
    """Trigger a trading order based on the provided event.

    See ``project_doc/MODULE_1_ORCHESTRATEUR_EVENEMENTS.md`` for the
    sequence of operations leading to this call.

    Args:
        event (Event): Planned event potentially containing trading tags.
    """
    if "trading" in event.context_tags:
        logger.info("[TRADING] Action triggered for %s", event.title)


# ---------------------------------------------------------------------------
# Event collection and analysis
# ---------------------------------------------------------------------------

def collect_events(
    project_db: Path = PROJECT_DB_PATH, trades_db: Path = TRADES_DB_PATH
) -> List[Dict[str, Any]]:
    """Load raw events from available SQLite databases.

    Detailed steps for this process are described in
    ``project_doc/MODULE_1_ORCHESTRATEUR_EVENEMENTS.md``.

    Args:
        project_db (Path): Path to the project database.
        trades_db (Path): Path to the trades database.

    Returns:
        List[Dict[str, Any]]: Unprocessed event dictionaries.
    """

    events: List[Dict[str, Any]] = []

    for row in fetch_tasks(project_db):
        events.append(
            {
                "event_id": f"task_{row['id']}",
                "source": "tasks",
                "title": row["description"],
                "due_date": row.get("due_date"),
                "importance": row.get("importance_score", 3),
            }
        )

    for row in fetch_user_stories(project_db):
        events.append(
            {
                "event_id": f"story_{row['id']}",
                "source": "user_stories",
                "title": row["story"],
                "priority_field": row.get("priority"),
                "status": row.get("status"),
            }
        )

    for row in fetch_personal_goals(project_db):
        events.append(
            {
                "event_id": f"goal_{row['id']}",
                "source": "personal_goals",
                "title": row["goal"],
                "target_date": row.get("target_date"),
                "category": row.get("category"),
            }
        )

    for row in fetch_trade_alerts(trades_db):
        events.append(
            {
                "event_id": f"trade_{row['ticker']}",
                "source": "watchlist",
                "title": row["ticker"],
                "score": row.get("score", 0),
                "change_percent": row.get("change_percent", 0.0),
            }
        )

    return events


def analyze_event_priority(event: Dict[str, Any]) -> Priority:
    """Return the priority for the provided raw event.

    The logic mirrors the description in
    ``project_doc/MODULE_1_ORCHESTRATEUR_EVENEMENTS.md``.

    Args:
        event (Dict[str, Any]): Raw event data.

    Returns:
        Priority: Computed priority level.
    """
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

    if event["source"] == "watchlist":
        score = float(event.get("score", 0))
        change = float(event.get("change_percent", 0))
        if score >= 9 or change >= 10:
            return Priority.URGENT
        if score >= 7:
            return Priority.IMPORTANT
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


def schedule_events(
    events: List[Event], scheduler: Optional[SmartScheduler] = None
) -> List[Event]:
    """Assign execution slots to events and sort them.

    Args:
        events (List[Event]): Events whose ``time_to_run`` should be set.
        scheduler (SmartScheduler | None): Custom scheduler, defaults to a
            :class:`SmartScheduler` instance.

    Returns:
        List[Event]: The list sorted by run time and priority.
    """

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
