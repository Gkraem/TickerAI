import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

def format_large_number(number):
    """
    Format large numbers into readable format with K, M, B, T suffixes
    
    Parameters:
    -----------
    number : int or float
        The number to format
    
    Returns:
    --------
    str
        Formatted number as string
    """
    if number is None:
        return "N/A"
    
    # Convert to float for safety
    number = float(number)
    
    # Define suffixes
    suffixes = ["", "K", "M", "B", "T"]
    
    # Determine the appropriate suffix
    magnitude = 0
    while abs(number) >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        number /= 1000.0
    
    # Format the number with the suffix
    # Use different precision based on magnitude
    if magnitude == 0:
        return f"${number:.2f}"
    else:
        return f"${number:.2f}{suffixes[magnitude]}"

def get_earnings_calendar(ticker):
    """
    Get earnings calendar data from Wall Street Horizon
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    
    Returns:
    --------
    dict
        Earnings calendar information
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Get earnings data from Wall Street Horizon
        url = f"https://www.wallstreethorizon.com/{ticker.lower()}-earnings-calendar"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse earnings data
            earnings_info = {
                'next_earnings_date': 'Not available',
                'status': 'Unconfirmed',
                'quarter': 'Unknown',
                'time': 'Unknown'
            }
            
            # Look for earnings date information
            date_elements = soup.find_all(['span', 'div'], text=lambda text: text and ('Q' in text or 'earnings' in text.lower()))
            
            if date_elements:
                for element in date_elements:
                    text = element.get_text().strip()
                    if 'Q' in text and ('2024' in text or '2025' in text):
                        earnings_info['quarter'] = text
                        break
            
            return earnings_info
        else:
            return {
                'next_earnings_date': 'Data unavailable',
                'status': 'Unknown',
                'quarter': 'Unknown',
                'time': 'Unknown'
            }
            
    except Exception as e:
        return {
            'next_earnings_date': 'Error retrieving data',
            'status': 'Unknown',
            'quarter': 'Unknown',
            'time': 'Unknown'
        }

def get_previous_earnings(ticker):
    """
    Get previous earnings results
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    
    Returns:
    --------
    list
        List of previous earnings results
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get quarterly earnings data
        quarterly_earnings = stock.quarterly_earnings
        
        if quarterly_earnings is not None and not quarterly_earnings.empty:
            # Get the last 2 quarters
            recent_earnings = quarterly_earnings.head(2)
            
            earnings_results = []
            for date, row in recent_earnings.iterrows():
                # Format quarter properly
                try:
                    if hasattr(date, 'quarter') and hasattr(date, 'year'):
                        quarter_str = f"{date.year} Q{date.quarter}"
                    else:
                        quarter_str = str(date)[:10]  # Just the date part
                except:
                    quarter_str = str(date)
                
                actual = row.get('Actual', 'N/A')
                estimate = row.get('Estimate', 'N/A')
                
                # Determine if beat or missed estimate
                beat_estimate = 'Unknown'
                if actual != 'N/A' and estimate != 'N/A':
                    try:
                        actual_val = float(actual)
                        estimate_val = float(estimate)
                        beat_estimate = 'Beat' if actual_val > estimate_val else 'Missed'
                    except:
                        beat_estimate = 'Unknown'
                
                quarter_info = {
                    'quarter': quarter_str,
                    'actual': actual,
                    'estimate': estimate,
                    'beat_estimate': beat_estimate
                }
                
                earnings_results.append(quarter_info)
            
            return earnings_results[:2]
        else:
            return []
            
    except Exception as e:
        return []

def get_stock_news(ticker, num_articles=5):
    """
    Get recent relevant news articles about a stock
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    num_articles : int
        Number of articles to return
    
    Returns:
    --------
    list
        List of dictionaries containing news information
    """
    try:
        # Get news from Yahoo Finance
        stock = yf.Ticker(ticker)
        yahoo_news = stock.news
        
        # Get company info for filtering
        info = stock.info
        company_name = info.get('longName', ticker).lower()
        
        # Format the news data with relevance filtering
        news_articles = []
        
        for article in yahoo_news:
            # Filter for relevance
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            
            # Check if article is relevant to the specific company
            is_relevant = (
                ticker.lower() in title or 
                company_name in title or
                ticker.lower() in summary or
                any(word in title for word in ['earnings', 'revenue', 'profit', 'guidance', 'beat', 'miss', 'upgrade', 'downgrade'])
            )
            
            if is_relevant:
                # Format the timestamp
                timestamp = article.get('providerPublishTime', None)
                if timestamp:
                    published_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    published_date = None
                
                news_article = {
                    'title': article.get('title', 'No title'),
                    'summary': article.get('summary', 'No summary available'),
                    'url': article.get('link', ''),
                    'publisher': article.get('publisher', 'Unknown'),
                    'published_date': published_date,
                    'thumbnail': article.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', '') if article.get('thumbnail') else ''
                }
                
                news_articles.append(news_article)
                
                if len(news_articles) >= num_articles:
                    break
        
        return news_articles[:num_articles]
        
    except Exception as e:
        print(f"Error fetching news for {ticker}: {str(e)}")
        return []
