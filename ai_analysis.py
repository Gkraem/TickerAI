"""
AI-powered stock analysis using OpenAI
Generates personalized buy/hold/sell recommendations with authentic financial data
"""

import json
import os
from openai import OpenAI
import yfinance as yf

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)


def get_sector_peers(ticker, sector, limit=5):
    """Get sector peers for comparison"""
    try:
        # Common sector tickers - this is a simplified approach
        sector_maps = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'CRM'],
            'Financial Services': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'AXP', 'BLK', 'SPGI', 'ICE'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'ABT', 'CVS', 'MDT', 'DHR', 'BMY'],
            'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX', 'BKNG'],
            'Consumer Defensive': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'CL', 'KMB', 'GIS', 'K', 'CPB'],
            'Industrials': ['BA', 'CAT', 'GE', 'UPS', 'HON', 'LMT', 'MMM', 'FDX', 'RTX', 'DE'],
            'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'CHTR', 'TMUS', 'TWTR'],
            'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PXD', 'KMI', 'OXY', 'PSX', 'VLO'],
            'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'PEG', 'ES'],
            'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'SPG', 'O', 'WELL', 'PSA', 'EXR', 'AVB'],
            'Materials': ['LIN', 'APD', 'SHW', 'ECL', 'FCX', 'NEM', 'DOW', 'DD', 'PPG', 'NUE'],
            'Consumer Staples': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'CL', 'KMB', 'GIS', 'K', 'CPB']
        }
        
        peers = sector_maps.get(sector, [])
        # Remove the current ticker from peers and limit results
        peers = [t for t in peers if t != ticker][:limit]
        return peers
    except:
        return []


