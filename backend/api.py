from fastapi import FastAPI, Response
from . import orchestrator

app = FastAPI()

@app.get("/watchlist/live")
async def watchlist_live():
    return await orchestrator.get_watchlist_data_for_ui()

@app.get("/watchlist/export")
async def export_watchlist():
    data = await orchestrator.get_watchlist_data_for_ui()
    return Response(orchestrator.to_csv(data), media_type="text/csv")
