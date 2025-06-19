from fastapi import FastAPI
from trading_orchestrator import TradingOrchestrator

app = FastAPI()
orchestrator = TradingOrchestrator()

@app.get("/watchlist/live")
async def live_watchlist():
    return await orchestrator.get_watchlist_data_for_ui()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
