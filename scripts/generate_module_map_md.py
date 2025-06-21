import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODULE_JSON_PATH = ROOT / 'module_map.json'
OUTPUT_MD = ROOT / 'MODULE_MAP.md'

# Load module map
with MODULE_JSON_PATH.open() as f:
    module_data = json.load(f)

rows = []
for module, info in sorted(module_data.items()):
    path = ROOT / module
    funcs = []
    notifications = False
    ai_features = []
    if path.is_file():
        try:
            tree = ast.parse(path.read_text())
        except Exception:
            tree = None
        if tree:
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    params = [arg.arg for arg in node.args.args]
                    ret = None
                    if node.returns:
                        ret = getattr(ast, 'unparse', lambda x: None)(node.returns) if hasattr(ast, 'unparse') else None
                    sig = f"{node.name}({', '.join(params)})"
                    if ret:
                        sig += f" -> {ret}"
                    funcs.append(sig)
            # Detect notification calls
            src = path.read_text()
            if 'send_telegram_message' in src or 'telegram_bot' in src:
                notifications = True
            # Detect AI usage
            if 'intelligence' in src or 'openai' in src or 'transformers' in src:
                ai_features.append('ai')
    funcs_str = '; '.join(funcs)
    deps = ', '.join(info.get('imports', []))
    used_by = ', '.join(info.get('used_by', []))
    db = 'yes' if info.get('db_access') else 'no'
    notif = 'yes' if notifications else 'no'
    ai = 'yes' if ai_features else 'no'
    rows.append({'module': module, 'inputs_outputs': funcs_str, 'dependencies': deps,
                 'used_by': used_by, 'db': db, 'notify': notif, 'ai': ai})

# Build markdown
lines = ["# Module Map", '', '| Module | Inputs/Outputs | Dependencies | Used By | DB | Notify | AI |', '|-------|---------------|-------------|--------|----|-------|----|']
for row in rows:
    lines.append(f"| {row['module']} | {row['inputs_outputs']} | {row['dependencies']} | {row['used_by']} | {row['db']} | {row['notify']} | {row['ai']} |")

OUTPUT_MD.write_text('\n'.join(lines))
