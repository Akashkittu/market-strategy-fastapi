# app/tests/test_api.py

import unittest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import prisma, connect_db, disconnect_db


class TestAPI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await connect_db()
        if not prisma.is_connected():
            await prisma.connect()
        await prisma.pricedata.delete_many()

    async def asyncTearDown(self):
        if not prisma.is_connected():
            await prisma.connect()
        await prisma.pricedata.delete_many()
        await disconnect_db()


    async def test_get_data_empty(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/data")
            self.assertEqual(response.status_code, 404)  # Since empty returns 404
            self.assertEqual(response.json(), {"detail": "No price data found"})

    async def test_post_data_and_fetch(self):
        candles = [{
            "datetime": "2023-01-01T10:00:00",
            "open": 100.0,
            "high": 101.0,
            "low": 99.5,
            "close": 100.5,
            "volume": 500
        }]
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            post_resp = await client.post("/data", json=candles)
            self.assertEqual(post_resp.status_code, 200)
            self.assertEqual(post_resp.json()["inserted_count"], 1)

            get_resp = await client.get("/data")
            self.assertEqual(get_resp.status_code, 200)
            data = get_resp.json()
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["volume"], 500)

    async def test_strategy_performance(self):
        sample_payload = [
            {
                "datetime": "2023-01-01T10:00:00",
                "open": 100.0,
                "high": 101.0,
                "low": 99.5,
                "close": 100.5,
                "volume": 500
            },
            {
                "datetime": "2023-01-02T10:00:00",
                "open": 101.0,
                "high": 102.0,
                "low": 100.0,
                "close": 101.5,
                "volume": 600
            },
            {
                "datetime": "2023-01-03T10:00:00",
                "open": 102.0,
                "high": 103.0,
                "low": 101.0,
                "close": 102.5,
                "volume": 700
            }
        ]
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post("/data", json=sample_payload)
            response = await client.get("/strategy/performance")
            self.assertEqual(response.status_code, 200)
            self.assertIn("performance", response.json())
            self.assertIn("signals", response.json())


if __name__ == '__main__':
    unittest.main()
