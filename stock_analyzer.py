import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from technical_analysis import TechnicalAnalysis
from fundamental_analysis import FundamentalAnalysis

class StockAnalyzer:
    """
    Main class for analyzing stock data and generating buy ratings
    """
    
    def __init__(self, ticker):
        """
        Initialize StockAnalyzer with a ticker symbol
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol (e.g., 'AAPL' for Apple)
        """
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        
        try:
            self.info = self.stock.info if hasattr(self.stock, 'info') else {}
        except (AttributeError, TypeError):
            self.info = {}
            
        # Get the stock data for the last day
        try:
            self.current_data = self.stock.history(period='2d')
        except Exception:
            self.current_data = pd.DataFrame()
            
        # Initialize analysis components
        self.technical = TechnicalAnalysis(ticker)
        self.fundamental = FundamentalAnalysis(ticker)
    
    def get_current_price(self):
        """Get the current stock price"""
        if not self.current_data.empty:
            return self.current_data['Close'].iloc[-1]
        return None
    
    def get_price_change(self):
        """Get the daily price change and percentage"""
        if len(self.current_data) >= 2:
            prev_close = self.current_data['Close'].iloc[-2]
            current_close = self.current_data['Close'].iloc[-1]
            price_change = current_close - prev_close
            price_change_percent = (price_change / prev_close) * 100
            return price_change, price_change_percent
        return 0, 0
    
    def get_market_cap(self):
        """Get the market capitalization"""
        return self.info.get('marketCap', None)
    
    def get_pe_ratio(self):
        """Get the price-to-earnings ratio"""
        return self.info.get('trailingPE', None)
    
    def get_52_week_range(self):
        """Get the 52-week price range"""
        return self.info.get('fiftyTwoWeekLow', 0), self.info.get('fiftyTwoWeekHigh', 0)
    
    def get_company_info(self):
        """Get general company information"""
        return self.info
    
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
        return self.stock.history(period=timeframe)
    
    def calculate_buy_rating(self):
        """
        Calculate an overall buy rating on a scale of 1-10
        
        Returns:
        --------
        float
            Buy rating score (1-10)
        dict
            Breakdown of the rating components
        """
        score_breakdown = {}
        
        # Technical Analysis Score (40% weight)
        technical_score = self._calculate_technical_score()
        score_breakdown['Technical Analysis'] = technical_score
        
        # Fundamental Analysis Score (40% weight)
        fundamental_score = self._calculate_fundamental_score()
        score_breakdown['Fundamental Analysis'] = fundamental_score
        
        # Market Sentiment Score (20% weight)
        sentiment_score = self._calculate_sentiment_score()
        score_breakdown['Market Sentiment'] = sentiment_score
        
        # Calculate final weighted score
        final_score = (
            technical_score['score'] * 0.4 +
            fundamental_score['score'] * 0.4 +
            sentiment_score['score'] * 0.2
        )
        
        # Round to one decimal place
        final_score = round(final_score, 1)
        
        return final_score, score_breakdown
    
    def _calculate_technical_score(self):
        """Calculate technical analysis score component"""
        # Get technical signals
        signals = self.technical.get_technical_signals()
        
        # Count bullish vs bearish signals
        bullish_count = sum(1 for signal in signals.values() if "bullish" in signal.lower())
        bearish_count = sum(1 for signal in signals.values() if "bearish" in signal.lower())
        total_signals = len(signals)
        
        if total_signals == 0:
            score = 5.0  # Neutral if no signals
            reason = "Insufficient technical data available"
        else:
            # Calculate score based on ratio of bullish to total signals
            score = (bullish_count / total_signals) * 10
            
            # Determine the reason
            if score >= 7:
                reason = "Strong bullish technical indicators"
            elif score >= 5:
                reason = "Moderately bullish technical indicators"
            elif score > 3:
                reason = "Mixed technical signals with slight bearish bias"
            else:
                reason = "Strong bearish technical indicators"
        
        return {'score': score, 'reason': reason}
    
    def _calculate_fundamental_score(self):
        """Calculate fundamental analysis score component"""
        # Get key fundamental ratios
        pe_ratio = self.get_pe_ratio()
        company_info = self.get_company_info()
        
        # Initialize parameters for scoring
        score_factors = []
        reasons = []
        
        # 1. P/E Ratio Assessment
        if pe_ratio is not None:
            # Compare to industry average (simplified)
            industry_avg_pe = company_info.get('forwardPE', 20)  # Default to 20 if not available
            
            if pe_ratio < industry_avg_pe * 0.7:  # Significantly undervalued
                score_factors.append(9)
                reasons.append("P/E ratio significantly below industry average (potentially undervalued)")
            elif pe_ratio < industry_avg_pe:  # Moderately undervalued
                score_factors.append(7)
                reasons.append("P/E ratio below industry average")
            elif pe_ratio < industry_avg_pe * 1.3:  # Fair value
                score_factors.append(5)
                reasons.append("P/E ratio near industry average")
            else:  # Overvalued
                score_factors.append(3)
                reasons.append("P/E ratio above industry average (potentially overvalued)")
        
        # 2. Profit Margins
        profit_margin = company_info.get('profitMargins', None)
        if profit_margin is not None:
            if profit_margin > 0.2:  # Very high margins
                score_factors.append(9)
                reasons.append("Excellent profit margins")
            elif profit_margin > 0.1:  # Good margins
                score_factors.append(7)
                reasons.append("Good profit margins")
            elif profit_margin > 0.05:  # Average margins
                score_factors.append(5)
                reasons.append("Average profit margins")
            elif profit_margin > 0:  # Low but positive margins
                score_factors.append(3)
                reasons.append("Below-average profit margins")
            else:  # Negative margins
                score_factors.append(1)
                reasons.append("Negative profit margins")
        
        # 3. Revenue Growth
        revenue_growth = company_info.get('revenueGrowth', None)
        if revenue_growth is not None:
            if revenue_growth > 0.25:  # Excellent growth
                score_factors.append(10)
                reasons.append("Exceptional revenue growth")
            elif revenue_growth > 0.15:  # Very good growth
                score_factors.append(8)
                reasons.append("Strong revenue growth")
            elif revenue_growth > 0.05:  # Good growth
                score_factors.append(6)
                reasons.append("Positive revenue growth")
            elif revenue_growth > 0:  # Minimal growth
                score_factors.append(4)
                reasons.append("Minimal revenue growth")
            else:  # Negative growth
                score_factors.append(2)
                reasons.append("Declining revenues")
        
        # 4. Debt-to-Equity
        debt_to_equity = company_info.get('debtToEquity', None)
        if debt_to_equity is not None:
            if debt_to_equity < 50:  # Very low debt
                score_factors.append(9)
                reasons.append("Very low debt-to-equity ratio")
            elif debt_to_equity < 100:  # Low debt
                score_factors.append(7)
                reasons.append("Low debt-to-equity ratio")
            elif debt_to_equity < 150:  # Moderate debt
                score_factors.append(5)
                reasons.append("Moderate debt-to-equity ratio")
            elif debt_to_equity < 200:  # High debt
                score_factors.append(3)
                reasons.append("High debt-to-equity ratio")
            else:  # Very high debt
                score_factors.append(1)
                reasons.append("Very high debt-to-equity ratio")
        
        # Calculate final fundamental score
        if score_factors:
            score = sum(score_factors) / len(score_factors)
            
            # Cap at 10
            score = min(score, 10)
            
            # Select top 2 reasons for summary
            top_reasons = reasons[:2] if len(reasons) > 1 else reasons
            reason = "; ".join(top_reasons)
        else:
            score = 5.0  # Neutral if no data
            reason = "Insufficient fundamental data available"
        
        return {'score': score, 'reason': reason}
    
    def _calculate_sentiment_score(self):
        """Calculate market sentiment score component"""
        company_info = self.get_company_info()
        
        # Analyst recommendations
        rec = company_info.get('recommendationMean', None)
        
        if rec is not None:
            # Convert 1-5 scale (where 1 is Strong Buy and 5 is Strong Sell) to 10-1 scale
            sentiment_score = ((5 - rec) / 4) * 9 + 1
            
            # Determine reason based on recommendation level
            if rec <= 1.5:
                reason = "Strong analyst buy recommendations"
            elif rec <= 2.5:
                reason = "Moderate analyst buy recommendations"
            elif rec <= 3.5:
                reason = "Hold recommendations from analysts"
            elif rec <= 4.5:
                reason = "Moderate analyst sell recommendations"
            else:
                reason = "Strong analyst sell recommendations"
        else:
            # Default to neutral if no analyst recommendations
            sentiment_score = 5.0
            reason = "No analyst recommendations available"
        
        return {'score': sentiment_score, 'reason': reason}
