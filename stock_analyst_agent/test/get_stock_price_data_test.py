import unittest
from unittest.mock import patch

import numpy as np

import pandas as pd

from stock_analyst_agent.src.tools import get_stock_price_data


class TestGetStockPriceData(unittest.TestCase):

    @patch('yfinance.Ticker')
    def test_get_stock_price_data_empty_data(self, mock_ticker):
        ticker = 'AAPL'
        period = 1
        period_unit = 'd'
        mock_ticker.return_value.history.return_value = pd.DataFrame()
        result = get_stock_price_data(ticker, period, period_unit)
        self.assertIsNone(result)

    def test_get_stock_price_data_invalid_period_unit(self):
        ticker = 'AAPL'
        period = 1
        period_unit = 'm'
        with self.assertRaises(ValueError):
            get_stock_price_data(ticker, period, period_unit)

    @patch('yfinance.Ticker')
    def test_get_stock_price_data_no_period(self, mock_ticker):
        ticker = 'AAPL'
        np.random.seed(42)
        data = {
            'Date': pd.date_range(start='2025-01-01', periods=10, freq='D'),
            'Stock': ticker,
            'Close_Price': np.random.uniform(100, 500, 10),
            'Volume': np.random.randint(1000000, 5000000, 10),
            'Change_%': np.random.uniform(-5, 5, 10)
        }
        mock_ticker.return_value.history.return_value = pd.DataFrame(data)
        result = get_stock_price_data(ticker=ticker)
        self.assertIsNotNone(result)

    @patch('yfinance.Ticker')
    def test_get_stock_price_data_exception(self, mock_ticker):
        ticker = 'AAPL'
        period = 1
        period_unit = 'd'
        mock_ticker.return_value.history.side_effect = Exception('Error')
        with self.assertRaises(Exception) as context:
            get_stock_price_data(ticker, period, period_unit)
        self.assertEqual(str(context.exception), "Error")

if __name__ == '__main__':
    unittest.main()