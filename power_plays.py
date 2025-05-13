"""
Power Plays functionality - Find top stock opportunities in Fortune 500
"""
import yfinance as yf
import pandas as pd
import streamlit as st
from stock_analyzer import StockAnalyzer
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from utils import format_large_number

# Stock indices for analysis
STOCK_INDICES = {
    "Fortune 500": [
        "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "NVDA", "UNH", "JNJ",
        "JPM", "V", "PG", "MA", "HD", "ABBV", "MRK", "XOM", "BAC", "CVX", 
        "LLY", "PFE", "KO", "PEP", "TMO", "COST", "AVGO", "DIS", "WMT", "CSCO",
        "ABT", "ACN", "MCD", "VZ", "CRM", "NKE", "CMCSA", "ADBE", "ORCL", "DHR",
        "IBM", "PM", "UPS", "AMD", "TXN", "INTC", "QCOM", "COP", "T", "AMGN"
    ],
    "S&P 500 Top 50": [
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "GOOG", "TSLA", "BRK-B", "LLY",
        "AVGO", "UNH", "JPM", "V", "XOM", "JNJ", "PG", "MA", "HD", "MRK", 
        "COST", "ABBV", "CVX", "PEP", "ADBE", "WMT", "CRM", "KO", "BAC", "TMO",
        "MCD", "ACN", "CSCO", "LIN", "AMD", "DIS", "WFC", "ABT", "CMCSA", "NFLX",
        "TXN", "COP", "INTC", "PM", "ORCL", "TMUS", "DHR", "CAT", "NKE", "VZ"
    ],
    "Dow Jones": [
        "AAPL", "MSFT", "UNH", "GS", "HD", "MCD", "CAT", "V", "TRV", "JPM",
        "AMGN", "BA", "CRM", "HON", "JNJ", "PG", "AXP", "IBM", "MRK", "WMT",
        "DIS", "MMM", "CVX", "KO", "CSCO", "DOW", "NKE", "INTC", "VZ", "WBA"
    ],
    "NASDAQ-100 Top 30": [
        "AAPL", "MSFT", "AMZN", "NVDA", "META", "TSLA", "GOOGL", "GOOG", "AVGO", "ADBE",
        "COST", "PEP", "CSCO", "AMD", "CMCSA", "TMUS", "NFLX", "INTC", "TXN", "QCOM", 
        "HON", "INTU", "AMAT", "ISRG", "BKNG", "SBUX", "MDLZ", "AMGN", "ADI", "PYPL"
    ],
    "Tech Giants": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AVGO", "ADBE", "CRM",
        "ORCL", "CSCO", "IBM", "INTC", "AMD", "QCOM", "TXN", "NFLX", "PYPL", "AMAT",
        "MU", "NOW", "INTU", "SNPS", "CDNS", "PANW", "WDAY", "ADSK", "NET", "ZS"
    ]
}

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
        
        # Get key financial metrics
        market_cap = info.get('marketCap', None)
        pe_ratio = info.get('trailingPE', None)
        eps = info.get('trailingEps', None)
        revenue = info.get('totalRevenue', None)
        dividend_yield = info.get('dividendYield', None)
        target_price = info.get('targetMeanPrice', None)
        current_price = analyzer.get_current_price()
        price_change = analyzer.get_price_change()
        
        # Additional data for detailed analysis
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        forward_pe = info.get('forwardPE', None)
        peg_ratio = info.get('pegRatio', None)
        profit_margin = info.get('profitMargins', None)
        
        # Format metrics
        formatted_metrics = {
            'market_cap': format_large_number(market_cap) if market_cap else 'N/A',
            'pe_ratio': f"{pe_ratio:.2f}" if pe_ratio else 'N/A',
            'eps': f"${eps:.2f}" if eps else 'N/A',
            'revenue': format_large_number(revenue) if revenue else 'N/A',
            'dividend_yield': f"{dividend_yield*100:.2f}%" if dividend_yield else 'N/A',
            'target_price': f"${target_price:.2f}" if target_price else 'N/A',
            'current_price': f"${current_price:.2f}" if current_price else 'N/A',
            'sector': sector,
            'industry': industry,
            'forward_pe': f"{forward_pe:.2f}" if forward_pe else 'N/A',
            'peg_ratio': f"{peg_ratio:.2f}" if peg_ratio else 'N/A',
            'profit_margin': f"{profit_margin*100:.2f}%" if profit_margin else 'N/A'
        }
        
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
        analysis = generate_analysis(ticker, buy_rating, technical_score, fundamental_score, sentiment_score, formatted_metrics)
        
        return {
            'ticker': ticker,
            'company_name': company_name,
            'buy_rating': buy_rating,
            'rating_components': rating_components,
            'analysis': analysis,
            'metrics': formatted_metrics
        }
    except Exception as e:
        # If there's an error, return None
        print(f"Error analyzing {ticker}: {str(e)}")
        return None

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
        rating_text = f"**Strong Buy ({buy_rating:.1f}/10):** {ticker} presents a compelling investment case based on {strength_text}."
    elif buy_rating >= 6:
        strength_text = ", ".join(strengths) if strengths else "several positive indicators"
        rating_text = f"**Buy ({buy_rating:.1f}/10):** {ticker} shows favorable characteristics including {strength_text}."
    elif buy_rating >= 4:
        if strengths and weaknesses:
            rating_text = f"**Hold ({buy_rating:.1f}/10):** {ticker} shows mixed signals with {', '.join(strengths)} but also {', '.join(weaknesses)}."
        else:
            rating_text = f"**Hold ({buy_rating:.1f}/10):** {ticker} currently presents a balanced risk-reward profile."
    elif buy_rating >= 2.5:
        weakness_text = ", ".join(weaknesses) if weaknesses else "various concerning factors"
        rating_text = f"**Sell ({buy_rating:.1f}/10):** {ticker} faces challenges including {weakness_text}."
    else:
        weakness_text = ", ".join(weaknesses) if weaknesses else "significant negative indicators"
        rating_text = f"**Strong Sell ({buy_rating:.1f}/10):** {ticker} faces major headwinds including {weakness_text}."
    
    # Add detailed metrics if available
    detailed_analysis = ""
    if metrics:
        # Format PE ratio analysis
        pe_text = ""
        if metrics.get('pe_ratio') != 'N/A' and metrics.get('forward_pe') != 'N/A':
            pe_ratio = float(metrics.get('pe_ratio').replace('N/A', '0'))
            try:
                forward_pe = float(metrics.get('forward_pe').replace('N/A', '0'))
                if pe_ratio > 0 and forward_pe > 0:
                    if forward_pe < pe_ratio:
                        pe_text = f"The forward P/E ({metrics['forward_pe']}) is lower than the trailing P/E ({metrics['pe_ratio']}), potentially indicating projected earnings growth. "
                    else:
                        pe_text = f"Current P/E ratio is {metrics['pe_ratio']} with a forward P/E of {metrics['forward_pe']}. "
            except:
                pe_text = f"Current P/E ratio is {metrics['pe_ratio']}. "
        elif metrics.get('pe_ratio') != 'N/A':
            pe_text = f"Current P/E ratio is {metrics['pe_ratio']}. "
        
        # Format market cap and sector
        cap_sector_text = ""
        if metrics.get('market_cap') != 'N/A':
            cap_sector_text += f"{ticker} has a market capitalization of {metrics['market_cap']} "
            if metrics.get('sector') != 'N/A':
                cap_sector_text += f"in the {metrics['sector']} sector. "
            else:
                cap_sector_text += ". "
        
        # Format profitability
        profit_text = ""
        if metrics.get('profit_margin') != 'N/A':
            try:
                profit_margin = float(metrics.get('profit_margin').replace('%', '').replace('N/A', '0'))
                if profit_margin > 15:
                    profit_text = f"The company shows an impressive profit margin of {metrics['profit_margin']}, indicating strong operational efficiency. "
                elif profit_margin > 0:
                    profit_text = f"With a profit margin of {metrics['profit_margin']}, the company is maintaining positive returns. "
                else:
                    profit_text = f"The company's current profit margin is {metrics['profit_margin']}, indicating profitability challenges. "
            except:
                pass
        
        # Format valuation
        valuation_text = ""
        if metrics.get('peg_ratio') != 'N/A':
            try:
                peg = float(metrics.get('peg_ratio').replace('N/A', '0'))
                if 0 < peg < 1:
                    valuation_text = f"With a PEG ratio of {metrics['peg_ratio']}, the stock appears potentially undervalued relative to its growth prospects. "
                elif peg >= 1:
                    valuation_text = f"The PEG ratio of {metrics['peg_ratio']} suggests the stock may be fairly valued to slightly overvalued. "
            except:
                pass
        
        # Format price target
        target_text = ""
        if metrics.get('target_price') != 'N/A' and metrics.get('current_price') != 'N/A':
            try:
                target = float(metrics.get('target_price').replace('$', '').replace('N/A', '0'))
                current = float(metrics.get('current_price').replace('$', '').replace('N/A', '0'))
                if target > current:
                    upside = ((target / current) - 1) * 100
                    target_text = f"Analysts have a mean price target of {metrics['target_price']}, suggesting a {upside:.1f}% upside potential. "
                else:
                    downside = ((1 - target / current)) * 100
                    target_text = f"The mean analyst price target of {metrics['target_price']} indicates a potential {downside:.1f}% downside from the current price. "
            except:
                pass
                
        # Combine all analysis components
        detailed_analysis = f"\n\n{cap_sector_text}{pe_text}{profit_text}{valuation_text}{target_text}"
        
    # Combine rating text with detailed analysis
    full_analysis = rating_text + detailed_analysis
    
    return full_analysis

