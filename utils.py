import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

def safe_float_convert(value, default=None):
    """
    Safely convert a value to float, handling 'N/A' strings and other non-numeric values
    
    Parameters:
    -----------
    value : any
        The value to convert to float
    default : float or None
        Default value to return if conversion fails
        
    Returns:
    --------
    float or default value
        Converted float or default value if conversion fails
    """
    if value is None:
        return default
        
    if isinstance(value, str) and (value == 'N/A' or value.strip() == ''):
        return default
        
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


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
    
    # Convert to float safely
    try:
        number = safe_float_convert(number)
        if number is None:
            return "N/A"
    except Exception:
        return "N/A"
    
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

def get_stock_news(ticker, num_articles=10):
    """
    Get recent news articles about a stock
    
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
        
        # Format the news data
        news_articles = []
        
        for article in yahoo_news[:num_articles]:
            # Format the timestamp
            timestamp = article.get('providerPublishTime', None)
            if timestamp:
                published_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S%z')
            else:
                published_date = None
            
            # Create article dict
            news_article = {
                'title': article.get('title', ''),
                'published': published_date,
                'link': article.get('link', ''),
                'publisher': article.get('publisher', ''),
                'summary': article.get('summary', '')
            }
            
            news_articles.append(news_article)
        
        return news_articles
    
    except Exception as e:
        print(f"Error fetching news for {ticker}: {str(e)}")
        return []
