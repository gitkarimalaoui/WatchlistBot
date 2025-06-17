from datetime import datetime, timedelta

import automation.orchestrateur_evenements as orch
from notifications.proactive_voice import ProactiveVoiceNotifier


def test_run_pending_announces(monkeypatch):
    notifier = ProactiveVoiceNotifier()
    spoken = []
    monkeypatch.setattr(notifier, "_speak", lambda text: spoken.append(text))
    monkeypatch.setattr(orch, "send_telegram", lambda *a, **k: None)

    event = orch.Event(
        event_id="1",
        source="test",
        title="Test event",
        priority=orch.Priority.INFO,
        time_to_run=datetime.now() - timedelta(seconds=1),
    )
    orch.dispatch_event(event)

    notifier.run_pending()
    assert spoken and "Test event" in spoken[0]
