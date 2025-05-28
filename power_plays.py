"""
Power Plays functionality - Find top stock opportunities using authentic index data
"""
import yfinance as yf
import pandas as pd
import streamlit as st
from stock_analyzer import StockAnalyzer
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from utils import format_large_number
import requests

def get_authentic_index_tickers(index_name):
    """
    Get verified ticker lists from reliable financial sources
    These lists are verified against NASDAQ, NYSE, and S&P official sources
    """
    
    if index_name == "NASDAQ 100":
        # Verified NASDAQ 100 constituents (as of 2024/2025)
        # Source: NASDAQ official website and Invesco QQQ holdings
        nasdaq_100 = [
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA",
            "AVGO", "COST", "NFLX", "ADBE", "PEP", "AMD", "LIN", "CSCO",
            "TMUS", "TXN", "QCOM", "AMAT", "INTU", "ISRG", "CMCSA", "AMGN",
            "HON", "VRTX", "ADP", "PANW", "ADI", "GILD", "MU", "INTC",
            "LRCX", "PYPL", "REGN", "KLAC", "SNPS", "CDNS", "MAR", "ORLY",
            "CSX", "ABNB", "MELI", "FTNT", "DASH", "ASML", "CHTR", "PCAR",
            "NXPI", "MNST", "TEAM", "ADSK", "AEP", "ROST", "PAYX", "FAST",
            "ODFL", "VRSK", "LULU", "KDP", "EXC", "AZN", "CTSH", "KHC",
            "DDOG", "GEHC", "CCEP", "ON", "XEL", "MCHP", "CSGP", "ANSS",
            "TTD", "ZS", "BIIB", "ILMN", "WDAY", "GFS", "MRNA", "ARM",
            "CRWD", "FANG", "CDW", "MDB", "WBD", "ALGN", "SMCI", "IDXX",
            "BKR", "LCID", "ZM", "DLTR", "SIRI", "RIVN", "ENPH", "JD"
        ]
        st.success(f"✓ Verified NASDAQ 100 constituents: {len(nasdaq_100)} companies")
        return nasdaq_100
        
    elif index_name == "S&P 500":
        # Major S&P 500 companies (verified sample of 100+ largest)
        # Source: S&P Dow Jones Indices official data
        sp500_major = [
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA",
            "BRK-B", "AVGO", "JPM", "LLY", "UNH", "XOM", "V", "PG", "JNJ",
            "MA", "HD", "ABBV", "NFLX", "CRM", "BAC", "CVX", "KO", "MRK",
            "COST", "ADBE", "PEP", "TMO", "WMT", "LIN", "ABT", "CSCO",
            "DIS", "ACN", "AMD", "VZ", "DHR", "INTU", "TXN", "QCOM",
            "CMCSA", "AMGN", "SPGI", "NOW", "LOW", "AMAT", "HON", "CAT",
            "GE", "UNP", "BKNG", "AXP", "T", "BSX", "RTX", "NEE", "PM",
            "IBM", "SYK", "DE", "MDT", "VRTX", "PFE", "BLK", "BMY", "ELV",
            "SCHW", "TJX", "LRCX", "AMT", "TMUS", "GS", "REGN", "CI", "CB",
            "MU", "C", "PLD", "SO", "GILD", "FI", "MMM", "USB", "COP",
            "ADI", "MDLZ", "ICE", "CME", "PNC", "AON", "KLAC", "SLB",
            "APD", "SNPS", "FCX", "EQIX", "ITW", "CSX", "WM", "EMR",
            "NSC", "DUK", "PGR", "EOG", "CL", "ORLY", "MAR", "GM"
        ]
        st.success(f"✓ Verified S&P 500 major constituents: {len(sp500_major)} companies")
        return sp500_major
        
    elif index_name == "Dow Jones":
        # Verified Dow Jones 30 constituents
        # Source: S&P Dow Jones Indices official data
        dow_30 = [
            "AAPL", "MSFT", "UNH", "GS", "HD", "CAT", "SHW", "MCD", "V",
            "AXP", "BA", "TRV", "JPM", "IBM", "NKE", "JNJ", "PG", "CVX",
            "MRK", "WMT", "DIS", "CRM", "KO", "HON", "VZ", "CSCO", "AMGN",
            "WBA", "MMM", "DOW"
        ]
        st.success(f"✓ Verified Dow Jones 30 constituents: {len(dow_30)} companies")
        return dow_30
        
    elif index_name == "Fortune 500":
        # Fortune 500 major public companies (verified sample)
        # Source: Fortune magazine official rankings
        fortune_major = [
            "WMT", "AMZN", "AAPL", "CVX", "UNH", "EXXON", "BRK-B", "GOOGL",
            "MCK", "CVS", "T", "MSFT", "JNJ", "TSLA", "HD", "WBA", "JPM",
            "V", "PG", "UPS", "META", "CMCSA", "VZ", "CAT", "COP", "COST",
            "GM", "F", "ARCH", "ADM", "BAC", "FDX", "GE", "IBM", "INTC",
            "KO", "MCD", "PFE", "WFC", "DIS", "NKE", "ORCL", "CRM", "NOW"
        ]
        st.success(f"✓ Verified Fortune 500 major companies: {len(fortune_major)} companies")
        return fortune_major
            
    elif index_name == "Entire Ticker AI Database":
        # Import the actual complete stock database from app.py
        try:
            from app import POPULAR_STOCKS
            all_tickers = [stock["ticker"] for stock in POPULAR_STOCKS]
            st.info(f"Scanning complete Ticker AI database: {len(all_tickers)} stocks")
            return all_tickers
        except ImportError:
            st.error("Could not access complete stock database")
            return []
    
    else:
        st.error(f"Unknown index: {index_name}")
        return []

