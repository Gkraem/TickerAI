import yfinance as yf
import pandas as pd
import numpy as np
import requests
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
        if self.info:
            return {
                'name': self.info.get('shortName', 'N/A'),
                'sector': self.info.get('sector', 'N/A'),
                'industry': self.info.get('industry', 'N/A'),
                'country': self.info.get('country', 'N/A'),
                'website': self.info.get('website', 'N/A'),
                'employees': self.info.get('fullTimeEmployees', 'N/A'),
                'description': self.info.get('longBusinessSummary', 'No description available.')
            }
        return {}
        
    def get_sector_performance(self):
        """
        Get sector performance comparison data
        
        Returns:
        --------
        dict
            Dictionary with sector performance metrics and comparison
        """
        if not self.info or 'sector' not in self.info:
            return None
            
        sector = self.info.get('sector')
        
        try:
            # Get sector ETFs data
            sector_etfs = {
                'Technology': 'XLK',
                'Financial Services': 'XLF',
                'Healthcare': 'XLV',
                'Consumer Cyclical': 'XLY',
                'Industrials': 'XLI',
                'Communication Services': 'XLC',
                'Consumer Defensive': 'XLP',
                'Energy': 'XLE',
                'Basic Materials': 'XLB',
                'Utilities': 'XLU',
                'Real Estate': 'XLRE'
            }
            
            # Default to SPY (S&P 500) if sector not found
            sector_etf = sector_etfs.get(sector, 'SPY')
            etf_data = yf.Ticker(sector_etf)
            
            # Get 1-year performance for the sector ETF
            etf_hist = etf_data.history(period='1y')
            if not etf_hist.empty:
                sector_perf_1y = ((etf_hist['Close'].iloc[-1] / etf_hist['Close'].iloc[0]) - 1) * 100
            else:
                sector_perf_1y = 0
            
            # Get 1-year performance for the stock
            stock_hist = self.stock.history(period='1y')
            if not stock_hist.empty:
                stock_perf_1y = ((stock_hist['Close'].iloc[-1] / stock_hist['Close'].iloc[0]) - 1) * 100
            else:
                stock_perf_1y = 0
            
            # Get S&P 500 performance as market benchmark
            spy_data = yf.Ticker('SPY')
            spy_hist = spy_data.history(period='1y')
            if not spy_hist.empty:
                market_perf_1y = ((spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0]) - 1) * 100
            else:
                market_perf_1y = 0
            
            # Calculate outperformance/underperformance
            sector_outperformance = stock_perf_1y - sector_perf_1y
            market_outperformance = stock_perf_1y - market_perf_1y
            
            # Get sector peers
            peers = []
            try:
                if hasattr(self.stock, 'recommendations'):
                    recs = self.stock.recommendations
                    if hasattr(recs, 'index') and not recs.empty:
                        peers = list(set(recs.index))[:5]
            except:
                peers = []
                
            # If no peers found, try to get them from similar tickers
            if not peers:
                similar_tickers = [
                    "AAPL", "MSFT", "GOOGL", "AMZN", "META",  # Tech
                    "JPM", "BAC", "WFC", "GS", "MS",  # Banks
                    "JNJ", "PFE", "MRK", "UNH", "CVS",  # Healthcare
                    "XOM", "CVX", "COP", "BP", "SLB",  # Energy
                    "TSLA", "F", "GM", "TM", "HMC"  # Auto
                ]
                
                # Filter similar tickers based on sector
                if self.info.get('sector'):
                    sector_map = {
                        'Technology': ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
                        'Financial Services': ["JPM", "BAC", "WFC", "GS", "MS"],
                        'Healthcare': ["JNJ", "PFE", "MRK", "UNH", "CVS"],
                        'Energy': ["XOM", "CVX", "COP", "BP", "SLB"],
                        'Consumer Cyclical': ["TSLA", "F", "GM", "TM", "HMC"]
                    }
                    
                    if self.info.get('sector') in sector_map:
                        peers = sector_map[self.info.get('sector')]
                    
            # Calculate performance for peers
            peer_perfs = []
            for peer in peers[:5]:
                if peer != self.ticker:  # Skip the current stock
                    try:
                        peer_data = yf.Ticker(peer)
                        peer_hist = peer_data.history(period='1y')
                        if not peer_hist.empty:
                            peer_perf = ((peer_hist['Close'].iloc[-1] / peer_hist['Close'].iloc[0]) - 1) * 100
                            peer_perfs.append((peer, peer_perf))
                    except:
                        continue
            
            # Calculate sector rank
            if peer_perfs:
                # Add current stock to the list
                all_perfs = peer_perfs + [(self.ticker, stock_perf_1y)]
                
                # Sort by performance (descending)
                all_perfs.sort(key=lambda x: x[1], reverse=True)
                
                # Get rank (1-based index)
                sector_rank = all_perfs.index((self.ticker, stock_perf_1y)) + 1
                total_peers = len(all_perfs)
            else:
                sector_rank = None
                total_peers = None
            
            return {
                'sector': sector,
                'sector_etf': sector_etf,
                'stock_performance_1y': stock_perf_1y,
                'sector_performance_1y': sector_perf_1y,
                'market_performance_1y': market_perf_1y,
                'sector_outperformance': sector_outperformance,
                'market_outperformance': market_outperformance,
                'sector_rank': sector_rank,
                'total_peers': total_peers,
                'peer_performances': peer_perfs
            }
        except Exception as e:
            print(f"Error fetching sector data: {e}")
            return None
            
    def get_dividend_info(self):
        """
        Get detailed dividend information
        
        Returns:
        --------
        dict
            Dictionary with dividend metrics
        """
        try:
            # Get dividend data
            dividend_yield = self.info.get('dividendYield', 0)
            if dividend_yield:
                dividend_yield = dividend_yield * 100  # Convert to percentage
            
            dividend_rate = self.info.get('dividendRate', 0)
            payout_ratio = self.info.get('payoutRatio', 0)
            if payout_ratio:
                payout_ratio = payout_ratio * 100  # Convert to percentage
            
            # Get dividend history
            dividends = self.stock.dividends
            
            if not dividends.empty:
                # Calculate dividend growth rates
                recent_dividends = dividends.tail(8).values  # Last 2 years assuming quarterly dividends
                
                if len(recent_dividends) >= 4:
                    # Calculate YoY growth
                    latest_year = recent_dividends[-4:].sum()
                    previous_year = recent_dividends[-8:-4].sum()
                    if previous_year > 0:
                        dividend_growth = ((latest_year / previous_year) - 1) * 100
                    else:
                        dividend_growth = 0
                else:
                    dividend_growth = 0
                
                # Get last dividend date
                last_dividend_date = dividends.index[-1].strftime('%Y-%m-%d')
                
                # Calculate average dividend frequency (in months)
                if len(dividends) >= 2:
                    dates = dividends.index[-5:]  # Last 5 dividend dates
                    diffs = []
                    for i in range(1, len(dates)):
                        diff = (dates[i] - dates[i-1]).days / 30  # Convert days to months
                        diffs.append(diff)
                    avg_frequency = sum(diffs) / len(diffs) if diffs else 0
                else:
                    avg_frequency = 0
                
                dividend_history = [(date.strftime('%Y-%m-%d'), amount) 
                                   for date, amount in zip(dividends.index[-4:], dividends.values[-4:])]
            else:
                dividend_growth = 0
                last_dividend_date = None
                avg_frequency = 0
                dividend_history = []
            
            # Calculate annual dividend amount
            annual_dividend = dividend_rate if dividend_rate else 0
            
            # Get dividend status
            ex_dividend_date = self.info.get('exDividendDate')
            if ex_dividend_date:
                ex_dividend_date = datetime.fromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
            
            return {
                'dividend_yield': dividend_yield,
                'dividend_rate': dividend_rate,
                'annual_dividend': annual_dividend,
                'payout_ratio': payout_ratio,
                'dividend_growth': dividend_growth,
                'last_dividend_date': last_dividend_date,
                'ex_dividend_date': ex_dividend_date,
                'avg_frequency': avg_frequency,  # in months
                'dividend_history': dividend_history
            }
        except Exception as e:
            print(f"Error fetching dividend data: {e}")
            return {
                'dividend_yield': 0,
                'dividend_rate': 0,
                'annual_dividend': 0,
                'payout_ratio': 0,
                'dividend_growth': 0,
                'last_dividend_date': None,
                'ex_dividend_date': None,
                'avg_frequency': 0,
                'dividend_history': []
            }
    
    def get_earnings_info(self):
        """
        Get earnings information including report links
        
        Returns:
        --------
        dict
            Dictionary with earnings data and report links
        """
        try:
            # Get earnings data
            earnings = {}
            if hasattr(self.stock, 'earnings'):
                earnings_data = self.stock.earnings
                if not isinstance(earnings_data, type(None)) and not earnings_data.empty:
                    earnings = earnings_data.to_dict()
            
            # Get earnings calendar
            next_earnings_date = None
            try:
                calendar = self.stock.calendar
                if hasattr(calendar, 'Earnings Date') and calendar['Earnings Date'] is not None:
                    next_earnings_date = calendar['Earnings Date'].strftime('%Y-%m-%d')
            except:
                pass
            
            # SEC filing links
            sec_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={self.ticker}&Find=Search&owner=exclude&action=getcompany"
            
            # Get most recent quarterly report link
            latest_10q_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={self.ticker}&type=10-Q"
            
            # Get most recent annual report link
            latest_10k_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={self.ticker}&type=10-K"
            
            # Get revenue data
            total_revenue = None
            net_income = None
            net_margin = None
            
            try:
                if hasattr(self.stock, 'financials'):
                    financials = self.stock.financials
                    if not isinstance(financials, type(None)) and not financials.empty:
                        # Get gross revenue (Total Revenue)
                        if 'Total Revenue' in financials.index:
                            total_revenue = financials.loc['Total Revenue'].iloc[0]
                        
                        # Get net income
                        if 'Net Income' in financials.index:
                            net_income = financials.loc['Net Income'].iloc[0]
                        
                        # Calculate net margin
                        if total_revenue and net_income and total_revenue != 0:
                            net_margin = (net_income / total_revenue) * 100
            except Exception as e:
                print(f"Error getting financial data: {e}")
            
            # Quarterly results (last 4 quarters)
            quarterly_results = []
            try:
                if hasattr(self.stock, 'quarterly_financials'):
                    quarterly_financials = self.stock.quarterly_financials
                    if not isinstance(quarterly_financials, type(None)) and not quarterly_financials.empty:
                        for i in range(min(4, quarterly_financials.shape[1])):
                            quarter_date = quarterly_financials.columns[i].strftime('%Y-%m-%d')
                            quarter_revenue = None
                            quarter_net_income = None
                            
                            if 'Total Revenue' in quarterly_financials.index:
                                quarter_revenue = quarterly_financials.loc['Total Revenue'].iloc[i]
                                
                            if 'Net Income' in quarterly_financials.index:
                                quarter_net_income = quarterly_financials.loc['Net Income'].iloc[i]
                            
                            quarterly_results.append({
                                'date': quarter_date,
                                'revenue': quarter_revenue,
                                'net_income': quarter_net_income
                            })
            except Exception as e:
                print(f"Error getting quarterly results: {e}")
            
            return {
                'earnings_data': earnings,
                'next_earnings_date': next_earnings_date,
                'sec_filings_url': sec_url,
                'latest_10q_url': latest_10q_url,
                'latest_10k_url': latest_10k_url,
                'total_revenue': total_revenue,
                'net_income': net_income,
                'net_margin': net_margin,
                'quarterly_results': quarterly_results
            }
        except Exception as e:
            print(f"Error fetching earnings data: {e}")
            return {
                'earnings_data': {},
                'next_earnings_date': None,
                'sec_filings_url': f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={self.ticker}&Find=Search&owner=exclude&action=getcompany",
                'latest_10q_url': f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={self.ticker}&type=10-Q",
                'latest_10k_url': f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={self.ticker}&type=10-K",
                'total_revenue': None,
                'net_income': None,
                'net_margin': None,
                'quarterly_results': []
            }
    
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
        try:
            # Get key fundamental ratios
            pe_ratio = self.get_pe_ratio()
            company_info = self.get_company_info()
            
            # Initialize parameters for scoring
            score_factors = []
            reasons = []
            
            # 1. P/E Ratio Assessment
            if pe_ratio is not None and isinstance(pe_ratio, (int, float)):
                # Compare to industry average (simplified)
                industry_avg_pe = company_info.get('forwardPE', 20)  # Default to 20 if not available
                
                # Make sure industry_avg_pe is a numeric value
                if not isinstance(industry_avg_pe, (int, float)) or industry_avg_pe == 'N/A':
                    industry_avg_pe = 20  # Default if not a valid number
                
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
            if profit_margin is not None and isinstance(profit_margin, (int, float)):
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
        except Exception as e:
            print(f"Error in fundamental score calculation: {e}")
            # Return default values if an error occurs
            return {'score': 5.0, 'reason': 'Limited fundamental data available'}
        
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
