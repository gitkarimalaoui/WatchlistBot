"""Asynchronous HTTP helpers with graceful fallback for synchronous callers.

The previous implementation created an ``asyncio.Semaphore`` at import time.
When this module was imported inside environments without a running event
loop (e.g. Streamlit's script thread) it resulted in the notorious
``RuntimeError: There is no current event loop``.  To avoid this we now create
the semaphore inside the coroutine and expose a synchronous wrapper that
manages its own event loop.
"""

from __future__ import annotations

import asyncio
import sys

import httpx
from tenacity import retry, wait_exponential_jitter, stop_after_attempt

# ---------------------------------------------------------------------------
# Platform specific setup
# ---------------------------------------------------------------------------
# On Windows/Python<=3.8, the default ProactorEventLoop can cause issues when
# used from threads.  Selecting the selector policy aligns behaviour with
# other platforms and mirrors the workaround used by many projects.
if sys.platform.startswith("win"):
    try:  # pragma: no cover - defensive, depends on platform
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:  # pragma: no cover - ignore if not available
        pass


@retry(wait=wait_exponential_jitter(2, 8), stop=stop_after_attempt(3))
async def _get(client: httpx.AsyncClient, sem: asyncio.Semaphore, url: str, **kw):
    """Internal helper performing a single GET request under a semaphore."""
    async with sem:
        r = await client.get(url, timeout=5.0, headers={"Connection": "keep-alive"}, **kw)
        r.raise_for_status()
        return r.json()


async def fetch_many(urls: list[str], concurrency: int = 12, **kw):
    """Fetch multiple URLs concurrently.

    Parameters
    ----------
    urls : list[str]
        The URLs to fetch.
    concurrency : int, optional
        Maximum number of concurrent requests, by default 12.
    kw : dict
        Extra keyword arguments forwarded to ``httpx.AsyncClient.get``.
    """
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(http2=True) as client:
        tasks = [_get(client, sem, u, **kw) for u in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)


def fetch_many_sync(urls: list[str], concurrency: int = 12, **kw):
    """Synchronous wrapper around :func:`fetch_many`.

    This is intended for environments that are not already running within an
    asyncio event loop.  It creates a private event loop, runs the coroutine
    and then closes the loop to avoid side effects.
    """
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(fetch_many(urls, concurrency=concurrency, **kw))
    finally:
        try:
            loop.run_until_complete(asyncio.sleep(0))
        except Exception:  # pragma: no cover - ignore cleanup issues
            pass
        loop.close()
        asyncio.set_event_loop(None)
