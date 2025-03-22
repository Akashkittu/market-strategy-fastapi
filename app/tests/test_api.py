# app/tests/test_api.py

import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database import prisma, connect_db, disconnect_db

client = TestClient(app)

class TestAPI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Connect to DB, clear table before each test
        await connect_db()
        await prisma.pricedata.delete_many()

    async def asyncTearDown(self):
        # Clean up after each test
        await prisma.pricedata.delete_many()
        await disconnect_db()

    def test_get_data_empty(self):
        """
        Should return an empty list when no records in DB.
        """
        response = client.get("/data")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_post_data_and_fetch(self):
        """
        POST some records and then GET them.
        """
        candles = [{
            "datetime": "2023-01-01T10:00:00",
            "open": 100.0,
            "high": 101.0,
            "low": 99.5,
            "close": 100.5,
            "volume": 500
        }]
        post_resp = client.post("/data", json=candles)
        self.assertEqual(post_resp.status_code, 200)
        self.assertEqual(post_resp.json()["inserted_count"], 1)

        # Now check GET /data
        get_resp = client.get("/data")
        self.assertEqual(get_resp.status_code, 200)
        data = get_resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["volume"], 500)

    def test_strategy_performance(self):
        """
        Insert sample data and call /strategy/performance.
        """
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
        client.post("/data", json=sample_payload)
        response = client.get("/strategy/performance")
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
