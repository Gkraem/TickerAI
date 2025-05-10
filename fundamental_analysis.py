import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FundamentalAnalysis:
    """
    Class for performing fundamental analysis on stock data
    """
    
    def __init__(self, ticker):
        """
        Initialize FundamentalAnalysis with a ticker symbol
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol (e.g., 'AAPL' for Apple)
        """
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.info = self.stock.info
    
    def get_valuation_ratios(self):
        """
        Get key valuation ratios for the stock
        
        Returns:
        --------
        pandas.DataFrame
            Dataframe with valuation ratios
        """
        # Define ratios to retrieve
        valuation_ratios = {
            'P/E Ratio (TTM)': self.info.get('trailingPE', None),
            'Forward P/E': self.info.get('forwardPE', None),
            'PEG Ratio': self.info.get('pegRatio', None),
            'Price/Sales (TTM)': self.info.get('priceToSalesTrailing12Months', None),
            'Price/Book': self.info.get('priceToBook', None),
            'Enterprise Value/EBITDA': self.info.get('enterpriseToEbitda', None),
            'Enterprise Value/Revenue': self.info.get('enterpriseToRevenue', None)
        }
        
        # Create dataframe
        df = pd.DataFrame({
            'Ratio': list(valuation_ratios.keys()),
            'Value': list(valuation_ratios.values())
        })
        
        return df
    
    def get_profitability_ratios(self):
        """
        Get profitability ratios for the stock
        
        Returns:
        --------
        pandas.DataFrame
            Dataframe with profitability ratios
        """
        # Define ratios to retrieve
        profitability_ratios = {
            'Profit Margin': self.info.get('profitMargins', None),
            'Operating Margin': self.info.get('operatingMargins', None),
            'Return on Assets': self.info.get('returnOnAssets', None),
            'Return on Equity': self.info.get('returnOnEquity', None),
            'Revenue Growth (YoY)': self.info.get('revenueGrowth', None),
            'Earnings Growth (YoY)': self.info.get('earningsGrowth', None),
            'Gross Margin': self.info.get('grossMargins', None)
        }
        
        # Convert ratios to percentages for better readability
        for key, value in profitability_ratios.items():
            if value is not None:
                profitability_ratios[key] = value * 100
        
        # Create dataframe
        df = pd.DataFrame({
            'Ratio': list(profitability_ratios.keys()),
            'Value (%)': list(profitability_ratios.values())
        })
        
        return df
    
    def get_income_statement(self):
        """
        Get the company's income statement
        
        Returns:
        --------
        pandas.DataFrame
            Income statement data
        """
        # Get income statement data
        income_stmt = self.stock.income_stmt
        
        if income_stmt.empty:
            return pd.DataFrame()
        
        # Transpose so dates are columns
        income_stmt = income_stmt.T
        
        # Format the index for better readability
        income_stmt.index = income_stmt.index.strftime('%Y-%m-%d')
        
        return income_stmt
    
    def get_balance_sheet(self):
        """
        Get the company's balance sheet
        
        Returns:
        --------
        pandas.DataFrame
            Balance sheet data
        """
        # Get balance sheet data
        balance_sheet = self.stock.balance_sheet
        
        if balance_sheet.empty:
            return pd.DataFrame()
        
        # Transpose so dates are columns
        balance_sheet = balance_sheet.T
        
        # Format the index for better readability
        balance_sheet.index = balance_sheet.index.strftime('%Y-%m-%d')
        
        return balance_sheet
    
    def get_cash_flow(self):
        """
        Get the company's cash flow statement
        
        Returns:
        --------
        pandas.DataFrame
            Cash flow statement data
        """
        # Get cash flow data
        cash_flow = self.stock.cashflow
        
        if cash_flow.empty:
            return pd.DataFrame()
        
        # Transpose so dates are columns
        cash_flow = cash_flow.T
        
        # Format the index for better readability
        cash_flow.index = cash_flow.index.strftime('%Y-%m-%d')
        
        return cash_flow
    
    def get_earnings_growth(self):
        """
        Get earnings and revenue growth data
        
        Returns:
        --------
        pandas.DataFrame
            Earnings and revenue data
        """
        # Get quarterly earnings data
        earnings = self.stock.quarterly_earnings
        
        if earnings is None or earnings.empty:
            return pd.DataFrame()
        
        # Get quarterly revenue data
        financials = self.stock.quarterly_financials
        
        if financials is None or financials.empty:
            return earnings
        
        # Extract revenue row if available
        if 'Total Revenue' in financials.index:
            revenue = financials.loc['Total Revenue']
            
            # Merge with earnings data
            result = pd.DataFrame({
                'Earnings': earnings['Earnings'],
                'Revenue': revenue
            })
            
            return result
        
        return earnings
    
    def get_analyst_recommendations(self):
        """
        Get analyst recommendations for the stock
        
        Returns:
        --------
        pandas.DataFrame
            Analyst recommendations
        """
        # Get recommendations
        recommendations = self.stock.recommendations
        
        if recommendations is None or recommendations.empty:
            return pd.DataFrame()
        
        # Convert index to string dates for better readability
        recommendations.index = recommendations.index.strftime('%Y-%m-%d')
        
        return recommendations
