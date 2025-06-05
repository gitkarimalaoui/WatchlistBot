
# 📘 EPIC 27 – Project & Productivity Management

## 🎯 Objective

This module empowers the user to monitor all EPICs, user stories, technical tasks, and tests. It supports Agile (Scrum) methods with persistent status tracking, integrated reminders, and daily operational efficiency via Telegram notifications.

## 🧠 IA Recommendations

An internal project management loop is essential to maintain code consistency, sprint discipline, and roadmap alignment with business goals. IA can help detect overdue stories, suggest improvements, and track test coverage.

## 🧩 Approach

- Create structured database with epics, US, tasks, tests
- Track progress and critical paths via interface
- Daily notifications via Telegram
- Integration with BOTV7 streamlit dashboard

---

## 🗃️ Database Tables

| Table        | Description                                 |
|--------------|---------------------------------------------|
| `epics`      | Core project-level units with statuses      |
| `user_stories` | Agile feature tracking                    |
| `tasks`      | Technical or management work units          |
| `tests`      | Test suite linked to tasks or US            |

---

## 📜 User Stories

➡️ See: [`bpmn_epic_27_project_productivity.xlsx`](../user_stories/bpmn_epic_27_project_productivity.xlsx)

---

## 📊 Diagramme BPMN

![BPMN – EPIC 27](../images/bpmn_epic_27_project_productivity.png)

---

## ⚙️ Critical Conditions

- If a task is overdue, send notification
- If test fails, log and notify with reason
- If all US are marked done → mark EPIC as completed

---

## 🧠 Prompt used

```plaintext
Design a BPMN for an internal Agile + productivity manager that includes:
- epic tracking
- user story validation
- technical & daily tasks
- test verification
- reminders via Telegram
```

---

## ⚠️ Known Limits

- No Kanban drag-and-drop yet
- Reminders limited to fixed time window

---

## 🔁 Cross-References

| Linked Feature        | EPIC             |
|-----------------------|------------------|
| Code Documentation    | EPIC 05          |
| Test Engine           | EPIC 13          |
| Learning Cycle Logs   | EPIC 16          |
| Dashboard Alerts      | EPIC 20          |

---

## 💡 Key Lesson

Managing your roadmap is not an overhead — it's your most valuable asset for productivity, control and clarity.

---

## 📋 User Stories Extract

### 📋 Extract – User Stories List (Top 10)

| ID | User Story | Status | Priority |
|----|-------------|--------|----------|
| US-PP-001 | As a Project Manager, I want to track it... | In Progress | High |
| US-PP-002 | As a Project Manager, I want to track it... | Done | High |
| US-PP-003 | As a Project Manager, I want to track it... | Ready | High |
| US-PP-004 | As a Project Manager, I want to track it... | To Do | High |
| US-PP-005 | As a Project Manager, I want to track it... | In Progress | High |
| US-PP-006 | As a Project Manager, I want to track it... | Done | High |
| US-PP-007 | As a Project Manager, I want to track it... | Ready | High |
| US-PP-008 | As a Project Manager, I want to track it... | To Do | High |
| US-PP-009 | As a Project Manager, I want to track it... | In Progress | High |
| US-PP-010 | As a Project Manager, I want to track it... | Done | High |


Full list: [USER_STORIES_PROJECT_PRODUCTIVITY.xlsx](../user_stories/bpmn_epic_27_project_productivity.xlsx)

---

## 🧠 Linked Modules

- `task_manager.py` → core logic to manage tasks/US/tests
- `daily_telegram_check.py` → send smart Telegram reminders
- `epic_status.db` → stores full state of EPICs, tasks, US and test coverage

---

## 🔁 Flow Summary

Each user story can contain:
- ✅ One or more technical or operational tasks
- 🧪 Each task may be linked to one or more validation tests
- 🔔 Tasks with `reminder = True` will trigger a daily notification

