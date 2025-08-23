import asyncio
import httpx
from tenacity import retry, wait_exponential_jitter, stop_after_attempt

SEM = asyncio.Semaphore(12)

@retry(wait=wait_exponential_jitter(2, 8), stop=stop_after_attempt(3))
async def _get(client: httpx.AsyncClient, url: str, **kw):
    async with SEM:
        r = await client.get(url, timeout=5.0, headers={"Connection": "keep-alive"}, **kw)
        r.raise_for_status()
        return r.json()

async def fetch_many(urls: list[str]):
    async with httpx.AsyncClient(http2=True) as client:
        return await asyncio.gather(*(_get(client, u) for u in urls), return_exceptions=True)
