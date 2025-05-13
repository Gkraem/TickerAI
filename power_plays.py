"""
Power Plays functionality - Find top stock opportunities in Fortune 500
"""
import yfinance as yf
import pandas as pd
import streamlit as st
from stock_analyzer import StockAnalyzer
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Fortune 500 tickers - top companies (using a subset for faster demo)
# In a real app, you would use the complete Fortune 500 list
FORTUNE_500_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "NVDA", "UNH", "JNJ",
    "JPM", "V", "PG", "MA", "HD", "ABBV", "MRK", "XOM", "BAC", "CVX", 
    "LLY", "PFE", "KO", "PEP", "TMO", "COST", "AVGO", "DIS", "WMT", "CSCO",
    "ABT", "ACN", "MCD", "VZ", "CRM", "NKE", "CMCSA", "ADBE", "ORCL", "DHR",
    "IBM", "PM", "UPS", "AMD", "TXN", "INTC", "QCOM", "COP", "T", "AMGN"
]

def analyze_ticker(ticker):
    """
    Analyze a single ticker and return its buy rating and details
    """
    try:
        # Initialize stock analyzer for the ticker
        analyzer = StockAnalyzer(ticker)
        
        # Get basic info
        info = analyzer.get_company_info()
        company_name = info.get('shortName', ticker)
        
        # Calculate buy rating
        buy_rating, rating_components = analyzer.calculate_buy_rating()
        
        # Get the score breakdown from components
        technical_data = rating_components.get('Technical Analysis', {})
        fundamental_data = rating_components.get('Fundamental Analysis', {})
        sentiment_data = rating_components.get('Market Sentiment', {})
        
        # Extract individual scores
        technical_score = technical_data.get('score', 5.0) if isinstance(technical_data, dict) else 5.0
        fundamental_score = fundamental_data.get('score', 5.0) if isinstance(fundamental_data, dict) else 5.0
        sentiment_score = sentiment_data.get('score', 5.0) if isinstance(sentiment_data, dict) else 5.0
        
        # Generate analysis
        analysis = generate_analysis(ticker, buy_rating, technical_score, fundamental_score, sentiment_score)
        
        return {
            'ticker': ticker,
            'company_name': company_name,
            'buy_rating': buy_rating,
            'rating_components': rating_components,
            'analysis': analysis
        }
    except Exception as e:
        # If there's an error, return None
        print(f"Error analyzing {ticker}: {str(e)}")
        return None

def generate_analysis(ticker, buy_rating, technical_score, fundamental_score, sentiment_score):
    """
    Generate analysis text based on the stock's scores
    """
    # Determine strength and weakness areas
    strengths = []
    weaknesses = []
    
    if technical_score >= 7:
        strengths.append("strong technical indicators (bullish chart patterns, positive momentum)")
    elif technical_score <= 4:
        weaknesses.append("concerning technical signals (bearish patterns, negative momentum)")
        
    if fundamental_score >= 7:
        strengths.append("solid fundamentals (strong earnings growth, healthy balance sheet)")
    elif fundamental_score <= 4:
        weaknesses.append("weak fundamentals (poor financial health, declining margins)")
        
    if sentiment_score >= 7:
        strengths.append("positive market sentiment (analyst upgrades, institutional buying)")
    elif sentiment_score <= 4:
        weaknesses.append("negative market sentiment (analyst downgrades, institutional selling)")
    
    # Create the explanation based on the rating and identified strengths/weaknesses
    if buy_rating >= 7.5:
        strength_text = ", ".join(strengths) if strengths else "multiple positive factors"
        explanation = f"**Strong Buy ({buy_rating:.1f}/10):** {ticker} presents a compelling investment case based on {strength_text}."
    elif buy_rating >= 6:
        strength_text = ", ".join(strengths) if strengths else "several positive indicators"
        explanation = f"**Buy ({buy_rating:.1f}/10):** {ticker} shows favorable characteristics including {strength_text}."
    elif buy_rating >= 4:
        if strengths and weaknesses:
            explanation = f"**Hold ({buy_rating:.1f}/10):** {ticker} shows mixed signals with {', '.join(strengths)} but also {', '.join(weaknesses)}."
        else:
            explanation = f"**Hold ({buy_rating:.1f}/10):** {ticker} currently presents a balanced risk-reward profile."
    elif buy_rating >= 2.5:
        weakness_text = ", ".join(weaknesses) if weaknesses else "various concerning factors"
        explanation = f"**Sell ({buy_rating:.1f}/10):** {ticker} faces challenges including {weakness_text}."
    else:
        weakness_text = ", ".join(weaknesses) if weaknesses else "significant negative indicators"
        explanation = f"**Strong Sell ({buy_rating:.1f}/10):** {ticker} faces major headwinds including {weakness_text}."
    
    return explanation

