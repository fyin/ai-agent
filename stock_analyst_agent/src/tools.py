import matplotlib.pyplot as plt
import talib
import yfinance as yf
import logging
from pandas import DataFrame
from typing import Union
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def get_stock_price_data(ticker: str, period: int =6, period_unit: str = 'mo') -> Union[DataFrame, str]:
    """
    Fetches stock price historical data for a given ticker and period.
    :param ticker: The ticker of the stock.
    :param period: The number of periods to fetch data for.
    :param period_unit: The unit of the period. Must be 'd' (days), 'mo' (months), or 'y' (years).
    If no period is provided, it defaults to 6 months.
    If no period_unit is provided, it defaults to 'mo'.
    """
    if period_unit not in ['d', 'mo', 'y']:
        raise ValueError("Invalid period unit. Must be 'd' (days), 'mo' (months), or 'y' (years).")
    else:
        period_with_unit = f'{period}{period_unit}'

    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period_with_unit)
        if data.empty:
            logger.warning(f"No data found for stock: {ticker}.")
            return None
        return data
    except Exception as e:
        logger.error(f"Error fetching data for stock: {ticker}.", e)
        raise e


def get_technical_analysis(ticker: str) -> Tuple[Dict[str, Any], DataFrame]:
    """
    Calculate technical analysis indicators for a given stock historical data.
    :param df: stock historical data in dataframe
    """
    df = get_stock_price_data(ticker)
    if df is None:
       raise ValueError(f"Dataframe is empty for stock: {ticker}")

    analysis = {}
    # Moving Averages
    analysis['SMA_50'] = talib.SMA(df['Close'], timeperiod=50)
    analysis['SMA_200'] = talib.SMA(df['Close'], timeperiod=200)
    # For plot
    df['SMA_50'] = analysis['SMA_50']
    df['SMA_200'] = analysis['SMA_200']

    # Support and Resistance
    analysis['Support'] = df['Low'].rolling(window=14).min().iloc[-1]
    analysis['Resistance'] = df['High'].rolling(window=14).max().iloc[-1]

    # Relative Strength Index
    analysis['RSI'] = talib.RSI(df['Close'], timeperiod=14).iloc[-1]
    # Calculate MACD
    macd, macd_signal, _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    analysis['MACD'] = macd.iloc[-1]
    analysis['MACD_Signal'] = macd_signal.iloc[-1]

    return analysis, df

def get_valuation_measures(ticker: str) -> Union[Dict, str]:
    """Fetches key valuation measures for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "Current Price": info.get("currentPrice"),
            "Market Cap": info.get("marketCap"),
            "PE Ratio": info.get("trailingPE"),
            "52 Week High": info.get("fiftyTwoWeekHigh"),
            "52 Week Low": info.get("fiftyTwoWeekLow"),
            "pe_ratio": info.get("forwardPE"),
            "price_to_book": info.get("priceToBook"),
            "debt_to_equity": info.get("debtToEquity"),
            "profit_margins": info.get("profitMargins")
        }
    except Exception as e:
        logger.error(f"Error fetching ratios for stock: {ticker}.", e)
        raise e

def plot_stock_data(ticker: str):
    """
    Plot stock data
    """
    _,df = get_technical_analysis(ticker)
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price', color='blue')
    plt.plot(df['SMA_50'], label='50-Day SMA', color='orange')
    plt.plot(df['SMA_200'], label='200-Day SMA', color='red')

    plt.title(f'{ticker} Stock Price with 50-Day and 200-Day SMA')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == '__main__':
    stock_ticker = 'tsla'
    metrics = get_valuation_measures(stock_ticker)
    print(metrics)
    plot_stock_data(stock_ticker)