def generate_ai_buy_analysis(ticker, analyzer, rating_components):
    """
    Generate AI-powered buy analysis using authentic financial data
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    analyzer : StockAnalyzer
        Analyzer instance with stock data
    rating_components : dict
        Dictionary with technical, fundamental, sentiment scores
    
    Returns:
    --------
    str
        AI-generated analysis text
    """
    # Extract rating components at function start to ensure availability in fallback
    buy_rating = rating_components.get('overall_rating', 5.0)
    technical_score = rating_components.get('technical_score', 5.0)
    fundamental_score = rating_components.get('fundamental_score', 5.0)
    sentiment_score = rating_components.get('sentiment_score', 5.0)
    
    try:
        # Get comprehensive stock data
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get financial metrics
        current_price = analyzer.get_current_price()
        market_cap = analyzer.get_market_cap()
        pe_ratio = analyzer.get_pe_ratio()
        
        # Get sector information
        sector = info.get('sector', 'Unknown')
        industry = info.get('industry', 'Unknown')
        company_name = info.get('longName', ticker)
        
        # Get sector peers for comparison
        peers = get_sector_peers(ticker, sector, 3)
        
        # Collect financial metrics for comparison
        financial_metrics = {
            'current_price': current_price,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None,
            'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else None,
            'debt_to_equity': info.get('debtToEquity', 0),
            'return_on_equity': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None,
            'beta': info.get('beta', 0),
            'target_price': info.get('targetMeanPrice', 0),
            '52_week_high': info.get('fiftyTwoWeekHigh', 0),
            '52_week_low': info.get('fiftyTwoWeekLow', 0)
        }
        
        # Calculate upside/downside
        upside = 0
        if financial_metrics['target_price'] and financial_metrics['target_price'] > 0:
            upside = ((financial_metrics['target_price'] / current_price) - 1) * 100
        
        # Determine overall recommendation based on buy rating
        buy_rating = rating_components.get('overall_rating', 5)
        if buy_rating >= 7:
            recommendation = "BUY"
        elif buy_rating >= 5:
            recommendation = "HOLD"
        else:
            recommendation = "SELL"
        
        # Create detailed prompt for AI analysis
        prompt = f"""
Analyze {company_name} ({ticker}) stock and provide a concise 3-4 sentence investment analysis. Use the following authentic financial data:

COMPANY: {company_name} ({ticker})
SECTOR: {sector} | INDUSTRY: {industry}
CURRENT PRICE: ${current_price:.2f}
MARKET CAP: ${market_cap/1e9:.1f}B
P/E RATIO: {pe_ratio:.1f}
PROFIT MARGIN: {financial_metrics['profit_margin']:.1f}% 
REVENUE GROWTH: {financial_metrics['revenue_growth']:.1f}%
DEBT-TO-EQUITY: {financial_metrics['debt_to_equity']:.1f}
ROE: {financial_metrics['return_on_equity']:.1f}%
DIVIDEND YIELD: {financial_metrics['dividend_yield']:.1f}%
BETA: {financial_metrics['beta']:.2f}
ANALYST TARGET: ${financial_metrics['target_price']:.2f} ({upside:+.1f}% upside)

RATING SCORES:
- Technical Score: {rating_components.get('technical_score', 0):.1f}/10
- Fundamental Score: {rating_components.get('fundamental_score', 0):.1f}/10  
- Sentiment Score: {rating_components.get('sentiment_score', 0):.1f}/10
- Overall Rating: {buy_rating:.1f}/10

SECTOR PEERS: {', '.join(peers) if peers else 'Limited peer data'}

Provide a {recommendation} analysis that:
1. References specific financial metrics above
2. Compares to sector performance expectations
3. Explains the key factors driving the {recommendation} recommendation
4. Mentions the most compelling strength and biggest risk

Keep it conversational, data-driven, and actionable. Do not use generic language.
"""

        # Generate AI analysis using GPT-4o
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional financial analyst providing precise, data-driven stock analysis. Use specific numbers and avoid generic statements."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=300,
            temperature=0.3  # Lower temperature for more consistent, factual analysis
        )
        
        content = response.choices[0].message.content
        analysis = content.strip() if content else "Analysis not available"
        return analysis
        
    except Exception as e:
        print(f"Error generating AI analysis for {ticker}: {str(e)}")
        # Enhanced fallback analysis with actual financial data
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            company_name = info.get('longName', ticker)
            sector = info.get('sector', 'Unknown')
            
            current_price = analyzer.get_current_price() if analyzer else 0
            pe_ratio = analyzer.get_pe_ratio() if analyzer else 0
            market_cap = analyzer.get_market_cap() if analyzer else 0
            
            profit_margin = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
            revenue_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
            target_price = info.get('targetMeanPrice', 0) or 0
            
            # Calculate upside if target price exists
            upside_text = ""
            if target_price and target_price > 0 and current_price > 0:
                upside = ((target_price / current_price) - 1) * 100
                upside_text = f" with analyst targets suggesting {upside:+.1f}% potential"
            
            # Determine recommendation
            if buy_rating >= 7:
                recommendation = "BUY"
                reason = f"strong fundamentals including {profit_margin:.1f}% profit margins"
            elif buy_rating >= 5:
                recommendation = "HOLD"
                reason = f"stable performance in the {sector} sector"
            else:
                recommendation = "SELL"
                reason = f"concerning financial metrics and market position"
            
            return f"{company_name} shows a {recommendation} rating based on {reason}. Trading at ${current_price:.2f} with a P/E of {pe_ratio:.1f if pe_ratio else 0}, the stock demonstrates {'solid' if buy_rating >= 6 else 'mixed' if buy_rating >= 4 else 'weak'} investment characteristics{upside_text}."
            
        except:
            return f"Based on the overall rating of {buy_rating:.1f}/10, this stock shows {'strong potential' if buy_rating >= 7 else 'moderate performance' if buy_rating >= 5 else 'weak fundamentals'}."


def get_recommendation_color(buy_rating):
    """Get color for recommendation based on buy rating"""
    if buy_rating >= 7:
        return "🟢"  # Green for BUY
    elif buy_rating >= 5:
        return "🟡"  # Yellow for HOLD
    else:
        return "🔴"  # Red for SELL


def get_recommendation_text(buy_rating):
    """Get recommendation text based on buy rating"""
    if buy_rating >= 7:
        return "BUY"
    elif buy_rating >= 5:
        return "HOLD"
    else:
        return "SELL"