import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
from prisma import Prisma

# ✅ Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"✅ DATABASE_URL Loaded: {DATABASE_URL}")  # Debugging step

async def insert_data():
    prisma = Prisma()
    await prisma.connect()  # ✅ Ensure connection to PostgreSQL

    print("✅ Connected to Database Successfully!")

    # Load the Excel file
    file_path = r"C:\Users\Akash\Downloads\project1\invsto_assignment\HINDALCO_1D.xlsx"
    df = pd.read_excel(file_path)

    # Rename columns to match PostgreSQL schema
    df = df.rename(columns={"datetime": "datetime", "open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume"})
    df = df[["datetime", "open", "high", "low", "close", "volume"]]  # Drop extra columns

    # ✅ Use correct model name (`PriceData`)
    for _, row in df.iterrows():
        
        # ✅ FIX: Use correct model name
        await prisma.pricedata.create( 
            data={
                "datetime": row["datetime"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": int(row["volume"]),  # Ensure volume is an integer
            }
        )

    await prisma.disconnect()
    print("✅ Data successfully inserted into PostgreSQL!")

# ✅ Run the async function
asyncio.run(insert_data())