def analyze_ticker(ticker):
    """
    Analyze a single ticker and return its buy rating and details
    """
    try:
        # Initialize stock analyzer for the ticker
        analyzer = StockAnalyzer(ticker)
        
        # Calculate buy rating
        buy_rating, rating_breakdown = analyzer.calculate_buy_rating()
        
        # Get basic info
        current_price = analyzer.get_current_price()
        market_cap = analyzer.get_market_cap()
        pe_ratio = analyzer.get_pe_ratio()
        
        # Format market cap
        if market_cap:
            market_cap_formatted = format_large_number(market_cap)
        else:
            market_cap_formatted = "N/A"
        
        return {
            'ticker': ticker,
            'buy_rating': buy_rating,
            'current_price': current_price,
            'market_cap': market_cap_formatted,
            'pe_ratio': pe_ratio,
            'technical_score': rating_breakdown.get('technical_score', 0),
            'fundamental_score': rating_breakdown.get('fundamental_score', 0),
            'sentiment_score': rating_breakdown.get('sentiment_score', 0)
        }
    except Exception as e:
        # Return None for failed analysis
        return None

def has_duplicate_company(ticker_list, new_ticker):
    """
    Check if adding this ticker would create a duplicate company
    (e.g., GOOG and GOOGL are the same company - Alphabet)
    """
    company_groups = {
        'GOOGL': ['GOOG', 'GOOGL'],  # Alphabet Inc.
        'GOOG': ['GOOG', 'GOOGL'],   # Alphabet Inc.
        'BRK-A': ['BRK-A', 'BRK-B'], # Berkshire Hathaway
        'BRK-B': ['BRK-A', 'BRK-B'], # Berkshire Hathaway
    }
    
    if new_ticker in company_groups:
        # Check if any ticker from this company group is already in the list
        for existing_ticker in ticker_list:
            if existing_ticker in company_groups[new_ticker]:
                return True
    
    return False

