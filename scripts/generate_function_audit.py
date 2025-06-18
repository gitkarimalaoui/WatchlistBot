import os
import ast
import re
from typing import List, Dict, Optional

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def list_python_files() -> List[str]:
    files = []
    for root, dirs, filenames in os.walk(REPO_ROOT):
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        for filename in filenames:
            if filename.endswith('.py'):
                files.append(os.path.join(root, filename))
    return files


def parse_functions(path: str) -> List[Dict[str, Optional[str]]]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=path)
    except Exception:
        return []

    functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            signature = f"{node.name}{ast.unparse(node.args)}"
            doc = ast.get_docstring(node)
            functions.append({'name': node.name, 'signature': signature, 'doc': doc})
    return functions


def load_all_text(files: List[str]) -> Dict[str, str]:
    texts = {}
    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                texts[path] = f.read()
        except Exception:
            texts[path] = ''
    return texts


def is_used(func_name: str, current_file: str, texts: Dict[str, str]) -> bool:
    pattern_call = re.compile(rf"\b{re.escape(func_name)}\s*\(")
    for path, text in texts.items():
        if path == current_file:
            continue
        if pattern_call.search(text):
            return True
        import_pattern = re.compile(rf"from\s+.*\s+import.*\b{re.escape(func_name)}\b")
        if import_pattern.search(text):
            return True
    return False


def find_doc_heading(func_name: str) -> Optional[str]:
    heading_pattern = re.compile(rf"^#+.*{re.escape(func_name)}.*", re.IGNORECASE)
    for base in ('project_doc', 'docs'):
        folder = os.path.join(REPO_ROOT, base)
        if not os.path.isdir(folder):
            continue
        for root, _, files in os.walk(folder):
            for file in files:
                if not file.endswith(('.md', '.txt')):
                    continue
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if heading_pattern.search(line):
                                return f"{line.strip()} ({os.path.relpath(path, REPO_ROOT)})"
                except Exception:
                    continue
    return None


def generate_audit() -> List[List[str]]:
    rows = []
    files = list_python_files()
    texts = load_all_text(files)
    for path in files:
        rel_path = os.path.relpath(path, REPO_ROOT)
        functions = parse_functions(path)
        for func in functions:
            used = 'Yes' if is_used(func['name'], path, texts) else 'No'
            doc = find_doc_heading(func['name'])
            user_story = ''
            if not doc:
                doc = ''
                user_story = f"As a developer, I want `{func['name']}` documented so that its purpose is clear."
            rows.append([func['signature'], rel_path, used, doc, user_story])
    return rows


def print_markdown(rows: List[List[str]]):
    print("| Function | Module | Used? | Documentation | User Story |")
    print("| --- | --- | --- | --- | --- |")
    for func, module, used, doc, story in rows:
        doc = doc.replace('|', '\\|') if doc else ''
        story = story.replace('|', '\\|') if story else ''
        print(f"| {func} | {module} | {used} | {doc} | {story} |")


def export_to_csv(rows, filename="audit_report.csv"):
    import csv
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Function", "Module", "Used?", "Documentation", "User Story"])
        writer.writerows(rows)


def export_to_md(rows, filename="audit_report.md"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("| Function | Module | Used? | Documentation | User Story |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for func, module, used, doc, story in rows:
            doc = doc.replace('|', '\\|') if doc else ''
            story = story.replace('|', '\\|') if story else ''
            f.write(f"| {func} | {module} | {used} | {doc} | {story} |\n")


def print_unused(rows: List[List[str]]):
    unused = [row for row in rows if row[2] == 'No']
    print("\n--- UNUSED FUNCTIONS ---\n")
    print_markdown(unused)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Generate function usage audit")
    parser.add_argument('--only-unused', action='store_true', help='Display only unused functions')
    parser.add_argument('--csv', default='audit_report.csv', help='CSV export filename')
    parser.add_argument('--md', default='audit_report.md', help='Markdown export filename')
    args = parser.parse_args()

    rows = generate_audit()

    if args.only_unused:
        print_unused(rows)
    else:
        print_markdown(rows)

    export_to_csv(rows, args.csv)
    export_to_md(rows, args.md)
