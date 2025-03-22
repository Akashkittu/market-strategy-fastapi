# app/tests/test_db.py

import unittest
import asyncio
from app.database import prisma, connect_db, disconnect_db
from datetime import datetime

class TestDatabase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await connect_db()
        # Clear table
        await prisma.pricedata.delete_many()

    async def asyncTearDown(self):
        await prisma.pricedata.delete_many()
        await disconnect_db()

    async def test_create_and_read(self):
        """
        Insert a record and verify it is fetched.
        """
        inserted = await prisma.pricedata.create(
            data={
                "datetime": datetime(2023,1,1,10,0,0),
                "open": "100.0",
                "high": "101.0",
                "low": "99.5",
                "close": "100.5",
                "volume": 500
            }
        )
        self.assertIsNotNone(inserted.id)

        records = await prisma.pricedata.find_many()
        self.assertEqual(len(records), 1)
        self.assertEqual(float(records[0].open), 100.0)

if __name__ == '__main__':
    unittest.main()
