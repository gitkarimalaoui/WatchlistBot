"""Compatibility helpers for optional runtime patches."""

from __future__ import annotations

import sys
from pathlib import Path


def patch_stockstats_for_py38() -> None:
    """Patch stockstats typing hints for Python < 3.9.

    The ``stockstats`` package uses built-in generics like ``list[int]`` which
    are only valid on Python >= 3.9. This function replaces those annotations
    with ``List[int]`` and ``Tuple[int, ...]`` so the package can be imported on
    older Python versions.
    """
    if sys.version_info >= (3, 9):
        return

    try:
        import stockstats  # type: ignore
    except Exception:
        return

    stock_file = Path(stockstats.__file__)
    try:
        text = stock_file.read_text(encoding="utf-8")
    except OSError:
        return

    modified = text
    if "list[int]" in modified or "tuple[int, ...]" in modified:
        if "from typing import Optional, Callable, Union" in modified and "Tuple" not in modified:
            modified = modified.replace(
                "from typing import Optional, Callable, Union",
                "from typing import Optional, Callable, Union, Tuple, List",
            )
        modified = modified.replace("list[int]", "List[int]")
        modified = modified.replace("tuple[int, ...]", "Tuple[int, ...]")
        try:
            stock_file.write_text(modified, encoding="utf-8")
        except OSError:
            pass

