from fastapi import FastAPI, Response
from backend import orchestrator
from utils.sanitize import sanitize_float_values

app = FastAPI()

@app.get("/watchlist/live")
async def live_watchlist():
    data = await orchestrator.get_watchlist_data_for_ui()
    return sanitize_float_values(data)

@app.get("/watchlist/export")
async def export_watchlist():
    data = await orchestrator.get_watchlist_data_for_ui()
    return Response(orchestrator.to_csv(data), media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
