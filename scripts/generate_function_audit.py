#!/usr/bin/env python3
"""Generate a simple audit of functions in the repository.

This script walks through all Python files and extracts top-level functions
with their signatures using the ``ast`` module. It then performs a naive
search across the repository to determine if each function is used
(called or imported). If no matching heading is found in ``project_doc`` or
``docs`` for a given function, a placeholder user story is produced.

Output is printed as a Markdown table.
"""

from __future__ import annotations

import ast
import os
import re
from typing import List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def list_python_files(root: str) -> List[str]:
    """Return a list of all ``.py`` files under ``root``."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden directories such as .git
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(os.path.join(dirpath, filename))
    return files


def path_to_module(path: str) -> str:
    """Convert a file path to a module path."""
    rel = os.path.relpath(path, REPO_ROOT)
    if rel.endswith("__init__.py"):
        rel = rel[: -len("__init__.py")]
    else:
        rel = rel[: -3]
    return rel.replace(os.sep, ".").strip(".")


def extract_functions(path: str) -> List[Tuple[str, str, str]]:
    """Return a list of ``(name, signature, docstring)`` for each top-level function."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    functions = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            signature = ast.unparse(node.args)
            docstring = ast.get_docstring(node) or ""
            functions.append((node.name, signature, docstring))
    return functions


def is_function_used(name: str, module: str, files: List[str], definition_path: str) -> bool:
    """Search other files for calls/imports of ``name``."""
    call_pattern = re.compile(r"\b" + re.escape(name) + r"\s*\(")
    import_pattern = re.compile(
        rf"from\s+{re.escape(module)}\s+import[^\n]*\b{re.escape(name)}\b"
    )
    for path in files:
        if path == definition_path:
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        if call_pattern.search(text) or import_pattern.search(text):
            return True
    return False


def load_doc_headings() -> List[Tuple[str, str]]:
    """Collect markdown headings from ``project_doc`` and ``docs``."""
    headings = []
    for docs_dir in ("project_doc", "docs"):
        full_dir = os.path.join(REPO_ROOT, docs_dir)
        if not os.path.isdir(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            for fname in files:
                if fname.endswith(".md"):
                    path = os.path.join(root, fname)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.startswith("#"):
                                    headings.append((line.strip().lstrip("# "), path))
                    except OSError:
                        continue
    return headings


def find_heading(name: str, headings: List[Tuple[str, str]]) -> str | None:
    name_lower = name.lower()
    for title, path in headings:
        if name_lower in title.lower():
            return f"{os.path.relpath(path, REPO_ROOT)}: {title}"
    return None


def placeholder_story(name: str, module: str) -> str:
    return (
        f"As a developer, I want `{name}` in `{module}` documented so that its "
        "purpose is clear."
    )


def main() -> None:
    py_files = list_python_files(REPO_ROOT)
    headings = load_doc_headings()

    rows = []
    for path in py_files:
        module = path_to_module(path)
        for func_name, signature, docstring in extract_functions(path):
            used = is_function_used(func_name, module, py_files, path)
            heading = find_heading(func_name, headings)
            user_story = "" if heading else placeholder_story(func_name, module)
            rows.append(
                (
                    f"{func_name}({signature})",
                    module,
                    "Yes" if used else "No",
                    heading or "Missing",
                    user_story,
                )
            )

    print("| Function | Module | Used? | Documentation | User Story |")
    print("| --- | --- | --- | --- | --- |")
    for func, mod, used, doc, story in rows:
        print(
            f"| `{func}` | `{mod}` | {used} | {doc} | {story} |"
        )


if __name__ == "__main__":
    main()
