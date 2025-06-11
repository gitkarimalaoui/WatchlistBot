"""Utility functions for token counting."""

from __future__ import annotations


def count_tokens(text: str) -> int:
    """Return the number of tokens for ``text``.

    This tries to use ``llama_cpp`` or ``tiktoken`` if available. If neither
    library is installed, it falls back to a simple word count.
    """
    # Try llama_cpp first
    try:
        from llama_cpp import Llama

        # Llama.tokenize expects bytes
        return len(Llama.tokenize(text.encode("utf-8")))
    except Exception:
        pass

    # Then try tiktoken
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        pass

    # Fallback to naive whitespace split
    return len(text.split())