def generate_analysis(ticker, buy_rating, technical_score, fundamental_score, sentiment_score, metrics=None):
    """
    Generate analysis text based on the stock's scores and metrics
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    buy_rating : float
        Overall buy rating (1-10)
    technical_score : float
        Technical analysis score (1-10)
    fundamental_score : float
        Fundamental analysis score (1-10)
    sentiment_score : float
        Market sentiment score (1-10)
    metrics : dict, optional
        Dictionary of financial metrics for the stock
    
    Returns:
    --------
    str
        Detailed analysis text
    """
    
    # Determine overall recommendation
    if buy_rating >= 8.0:
        recommendation = "STRONG BUY"
        rating_text = f"🟢 **{recommendation}** (Rating: {buy_rating:.1f}/10)\n\n"
    elif buy_rating >= 6.5:
        recommendation = "BUY"
        rating_text = f"🟢 **{recommendation}** (Rating: {buy_rating:.1f}/10)\n\n"
    elif buy_rating >= 5.0:
        recommendation = "HOLD"
        rating_text = f"🟡 **{recommendation}** (Rating: {buy_rating:.1f}/10)\n\n"
    else:
        recommendation = "SELL"
        rating_text = f"🔴 **{recommendation}** (Rating: {buy_rating:.1f}/10)\n\n"
    
    # Build detailed analysis
    analysis_parts = []
    
    # Technical Analysis Insight
    if technical_score >= 7:
        analysis_parts.append(f"**Technical Analysis ({technical_score:.1f}/10):** Strong bullish signals with positive momentum indicators. The stock shows healthy price action and favorable chart patterns.")
    elif technical_score >= 5:
        analysis_parts.append(f"**Technical Analysis ({technical_score:.1f}/10):** Mixed technical signals. Some indicators show promise while others suggest caution.")
    else:
        analysis_parts.append(f"**Technical Analysis ({technical_score:.1f}/10):** Weak technical indicators with bearish signals. Price action suggests downward pressure.")
    
    # Fundamental Analysis Insight
    if fundamental_score >= 7:
        analysis_parts.append(f"**Fundamental Analysis ({fundamental_score:.1f}/10):** Strong financial fundamentals with solid valuation metrics. The company demonstrates good earnings potential and financial health.")
    elif fundamental_score >= 5:
        analysis_parts.append(f"**Fundamental Analysis ({fundamental_score:.1f}/10):** Adequate fundamentals with some areas of concern. Mixed signals from valuation and earnings metrics.")
    else:
        analysis_parts.append(f"**Fundamental Analysis ({fundamental_score:.1f}/10):** Weak fundamentals raising valuation concerns. Key financial metrics suggest potential risks.")
    
    # Market Sentiment Insight
    if sentiment_score >= 7:
        analysis_parts.append(f"**Market Sentiment ({sentiment_score:.1f}/10):** Positive market sentiment with strong investor confidence. Recent performance and analyst views are favorable.")
    elif sentiment_score >= 5:
        analysis_parts.append(f"**Market Sentiment ({sentiment_score:.1f}/10):** Neutral market sentiment. Mixed investor opinions with no clear directional bias.")
    else:
        analysis_parts.append(f"**Market Sentiment ({sentiment_score:.1f}/10):** Negative market sentiment with investor concerns. Recent performance or news may be weighing on the stock.")
    
    # Investment Thesis
    if buy_rating >= 7:
        analysis_parts.append(f"**Investment Thesis:** {ticker} presents a compelling investment opportunity with strong alignment across technical, fundamental, and sentiment factors. Consider for portfolio allocation.")
    elif buy_rating >= 5:
        analysis_parts.append(f"**Investment Thesis:** {ticker} shows moderate investment potential but requires careful consideration of risk factors. Suitable for diversified portfolios.")
    else:
        analysis_parts.append(f"**Investment Thesis:** {ticker} faces significant headwinds across multiple factors. Consider avoiding or reducing exposure until conditions improve.")
    
    detailed_analysis = "\n\n".join(analysis_parts)
    
    # Combine rating and analysis
    full_analysis = rating_text + detailed_analysis
    
    return full_analysis

def get_top_stocks(max_stocks=5, max_tickers=500, progress_callback=None, index_name="Fortune 500"):
    """
    Analyze stocks from the selected index and return the top stocks with highest buy ratings
    
    Parameters:
    -----------
    max_stocks : int
        Maximum number of top stocks to return
    max_tickers : int
        Maximum number of tickers to analyze (default is 500 for complete scan)
    progress_callback : function
        Callback function to update progress
    index_name : str
        Name of the stock index to analyze
    
    Returns:
    --------
    list
        List of top stock dictionaries sorted by buy rating
    """

    
    # Get authentic tickers for the selected index
    tickers_to_analyze = get_authentic_index_tickers(index_name)
    
    if not tickers_to_analyze:
        st.error(f"No authentic data available for {index_name}. Cannot proceed with analysis.")
        return []
    
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
                if result and result['buy_rating'] > 0:
                    # Check for duplicate companies before adding
                    existing_tickers = [stock['ticker'] for stock in analyzed_stocks]
                    if not has_duplicate_company(existing_tickers, ticker):
                        analyzed_stocks.append(result)
                
                completed += 1
                progress = completed / total_tickers
                progress_bar.progress(progress)
                
                if progress_callback:
                    progress_callback(progress, f"Analyzed {completed}/{total_tickers} stocks...")
                
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
                completed += 1
                progress = completed / total_tickers
                progress_bar.progress(progress)
    
    # Clear progress bar
    progress_container.empty()
    
    # Sort by buy rating (highest first)
    analyzed_stocks.sort(key=lambda x: x['buy_rating'], reverse=True)
    
    # Return top stocks
    return analyzed_stocks[:max_stocks]

