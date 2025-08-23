#!/usr/bin/env python
import subprocess as sp, json, pathlib, sys

REPORTS = pathlib.Path("reports")
REPORTS.mkdir(parents=True, exist_ok=True)

def run(cmd: str):
    print(f"→ {cmd}")
    p = sp.run(cmd, shell=True, text=True, capture_output=True)
    return {"cmd": cmd, "code": p.returncode, "out": p.stdout, "err": p.stderr}

results = {
    "ruff": run("ruff check ."),
    "mypy": run("mypy src || true"),
    "pytest": run("pytest || true"),
    "bandit": run("bandit -r src -lll || true"),
    "pip-audit": run("pip-audit --strict || true"),
    "deps": run("pipdeptree || true"),
}

(REPORTS / "audit.json").write_text(
    json.dumps({k: {"code": v["code"]} for k, v in results.items()}, indent=2),
    encoding="utf-8",
)

def block(res): return f"### {res['cmd']}\n\n```\n{res['out']}\n{res['err']}\n```\n"
md = ["# Audit WatchlistBot — Résultats\n"]
for k, v in results.items(): md.append(f"## {k}\n{block(v)}")
(REPORTS / "audit.md").write_text("\n".join(md), encoding="utf-8")
print("✔ Rapport écrit dans reports/audit.md")
sys.exit(0)
