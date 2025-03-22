# app/main.py

from fastapi import FastAPI, HTTPException
from prisma import Prisma
from .database import prisma, connect_db, disconnect_db
from .models import PriceDataIn, PriceDataOut
from .strategy import (
    calculate_moving_averages,
    moving_average_crossover_strategy,
    evaluate_strategy_performance
)
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Invsto FastAPI!"}
app = FastAPI(
    title="Invsto Assignment",
    description="FastAPI + Prisma + PostgreSQL for Candle Data",
    version="1.0.0"
)

# -- Connect & Disconnect DB on Startup/Shutdown --
@app.on_event("startup")
async def startup_event():
    await connect_db()  # Existing function
    if not prisma.is_connected():  # ✅ Check if already connected
        await prisma.connect()  # ✅ Ensure Prisma is connected


@app.on_event("shutdown")
async def shutdown_event():
    await disconnect_db()

# -----------------------------
# GET /data -> Fetch all records
# -----------------------------
@app.get("/data", response_model=list[PriceDataOut])
async def get_data():
    """
    Returns all candle records from the database, sorted by datetime.
    """
    if not prisma.is_connected():  # ✅ Avoid redundant connection
        await prisma.connect()  # ✅ Ensure connection before fetching

    records = await prisma.pricedata.find_many(order={'datetime': 'asc'})

    await prisma.disconnect()  # ✅ Disconnect after fetching

    if not records:
        raise HTTPException(status_code=404, detail="No price data found")

    return [
        PriceDataOut(
            datetime=r.datetime,
            open=float(r.open),
            high=float(r.high),
            low=float(r.low),
            close=float(r.close),
            volume=r.volume
        )
        for r in records
    ]

# -----------------------------
# POST /data -> Insert records
# -----------------------------
@app.post("/data")
async def post_data(payload: list[PriceDataIn]):
    """
    Insert multiple candle records into the database.
    """
    inserted_count = 0
    for record in payload:
        # Insert using Prisma
        await prisma.pricedata.create(
            data={
                "datetime": record.datetime,
                "open": str(record.open),
                "high": str(record.high),
                "low": str(record.low),
                "close": str(record.close),
                "volume": record.volume
            }
        )
        inserted_count += 1

    return {"inserted_count": inserted_count, "status": "success"}

# ----------------------------------------------------------
# GET /strategy/performance -> Evaluate MA crossover strategy
# ----------------------------------------------------------
@app.get("/strategy/performance")
async def get_performance(short_window: int = 10, long_window: int = 30):
    """
    Returns signals and performance of a moving average crossover strategy.
    """
    if not prisma.is_connected():
        await prisma.connect()
    records = await prisma.pricedata.find_many(order={'datetime': 'asc'})
    if not records:
        raise HTTPException(status_code=404, detail="No price data found")

    # Convert decimal fields to float for calculations
    data_list = []
    for r in records:
        data_list.append({
            "datetime": r.datetime,
            "close": float(r.close),
            "open": float(r.open),
            "high": float(r.high),
            "low": float(r.low),
            "volume": r.volume
        })

    df = calculate_moving_averages(data_list, short_window, long_window)
    signals = moving_average_crossover_strategy(df)
    performance = evaluate_strategy_performance(df, signals)

    return {
        "short_window": short_window,
        "long_window": long_window,
        "total_records": len(records),
        "signals": signals,
        "performance": performance
    }