def get_top_stocks(max_stocks=5, max_tickers=None, progress_callback=None, index_name="Fortune 500"):
    """
    Analyze stocks from the selected index and return the top stocks with highest buy ratings
    
    Parameters:
    -----------
    max_stocks : int
        Maximum number of top stocks to return
    max_tickers : int
        Maximum number of tickers to analyze (for testing/demo purposes)
    progress_callback : function
        Callback function to update progress
    index_name : str
        Name of the stock index to analyze (must be a key in STOCK_INDICES)
    
    Returns:
    --------
    list
        List of top stock dictionaries sorted by buy rating
    """
    st.write(f"Scanning {index_name} companies for investment opportunities...")
    
    # Get tickers for the selected index (fallback to Fortune 500 if the index doesn't exist)
    tickers_to_analyze = STOCK_INDICES.get(index_name, STOCK_INDICES["Fortune 500"])
    
    # Use a subset of tickers for testing if specified
    if max_tickers:
        tickers_to_analyze = tickers_to_analyze[:max_tickers]
    
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
    Power Plays delivers the five most compelling stock opportunities, ranked by AI-driven buy ratings. 
    Updated in real time, these picks offer a snapshot of where the strongest buying signals are—so you can act fast, with confidence.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state variables if needed
    if 'power_plays_results' not in st.session_state:
        st.session_state.power_plays_results = None
    
    if 'power_plays_index' not in st.session_state:
        st.session_state.power_plays_index = "Fortune 500"
    
    # Dropdown for selecting stock index
    selected_index = st.selectbox(
        "Select stock index to analyze:", 
        options=list(STOCK_INDICES.keys()),
        index=list(STOCK_INDICES.keys()).index(st.session_state.power_plays_index)
    )
    
    # Update the session state if index changed
    if selected_index != st.session_state.power_plays_index:
        st.session_state.power_plays_index = selected_index
        st.session_state.power_plays_results = None
    
    # Add some space
    st.write("")
    
    # Option to refresh analysis
    if st.button("Refresh Analysis"):
        with st.spinner(f"Refreshing analysis for {selected_index}..."):
            st.session_state.power_plays_results = get_top_stocks(
                max_stocks=5, 
                max_tickers=30, 
                index_name=selected_index
            )
    
    # Run analysis if no cached results
    if st.session_state.power_plays_results is None:
        with st.spinner(f"Analyzing {selected_index} stocks to find the best opportunities..."):
            # Get top stocks (limiting to 30 tickers for demo purposes to speed up execution)
            st.session_state.power_plays_results = get_top_stocks(
                max_stocks=5, 
                max_tickers=30,
                index_name=selected_index
            )
    
    # Display results
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
            <div style="font-size: 22px; font-weight: bold; margin: 0;">{ticker}: {company_name}</div>
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
    
    # Add a button to go back to stock search
    st.write("")  # Add some spacing
    if st.button("Back to Stock Search"):
        # Clear power_plays_results and go back to the stock search page
        st.session_state.power_plays_results = None
        st.session_state.current_page = "stock_search"
        st.rerun()
    
    # Add vertical buffer at the bottom to push content away from footer
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)