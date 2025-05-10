import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TechnicalAnalysis:
    """
    Class for performing technical analysis on stock data
    """
    
    def __init__(self, ticker):
        """
        Initialize TechnicalAnalysis with a ticker symbol
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol (e.g., 'AAPL' for Apple)
        """
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
    
    def get_historical_data(self, timeframe='1y'):
        """
        Get historical price data
        
        Parameters:
        -----------
        timeframe : str
            Time period for historical data (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
        
        Returns:
        --------
        pandas.DataFrame
            Historical stock data
        """
        try:
            data = self.stock.history(period=timeframe)
            if data is None or isinstance(data, dict):
                return pd.DataFrame()
            return data
        except Exception as e:
            print(f"Error fetching historical data for {self.ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_moving_averages(self, timeframe='1y'):
        """
        Calculate moving averages for the stock
        
        Parameters:
        -----------
        timeframe : str
            Time period for historical data
        
        Returns:
        --------
        pandas.DataFrame
            Dataframe with stock prices and moving averages
        """
        # Get historical data
        data = self.get_historical_data(timeframe)
        
        if data.empty:
            return pd.DataFrame()
        
        # Calculate moving averages
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA50'] = data['Close'].rolling(window=50).mean()
        data['MA200'] = data['Close'].rolling(window=200).mean()
        
        return data
    
    def interpret_moving_averages(self):
        """
        Interpret moving average signals
        
        Returns:
        --------
        dict
            Dictionary of moving average signals and their interpretations
        """
        # Get data with moving averages
        data = self.get_moving_averages('1y')
        
        if data.empty or len(data) < 200:  # Need at least 200 days for 200MA
            return {'Insufficient Data': 'Not enough historical data for moving average analysis'}
        
        # Get latest values
        latest = data.iloc[-1]
        close = latest['Close']
        ma20 = latest['MA20']
        ma50 = latest['MA50']
        ma200 = latest['MA200']
        
        signals = {}
        
        # Price vs. MA20
        if close > ma20:
            signals['Short-term Trend'] = 'Bullish: Price above 20-day MA'
        else:
            signals['Short-term Trend'] = 'Bearish: Price below 20-day MA'
        
        # Price vs. MA50
        if close > ma50:
            signals['Medium-term Trend'] = 'Bullish: Price above 50-day MA'
        else:
            signals['Medium-term Trend'] = 'Bearish: Price below 50-day MA'
        
        # Price vs. MA200
        if close > ma200:
            signals['Long-term Trend'] = 'Bullish: Price above 200-day MA'
        else:
            signals['Long-term Trend'] = 'Bearish: Price below 200-day MA'
        
        # Golden Cross / Death Cross (MA50 vs MA200)
        # Check for recent crossing
        last_5_days = data.tail(5)
        cross_detected = False
        
        for i in range(1, len(last_5_days)):
            prev_day = last_5_days.iloc[i-1]
            curr_day = last_5_days.iloc[i]
            
            # Check for Golden Cross (MA50 crosses above MA200)
            if prev_day['MA50'] <= prev_day['MA200'] and curr_day['MA50'] > curr_day['MA200']:
                signals['Major Signal'] = 'Bullish: Recent Golden Cross (50-day MA crossed above 200-day MA)'
                cross_detected = True
                break
            
            # Check for Death Cross (MA50 crosses below MA200)
            if prev_day['MA50'] >= prev_day['MA200'] and curr_day['MA50'] < curr_day['MA200']:
                signals['Major Signal'] = 'Bearish: Recent Death Cross (50-day MA crossed below 200-day MA)'
                cross_detected = True
                break
        
        # Current relationship between MA50 and MA200
        if not cross_detected:
            if ma50 > ma200:
                signals['MA Relationship'] = 'Bullish: 50-day MA above 200-day MA'
            else:
                signals['MA Relationship'] = 'Bearish: 50-day MA below 200-day MA'
        
        return signals
    
    def get_rsi(self, timeframe='1y', window=14):
        """
        Calculate Relative Strength Index (RSI)
        
        Parameters:
        -----------
        timeframe : str
            Time period for historical data
        window : int
            RSI calculation window (default is 14 days)
        
        Returns:
        --------
        pandas.DataFrame
            Dataframe with RSI values
        """
        # Get historical data
        data = self.get_historical_data(timeframe)
        
        if data.empty:
            return pd.DataFrame()
        
        # Calculate daily price changes
        delta = data['Close'].diff()
        
        # Separate gains and losses
        gain = delta.copy()
        loss = delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        loss = abs(loss)
        
        # Calculate average gain and loss over specified window
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        # Calculate RS (Relative Strength)
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        # Create result dataframe
        result = pd.DataFrame(index=data.index)
        result['Close'] = data['Close']
        result['RSI'] = rsi
        
        return result
    
    def get_macd(self, timeframe='1y', fast=12, slow=26, signal=9):
        """
        Calculate Moving Average Convergence Divergence (MACD)
        
        Parameters:
        -----------
        timeframe : str
            Time period for historical data
        fast : int
            Fast EMA period
        slow : int
            Slow EMA period
        signal : int
            Signal line period
        
        Returns:
        --------
        pandas.DataFrame
            Dataframe with MACD values
        """
        # Get historical data
        data = self.get_historical_data(timeframe)
        
        if data.empty:
            return pd.DataFrame()
        
        # Calculate EMAs
        ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        # Create result dataframe
        result = pd.DataFrame(index=data.index)
        result['Close'] = data['Close']
        result['MACD'] = macd_line
        result['Signal'] = signal_line
        result['Histogram'] = histogram
        
        return result
    
    def interpret_macd(self):
        """
        Interpret MACD signals
        
        Returns:
        --------
        str
            MACD signal interpretation
        """
        # Get MACD data
        macd_data = self.get_macd('1y')
        
        if macd_data.empty:
            return "Insufficient data for MACD analysis"
        
        # Get latest values
        latest = macd_data.iloc[-1]
        macd = latest['MACD']
        signal = latest['Signal']
        histogram = latest['Histogram']
        
        # Get previous values for trend
        if len(macd_data) > 1:
            prev = macd_data.iloc[-2]
            prev_histogram = prev['Histogram']
            histogram_trend = histogram - prev_histogram
        else:
            histogram_trend = 0
        
        # Interpret signals
        if macd > signal and histogram > 0:
            if histogram_trend > 0:
                return "Bullish: MACD above signal line with increasing momentum"
            else:
                return "Bullish: MACD above signal line but momentum may be slowing"
        elif macd < signal and histogram < 0:
            if histogram_trend < 0:
                return "Bearish: MACD below signal line with increasing downward momentum"
            else:
                return "Bearish: MACD below signal line but downward momentum may be slowing"
        elif macd > signal and histogram_trend > 0:
            return "Bullish: MACD just crossed above signal line (bullish crossover)"
        elif macd < signal and histogram_trend < 0:
            return "Bearish: MACD just crossed below signal line (bearish crossover)"
        else:
            return "Neutral: No clear MACD signal at the moment"
    
    def get_bollinger_bands(self, timeframe='1y', window=20, num_std=2):
        """
        Calculate Bollinger Bands
        
        Parameters:
        -----------
        timeframe : str
            Time period for historical data
        window : int
            Moving average window
        num_std : int
            Number of standard deviations for bands
        
        Returns:
        --------
        pandas.DataFrame
            Dataframe with Bollinger Bands
        """
        # Get historical data
        data = self.get_historical_data(timeframe)
        
        if data.empty:
            return pd.DataFrame()
        
        # Calculate middle band (SMA)
        middle_band = data['Close'].rolling(window=window).mean()
        
        # Calculate standard deviation
        std = data['Close'].rolling(window=window).std()
        
        # Calculate upper and lower bands
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        
        # Create result dataframe
        result = pd.DataFrame(index=data.index)
        result['Close'] = data['Close']
        result['Middle Band'] = middle_band
        result['Upper Band'] = upper_band
        result['Lower Band'] = lower_band
        
        return result
    
    def interpret_bollinger_bands(self):
        """
        Interpret Bollinger Bands signals
        
        Returns:
        --------
        str
            Bollinger Bands signal interpretation
        """
        # Get Bollinger Bands data
        bb_data = self.get_bollinger_bands('1y')
        
        if bb_data.empty:
            return "Insufficient data for Bollinger Bands analysis"
        
        # Get latest values
        latest = bb_data.iloc[-1]
        close = latest['Close']
        middle = latest['Middle Band']
        upper = latest['Upper Band']
        lower = latest['Lower Band']
        
        # Calculate bandwidth and %B
        bandwidth = (upper - lower) / middle
        percent_b = (close - lower) / (upper - lower) if (upper - lower) != 0 else 0.5
        
        # Look at recent data for breakouts
        last_5_days = bb_data.tail(5)
        breakout_detected = False
        
        for i in range(1, len(last_5_days)):
            prev_day = last_5_days.iloc[i-1]
            curr_day = last_5_days.iloc[i]
            
            # Upper band breakout
            if prev_day['Close'] <= prev_day['Upper Band'] and curr_day['Close'] > curr_day['Upper Band']:
                return "Bullish: Price breaking out above upper Bollinger Band"
            
            # Lower band breakout
            if prev_day['Close'] >= prev_day['Lower Band'] and curr_day['Close'] < curr_day['Lower Band']:
                return "Bearish: Price breaking down below lower Bollinger Band"
        
        # Interpret current position
        if close > upper:
            return "Overbought: Price above upper Bollinger Band"
        elif close < lower:
            return "Oversold: Price below lower Bollinger Band"
        elif close > middle and percent_b > 0.8:
            return "Bullish: Price in upper Bollinger Band range"
        elif close < middle and percent_b < 0.2:
            return "Bearish: Price in lower Bollinger Band range"
        else:
            return "Neutral: Price within normal Bollinger Band range"
    
    def get_technical_signals(self):
        """
        Get a comprehensive set of technical signals
        
        Returns:
        --------
        dict
            Dictionary of technical indicators and their signals
        """
        signals = {}
        
        # Moving Averages
        ma_signals = self.interpret_moving_averages()
        for key, value in ma_signals.items():
            signals[key] = value
        
        # RSI
        rsi_data = self.get_rsi()
        if not rsi_data.empty:
            rsi_value = rsi_data['RSI'].iloc[-1]
            if rsi_value > 70:
                signals['RSI'] = f"Bearish: Overbought (RSI = {rsi_value:.2f})"
            elif rsi_value < 30:
                signals['RSI'] = f"Bullish: Oversold (RSI = {rsi_value:.2f})"
            elif rsi_value > 50:
                signals['RSI'] = f"Neutral-Bullish (RSI = {rsi_value:.2f})"
            else:
                signals['RSI'] = f"Neutral-Bearish (RSI = {rsi_value:.2f})"
        
        # MACD
        signals['MACD'] = self.interpret_macd()
        
        # Bollinger Bands
        signals['Bollinger Bands'] = self.interpret_bollinger_bands()
        
        return signals
