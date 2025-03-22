# app/database.py

from prisma import Prisma

# Prisma client singleton
prisma = Prisma()

async def connect_db():
      # ✅ Check if already connected
    await prisma.connect()

async def disconnect_db():
      # ✅ Avoid disconnecting if already disconnected
    await prisma.disconnect()