def get_top_stocks(max_stocks=5, max_tickers=None, progress_callback=None):
    """
    Analyze Fortune 500 stocks and return the top stocks with highest buy ratings
    
    Parameters:
    -----------
    max_stocks : int
        Maximum number of top stocks to return
    max_tickers : int
        Maximum number of tickers to analyze (for testing/demo purposes)
    progress_callback : function
        Callback function to update progress
    
    Returns:
    --------
    list
        List of top stock dictionaries sorted by buy rating
    """
    st.write("Scanning Fortune 500 companies for investment opportunities...")
    
    # Use a subset of tickers for testing if specified
    tickers_to_analyze = FORTUNE_500_TICKERS[:max_tickers] if max_tickers else FORTUNE_500_TICKERS
    
    # Show a progress bar
    progress_container = st.empty()
    progress_bar = progress_container.progress(0)
    
    analyzed_stocks = []
    total_tickers = len(tickers_to_analyze)
    completed = 0
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_ticker = {executor.submit(analyze_ticker, ticker): ticker for ticker in tickers_to_analyze}
        
        # Process results as they complete
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                if result:  # If analysis was successful
                    analyzed_stocks.append(result)
            except Exception as e:
                st.error(f"Error analyzing {ticker}: {str(e)}")
            
            # Update progress
            completed += 1
            progress_percentage = completed / total_tickers
            
            # Update progress bar or use callback
            if progress_callback:
                progress_callback(progress_percentage)
            else:
                progress_bar.progress(progress_percentage)
    
    # Remove the progress bar when done
    progress_container.empty()
    
    # Sort by buy rating and get top N
    top_stocks = sorted(analyzed_stocks, key=lambda x: x['buy_rating'], reverse=True)[:max_stocks]
    
    return top_stocks

def display_power_plays():
    """
    Display the Power Plays page with top stock picks
    """
    # Header and introduction
    st.title("Power Plays 🚀")
    
    st.markdown("""
    <div style="background-color: rgba(17, 24, 39, 0.7); padding: 20px; border-radius: 10px; margin-bottom: 30px;">
    <p style="font-size: 18px; line-height: 1.6;">
    Power Plays delivers the five most compelling stock opportunities in the Fortune 500, ranked by AI-driven buy ratings. 
    Updated in real time, these picks offer a snapshot of where the strongest buying signals are—so you can act fast, with confidence.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have cached results
    if 'power_plays_results' not in st.session_state:
        with st.spinner("Analyzing Fortune 500 stocks to find the best opportunities..."):
            # Get top stocks (limiting to 30 tickers for demo purposes)
            st.session_state.power_plays_results = get_top_stocks(max_stocks=5, max_tickers=30)
    
    # Display results
    top_stocks = st.session_state.power_plays_results
    
    # Option to refresh
    if st.button("Refresh Analysis"):
        with st.spinner("Refreshing analysis..."):
            st.session_state.power_plays_results = get_top_stocks(max_stocks=5, max_tickers=30)
            top_stocks = st.session_state.power_plays_results
    
    # Display each top stock
    for i, stock in enumerate(top_stocks):
        ticker = stock['ticker']
        company_name = stock['company_name']
        buy_rating = stock['buy_rating']
        analysis = stock['analysis']
        
        # Create rank badge
        rank_badge = f"""
        <div style="display: inline-block; background-color: rgba(59, 130, 246, 0.8); 
                    color: white; border-radius: 50%; width: 30px; height: 30px; 
                    text-align: center; line-height: 30px; font-weight: bold; margin-right: 10px;">
            #{i+1}
        </div>
        """
        
        # Display header with rank
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            {rank_badge}
            <h2 style="margin: 0;">{ticker}: {company_name}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Display buy rating
        color = ""
        if buy_rating >= 7:
            color = "green"
            rating_text = "BUY"
        elif buy_rating >= 4:
            color = "orange"
            rating_text = "HOLD"
        else:
            color = "red"
            rating_text = "SELL"
        
        # Rating display
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 20px 0;">
            <div style="display: flex; flex-direction: column; align-items: center; 
                       background-color: rgba(17, 24, 39, 0.7); border-radius: 12px; 
                       padding: 20px 30px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); 
                       border: 3px solid {color}; width: 180px;">
                <div style="font-size: 42px; font-weight: bold; margin-bottom: 5px; 
                           text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3); color: white;">
                    {buy_rating:.1f}
                </div>
                <div style="font-size: 14px; color: #e5e7eb; text-transform: uppercase; 
                           letter-spacing: 1px; margin-bottom: 10px;">
                    BUY RATING
                </div>
                <div style="font-size: 22px; font-weight: bold; text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3); 
                           color: {color};">
                    {rating_text}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display analysis
        st.markdown(analysis, unsafe_allow_html=True)
        
        # Add horizontal separator except for the last item
        if i < len(top_stocks) - 1:
            st.markdown("<hr style='margin-top: 30px; margin-bottom: 30px; border-color: rgba(59, 130, 246, 0.2);'>", unsafe_allow_html=True)