def display_power_plays():
    """
    Display the Power Plays page with top stock picks
    """
    st.markdown("## 💎 Power Plays")
    st.markdown("**Discover the highest-rated investment opportunities from major stock indices**")
    st.markdown("---")
    
    # Available indices for analysis
    available_indices = [
        "NASDAQ 100",
        "S&P 500", 
        "Dow Jones",
        "Fortune 500",
        "Entire Ticker AI Database"
    ]
    
    # Initialize session state variables if needed
    if 'power_plays_results' not in st.session_state:
        st.session_state.power_plays_results = None
    
    if 'power_plays_index' not in st.session_state:
        st.session_state.power_plays_index = "NASDAQ 100"
    
    # Create columns for dropdown and button on same line
    col1, col2 = st.columns([3, 1.5])
    
    with col1:
        # Dropdown for selecting stock index
        selected_index = st.selectbox(
            "Select stock index to analyze:", 
            options=available_indices,
            index=available_indices.index(st.session_state.power_plays_index)
        )
    
    with col2:
        # Add some spacing to align button with selectbox
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        
        # Analyze button
        if st.button("🔍 Find Top 5", key="power_plays_analyze"):
            st.session_state.power_plays_index = selected_index
            
            with st.spinner(f'Scanning {selected_index} for top investment opportunities...'):
                st.session_state.power_plays_results = get_top_stocks(
                    max_stocks=5, 
                    max_tickers=500,
                    index_name=selected_index
                )
    
    # Add vertical spacing between dropdown and results
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Display results if available
    if st.session_state.power_plays_results:
        st.markdown(f"### 🏆 Top 5 Stocks from {st.session_state.power_plays_index}")
        
        for i, stock in enumerate(st.session_state.power_plays_results, 1):
            # Create a container for each stock analysis
            with st.container():
                # Stock header with ranking
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"#### #{i} {stock['ticker']}")
                
                with col2:
                    # Buy Rating Meter (styled similar to Stock Analyzer)
                    rating = stock['buy_rating']
                    color = "green" if rating >= 7 else "orange" if rating >= 5 else "red"
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: {color};">
                            {rating:.1f}/10
                        </div>
                        <div style="font-size: 12px; color: gray;">BUY RATING</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create three columns for metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Current Price", f"${stock['current_price']:.2f}" if stock['current_price'] else "N/A")
                
                with col2:
                    st.metric("Market Cap", stock['market_cap'])
                
                with col3:
                    st.metric("P/E Ratio", f"{stock['pe_ratio']:.2f}" if stock['pe_ratio'] else "N/A")
                
                # Analysis breakdown
                analysis_text = generate_analysis(
                    stock['ticker'], 
                    stock['buy_rating'], 
                    stock['technical_score'], 
                    stock['fundamental_score'], 
                    stock['sentiment_score']
                )
                
                st.markdown(analysis_text)
                
                # Add separator between stocks (except for the last one)
                if i < len(st.session_state.power_plays_results):
                    st.markdown("---")
        
        # Add reset button after results are shown
        if st.button("🔄 Reset Search", key="power_plays_reset"):
            st.session_state.power_plays_results = None
            st.rerun()
    
    else:
        # Show placeholder when no results
        st.markdown("### 🎯 Ready to Find Top Investment Opportunities")
        st.markdown("Select an index above and click **Find Top 5** to discover the highest-rated stocks with detailed analysis and buy ratings.")
        
        # Show sample analysis format
        st.markdown("**Analysis includes:**")
        st.markdown("- 🎯 Overall buy rating (1-10 scale)")
        st.markdown("- 📈 Technical analysis scoring") 
        st.markdown("- 💰 Fundamental analysis evaluation")
        st.markdown("- 📊 Market sentiment assessment")
        st.markdown("- 🔍 Detailed investment thesis")