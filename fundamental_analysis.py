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
        try:
            # Get income statement data
            income_stmt = self.stock.income_stmt
            
            if income_stmt is None or isinstance(income_stmt, dict):
                return pd.DataFrame()
                
            if income_stmt.empty:
                return pd.DataFrame()
            
            # Transpose so dates are columns
            income_stmt = income_stmt.T
            
            # Format the index for better readability if it's a datetime index
            try:
                if isinstance(income_stmt.index, pd.DatetimeIndex):
                    income_stmt.index = [idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx) for idx in income_stmt.index]
            except Exception as e:
                print(f"Error formatting income statement index: {str(e)}")
            
            return income_stmt
        except Exception as e:
            print(f"Error in get_income_statement: {str(e)}")
            return pd.DataFrame()
    
    def get_balance_sheet(self):
        """
        Get the company's balance sheet
        
        Returns:
        --------
        pandas.DataFrame
            Balance sheet data
        """
        try:
            # Get balance sheet data
            balance_sheet = self.stock.balance_sheet
            
            if balance_sheet is None or isinstance(balance_sheet, dict):
                return pd.DataFrame()
                
            if balance_sheet.empty:
                return pd.DataFrame()
            
            # Transpose so dates are columns
            balance_sheet = balance_sheet.T
            
            # Format the index for better readability if it's a datetime index
            try:
                if isinstance(balance_sheet.index, pd.DatetimeIndex):
                    balance_sheet.index = [idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx) for idx in balance_sheet.index]
            except Exception as e:
                print(f"Error formatting balance sheet index: {str(e)}")
            
            return balance_sheet
        except Exception as e:
            print(f"Error in get_balance_sheet: {str(e)}")
            return pd.DataFrame()
    
    def get_cash_flow(self):
        """
        Get the company's cash flow statement
        
        Returns:
        --------
        pandas.DataFrame
            Cash flow statement data
        """
        try:
            # Get cash flow data
            cash_flow = self.stock.cashflow
            
            if cash_flow is None or isinstance(cash_flow, dict):
                return pd.DataFrame()
                
            if cash_flow.empty:
                return pd.DataFrame()
            
            # Transpose so dates are columns
            cash_flow = cash_flow.T
            
            # Format the index for better readability if it's a datetime index
            try:
                if isinstance(cash_flow.index, pd.DatetimeIndex):
                    cash_flow.index = [idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx) for idx in cash_flow.index]
            except Exception as e:
                print(f"Error formatting cash flow index: {str(e)}")
            
            return cash_flow
        except Exception as e:
            print(f"Error in get_cash_flow: {str(e)}")
            return pd.DataFrame()
    
    def get_earnings_growth(self):
        """
        Get earnings and revenue growth data
        
        Returns:
        --------
        pandas.DataFrame
            Earnings and revenue data
        """
        try:
            # Get quarterly earnings data
            earnings = self.stock.quarterly_earnings
            
            if earnings is None or earnings.empty:
                return pd.DataFrame()
            
            # Ensure the index is not RangeIndex
            if isinstance(earnings.index, pd.RangeIndex):
                # Create a default index if it's a RangeIndex
                # This helps avoid the 'RangeIndex' object has no attribute 'strftime' error
                quarters = [f'Q{i+1}' for i in range(len(earnings))]
                earnings.index = quarters
            
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
        except Exception as e:
            print(f"Error in get_earnings_growth: {str(e)}")
            return pd.DataFrame()
    
    def get_analyst_recommendations(self):
        """
        Get analyst recommendations for the stock
        
        Returns:
        --------
        pandas.DataFrame
            Analyst recommendations
        """
        try:
            # Get recommendations
            recommendations = self.stock.recommendations
            
            # Handle cases where recommendations might be None or not a DataFrame
            if recommendations is None or not isinstance(recommendations, pd.DataFrame):
                return pd.DataFrame()
                
            # Handle empty DataFrame
            if len(recommendations) == 0:
                return pd.DataFrame()
            
            # Ensure the index is not RangeIndex
            if isinstance(recommendations.index, pd.RangeIndex):
                # Create a default index if it's a RangeIndex
                dates = [f'Analysis {i+1}' for i in range(len(recommendations))]
                recommendations.index = dates
                return recommendations
            
            # If we have a DatetimeIndex, format it properly
            if isinstance(recommendations.index, pd.DatetimeIndex):
                # Convert index to string dates for better readability
                new_index = []
                for date in recommendations.index:
                    try:
                        if hasattr(date, 'strftime'):
                            new_index.append(date.strftime('%Y-%m-%d'))
                        else:
                            new_index.append(str(date))
                    except:
                        new_index.append(str(date))
                recommendations.index = new_index
            
            return recommendations
        except Exception as e:
            print(f"Error in get_analyst_recommendations: {str(e)}")
            return pd.DataFrame()
