import asyncio

async def to_thread(func, *args, **kwargs):
    if hasattr(asyncio, "to_thread"):
        return await asyncio.to_thread(func, *args, **kwargs)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)
