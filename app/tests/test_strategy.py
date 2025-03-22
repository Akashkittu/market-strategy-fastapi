import unittest
import pandas as pd
from datetime import datetime, timedelta
from app.strategy import (
    calculate_moving_averages,
    moving_average_crossover_strategy,
    evaluate_strategy_performance
)

class TestStrategy(unittest.TestCase):
    def setUp(self):
        # Create 60 days of incremental data
        base = datetime(2023, 1, 1)
        self.mock_data = []
        for i in range(60):
            self.mock_data.append({
                "datetime": base + timedelta(days=i),
                "close": 100 + i * 0.5,  # steadily increasing
                "open": 100 + i * 0.4,
                "high": 100 + i * 0.6,
                "low":  100 + i * 0.3,
                "volume": 1000 + i * 10
            })

    def test_calculate_moving_averages(self):
        df = calculate_moving_averages(self.mock_data, 10, 30)
        # first 9 are NaN for ma_short, first 29 for ma_long
        self.assertTrue(pd.isna(df.iloc[0]['ma_short']))
        self.assertFalse(pd.isna(df.iloc[29]['ma_long']))

    def test_crossover_signals(self):
        df = calculate_moving_averages(self.mock_data, 10, 30)
        signals = moving_average_crossover_strategy(df)
        # Because data rises, eventually short MA > long MA
        # Ensure there's at least one BUY signal
        buys = [s for s in signals if s[1] == 'BUY']
        self.assertGreater(len(buys), 0, "No BUY signal found")

    def test_performance(self):
        df = calculate_moving_averages(self.mock_data, 10, 30)
        signals = moving_average_crossover_strategy(df)
        perf = evaluate_strategy_performance(df, signals)
        self.assertIn('total_buys', perf)
        self.assertIn('profit_estimate', perf)

if __name__ == '__main__':
    unittest.main()
