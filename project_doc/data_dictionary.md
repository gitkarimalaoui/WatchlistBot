# 📘 Data Dictionary

## trades.db
### Table: watchlist
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | False | None | True |
| ticker | TEXT | False | None | False |
| last_price | REAL | False | None | False |
| volume | INTEGER | False | None | False |
| float | INTEGER | False | None | False |
| change_percent | REAL | False | None | False |
| score | REAL | False | None | False |
| source | TEXT | False | None | False |
| date | TEXT | False | None | False |
| description | TEXT | False | None | False |
| updated_at | DATETIME | False | None | False |

### Table: sqlite_sequence
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| name |  | False | None | False |
| seq |  | False | None | False |

### Table: news_score
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| symbol | TEXT | False | None | True |
| summary | TEXT | False | None | False |
| score | INTEGER | False | None | False |
| timestamp | DATETIME | False | CURRENT_TIMESTAMP | False |
| last_analyzed | DATETIME | False | None | False |
| desc_hash | TEXT | False | None | False |
| sentiment | TEXT | False | None | False |

### Table: personal_goals
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | False | None | True |
| goal | TEXT | True | None | False |
| category | TEXT | False | None | False |
| created_at | DATETIME | False | CURRENT_TIMESTAMP | False |
| completed | BOOLEAN | False | 0 | False |

## project_tracker.db
### Table: epics
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | TEXT | False | None | True |
| label | TEXT | False | None | False |

### Table: user_stories
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | TEXT | False | None | True |
| epic | TEXT | False | None | False |
| story | TEXT | False | None | False |
| criteria | TEXT | False | None | False |
| module | TEXT | False | None | False |
| priority | TEXT | False | None | False |
| status | TEXT | False | None | False |
| testable | TEXT | False | None | False |

### Table: tasks
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | False | None | True |
| us_id | TEXT | False | None | False |
| description | TEXT | False | None | False |
| due_date | TEXT | False | None | False |
| done | INTEGER | False | None | False |
| reminder | INTEGER | False | None | False |

### Table: sqlite_sequence
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| name |  | False | None | False |
| seq |  | False | None | False |

### Table: personal_goals
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | False | None | True |
| goal | TEXT | True | None | False |
| category | TEXT | False | None | False |
| created_at | DATETIME | False | CURRENT_TIMESTAMP | False |
| completed | BOOLEAN | False | 0 | False |
