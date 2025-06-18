import ast
import csv
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def list_py_files():
    return [p for p in REPO_ROOT.rglob('*.py') if '__pycache__' not in p.parts]


def format_signature(args: ast.arguments) -> str:
    parts = []
    defaults = [None] * (len(args.args) - len(args.defaults)) + list(args.defaults)
    for arg, default in zip(args.args, defaults):
        if default is None:
            parts.append(arg.arg)
        else:
            try:
                default_str = ast.unparse(default)
            except Exception:
                default_str = '...'
            parts.append(f"{arg.arg}={default_str}")
    if args.vararg:
        parts.append('*' + args.vararg.arg)
    kw_defaults = args.kw_defaults or []
    for arg, default in zip(args.kwonlyargs, kw_defaults):
        if default is None:
            parts.append(arg.arg)
        else:
            try:
                default_str = ast.unparse(default)
            except Exception:
                default_str = '...'
            parts.append(f"{arg.arg}={default_str}")
    if args.kwarg:
        parts.append('**' + args.kwarg.arg)
    return '(' + ', '.join(parts) + ')'


def extract_functions(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    except Exception:
        return []
    funcs = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append(node)
    return funcs


def module_import_path(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).with_suffix('')
    return '.'.join(rel.parts)


def is_used(func_name: str, module_import: str, exclude: Path, files: list[Path]) -> bool:
    call_pattern = re.compile(rf"\b{re.escape(func_name)}\s*\(")
    attr_pattern = re.compile(rf"\b{re.escape(module_import)}\.{re.escape(func_name)}\s*\(")
    import_pattern = re.compile(rf"from\s+{re.escape(module_import)}\s+import.*\b{re.escape(func_name)}\b")
    for f in files:
        if f == exclude:
            continue
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue
        if call_pattern.search(text) or attr_pattern.search(text) or import_pattern.search(text):
            return True
    return False


def find_doc_heading(name: str) -> str:
    for docs_dir in ['project_doc', 'docs']:
        base = REPO_ROOT / docs_dir
        if not base.exists():
            continue
        for md in base.rglob('*.md'):
            try:
                for line in md.read_text(encoding='utf-8').splitlines():
                    if line.lstrip().startswith('#') and name in line:
                        return line.strip()
            except Exception:
                continue
    return ''


def main():
    files = list_py_files()
    rows = []
    for file_path in files:
        funcs = extract_functions(file_path)
        mod_import = module_import_path(file_path)
        for func in funcs:
            sig = format_signature(func.args)
            doc = ast.get_docstring(func) or ''
            used = is_used(func.name, mod_import, file_path, files)
            heading = find_doc_heading(func.name)
            story = '' if heading else f"As a developer, I want documentation for `{func.name}` so I can understand its purpose."
            rows.append({
                'Function': f"{func.name}{sig}",
                'Module': str(file_path.relative_to(REPO_ROOT)),
                'Used?': 'Yes' if used else 'No',
                'Documentation': heading or '',
                'User Story': story,
            })

    # Write CSV
    csv_path = REPO_ROOT / 'function_audit.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Function', 'Module', 'Used?', 'Documentation', 'User Story'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    # Output Markdown table
    print('| Function | Module | Used? | Documentation | User Story |')
    print('|---|---|---|---|---|')
    for row in rows:
        doc = row['Documentation'] or ''
        story = row['User Story']
        print(f"| {row['Function']} | {row['Module']} | {row['Used?']} | {doc} | {story} |")


if __name__ == '__main__':
    main()
