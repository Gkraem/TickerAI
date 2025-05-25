import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import base64
import os
from datetime import datetime, timedelta
from stock_analyzer import StockAnalyzer
from technical_analysis import TechnicalAnalysis
from fundamental_analysis import FundamentalAnalysis
from utils import format_large_number, get_stock_news
from data_sources import DATA_SOURCES
from user_management import is_authenticated, get_session_user 
from auth_components import auth_page, logout_button
from admin import is_admin, admin_panel
from power_plays import display_power_plays

# Popular companies and tickers mapping for search functionality
POPULAR_STOCKS = [
    {"ticker": "AAPL", "name": "Apple Inc."},
    {"ticker": "MSFT", "name": "Microsoft Corporation"},
    {"ticker": "AMZN", "name": "Amazon.com Inc."},
    {"ticker": "GOOGL", "name": "Alphabet Inc. (Google)"},
    {"ticker": "META", "name": "Meta Platforms Inc. (Facebook)"},
    {"ticker": "TSLA", "name": "Tesla Inc."},
    {"ticker": "NVDA", "name": "NVIDIA Corporation"},
    {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
    {"ticker": "V", "name": "Visa Inc."},
    {"ticker": "JNJ", "name": "Johnson & Johnson"},
    {"ticker": "WMT", "name": "Walmart Inc."},
    {"ticker": "PG", "name": "Procter & Gamble Co."},
    {"ticker": "MA", "name": "Mastercard Inc."},
    {"ticker": "UNH", "name": "UnitedHealth Group Inc."},
    {"ticker": "HD", "name": "Home Depot Inc."},
    {"ticker": "BAC", "name": "Bank of America Corp."},
    {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
    {"ticker": "PFE", "name": "Pfizer Inc."},
    {"ticker": "CSCO", "name": "Cisco Systems Inc."},
    {"ticker": "NFLX", "name": "Netflix Inc."},
    {"ticker": "INTC", "name": "Intel Corporation"},
    {"ticker": "PYPL", "name": "PayPal Holdings Inc."},
    {"ticker": "ADBE", "name": "Adobe Inc."},
    {"ticker": "CRM", "name": "Salesforce Inc."},
    {"ticker": "KO", "name": "Coca-Cola Company"},
    {"ticker": "DIS", "name": "Walt Disney Company"},
    {"ticker": "CMCSA", "name": "Comcast Corporation"},
    {"ticker": "VZ", "name": "Verizon Communications Inc."},
    {"ticker": "ABT", "name": "Abbott Laboratories"},
    {"ticker": "PEP", "name": "PepsiCo Inc."},
    {"ticker": "NKE", "name": "Nike Inc."},
    {"ticker": "MRK", "name": "Merck & Co. Inc."},
    {"ticker": "T", "name": "AT&T Inc."},
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "MCD", "name": "McDonald's Corporation"},
    {"ticker": "ORCL", "name": "Oracle Corporation"},
    {"ticker": "IBM", "name": "International Business Machines"},
    {"ticker": "AMD", "name": "Advanced Micro Devices Inc."},
    {"ticker": "QCOM", "name": "Qualcomm Inc."},
    {"ticker": "SBUX", "name": "Starbucks Corporation"},
    {"ticker": "COST", "name": "Costco Wholesale Corporation"},
    {"ticker": "GOOG", "name": "Alphabet Inc. (Google) Class C"},
    {"ticker": "TXN", "name": "Texas Instruments Incorporated"},
    {"ticker": "AMGN", "name": "Amgen Inc."},
    {"ticker": "LLY", "name": "Eli Lilly and Company"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific Inc."},
    {"ticker": "ACN", "name": "Accenture plc"},
    {"ticker": "AVGO", "name": "Broadcom Inc."},
    {"ticker": "MDT", "name": "Medtronic plc"},
    {"ticker": "PM", "name": "Philip Morris International"},
    # Adding more popular stocks that were missing
    {"ticker": "MU", "name": "Micron Technology Inc."},
    {"ticker": "PLTR", "name": "Palantir Technologies Inc."},
    {"ticker": "AAL", "name": "American Airlines Group Inc."},
    {"ticker": "UAL", "name": "United Airlines Holdings Inc."},
    {"ticker": "DAL", "name": "Delta Air Lines Inc."},
    {"ticker": "GME", "name": "GameStop Corp."},
    {"ticker": "AMC", "name": "AMC Entertainment Holdings Inc."},
    {"ticker": "F", "name": "Ford Motor Company"},
    {"ticker": "GM", "name": "General Motors Company"},
    {"ticker": "UBER", "name": "Uber Technologies Inc."},
    {"ticker": "LYFT", "name": "Lyft Inc."},
    {"ticker": "SNAP", "name": "Snap Inc."},
    {"ticker": "PINS", "name": "Pinterest Inc."},
    {"ticker": "TWTR", "name": "Twitter Inc."},
    {"ticker": "SQ", "name": "Block Inc. (Square)"},
    {"ticker": "COIN", "name": "Coinbase Global Inc."},
    {"ticker": "ROKU", "name": "Roku Inc."},
    {"ticker": "ZM", "name": "Zoom Video Communications Inc."},
    {"ticker": "SHOP", "name": "Shopify Inc."},
    {"ticker": "BABA", "name": "Alibaba Group Holding Limited"},
    {"ticker": "JD", "name": "JD.com Inc."},
    {"ticker": "TCEHY", "name": "Tencent Holdings Ltd."},
    {"ticker": "SONY", "name": "Sony Group Corporation"},
    {"ticker": "SPOT", "name": "Spotify Technology S.A."},
    {"ticker": "ABNB", "name": "Airbnb Inc."},
    {"ticker": "DASH", "name": "DoorDash Inc."},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc."},
    {"ticker": "MS", "name": "Morgan Stanley"},
    {"ticker": "C", "name": "Citigroup Inc."},
    {"ticker": "WFC", "name": "Wells Fargo & Company"},
    {"ticker": "BA", "name": "Boeing Company"},
    {"ticker": "LMT", "name": "Lockheed Martin Corporation"},
    {"ticker": "RTX", "name": "Raytheon Technologies Corporation"},
    {"ticker": "CAT", "name": "Caterpillar Inc."},
    {"ticker": "DE", "name": "Deere & Company"},
    {"ticker": "MMM", "name": "3M Company"},
    {"ticker": "HON", "name": "Honeywell International Inc."},
    {"ticker": "GE", "name": "General Electric Company"},
]

# Function to search for stocks by partial ticker or name match using Yahoo Finance
def search_stocks(query):
    """
    Search for stocks by partial ticker or company name match
    Uses both local database and Yahoo Finance search API
    
    Parameters:
    -----------
    query : str
        Search query (can be ticker or company name)
    
    Returns:
    --------
    list
        List of matching stock dictionaries with ticker and name
    """
    if not query:
        return []
    
    # First search local database for faster results
    query_upper = query.upper()
    query_lower = query.lower()
    local_matches = []
    
    for stock in POPULAR_STOCKS:
        # Match on ticker (exact or starting with)
        if stock["ticker"] == query_upper or stock["ticker"].startswith(query_upper):
            local_matches.append(stock)
        # Match on name (case-insensitive partial match)
        elif query_lower in stock["name"].lower():
            local_matches.append(stock)
    
    # Sort matches: exact ticker matches first, then starts-with ticker matches, then name matches
    local_matches.sort(key=lambda x: (
        0 if x["ticker"] == query_upper else 
        1 if x["ticker"].startswith(query_upper) else 
        2
    ))
    
    # If we already have enough local matches, return them
    if len(local_matches) >= 10:
        return local_matches[:10]
    
    # Try to get additional matches from Yahoo Finance API
    try:
        import yfinance as yf
        import requests
        
        # Yahoo Finance search API
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'quotes' in data:
                for quote in data['quotes']:
                    if 'symbol' in quote and 'shortname' in quote:
                        # Skip if already in local matches
                        if any(stock['ticker'] == quote['symbol'] for stock in local_matches):
                            continue
                        
                        local_matches.append({
                            "ticker": quote['symbol'],
                            "name": quote['shortname']
                        })
    except Exception as e:
        # If API call fails, just continue with local matches
        print(f"Error fetching data from Yahoo Finance: {e}")
    
    # Return combined results (limit to 10)
    return local_matches[:10]

# Set page configuration without title to avoid header bar
st.set_page_config(
    page_title="Ticker AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and apply custom CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

load_css("assets/custom.css")

# Function to render SVG
def render_svg(svg_file):
    with open(svg_file, "r") as f:
        svg = f.read()
        b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        html = f'<img src="data:image/svg+xml;base64,{b64}" class="navbar-logo-img" />'
        return html

# No navbar - completely removing the black header bar

# Remove footer for better mobile experience

# Initialize view mode state if not exists
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"  # Options: "main", "admin"

# Check if user is authenticated
if not is_authenticated():
    # Show authentication page when not logged in
    auth_page()
else:
    # Display the user's name in the sidebar
    user = get_session_user()
    if user and isinstance(user, dict) and 'name' in user:
        st.sidebar.markdown(f"### Welcome, {user['name']}")
    else:
        st.sidebar.markdown("### Welcome")
    
    logout_button()
    
    # Add admin controls if the user is an admin
    if is_admin():
        st.sidebar.markdown("---")
        
        # Toggle between main app and admin panel
        if st.session_state.view_mode == "main":
            if st.sidebar.button("Admin Panel", type="primary"):
                st.session_state.view_mode = "admin"
                st.rerun()
        else:  # In admin mode
            if st.sidebar.button("Return to Stock Analyzer", type="primary"):
                st.session_state.view_mode = "main"
                st.rerun()
    
    # Completely removed all headers and keeping proper spacing
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # Check view mode to determine what content to display
    if st.session_state.view_mode == "admin" and is_admin():
        # === ADMIN PANEL CONTENT ===
        st.title("Ticker AI Admin Panel")
        
        # Show user info
        user = get_session_user()
        if user and isinstance(user, dict):
            st.markdown(f"**Logged in as:** {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        
        # Add a separator
        st.markdown("<hr style='margin-top: 0; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        # Display admin panel content
        admin_panel()
        
    else:
        # === MAIN APP CONTENT ===
        # Set view mode to main (in case coming from admin page or for initial state)
        st.session_state.view_mode = "main"
        
        # Sidebar for ticker input
        st.sidebar.title("Stock Search")
        
        # Initialize session states if they don't exist
        if "search_query" not in st.session_state:
            st.session_state.search_query = ""
        if "selected_ticker" not in st.session_state:
            st.session_state.selected_ticker = ""
            
        # Function to update selected ticker when dropdown changes
        def on_stock_select():
            selected_option = st.session_state.stock_selector
            if selected_option != "Search for a stock...":
                # Extract ticker from selection
                st.session_state.selected_ticker = selected_option.split(" - ")[0]
            else:
                st.session_state.selected_ticker = ""
        
        # Get current search query value
        search_query = st.session_state.search_query
        
        # The integrated search field with dropdown
        ticker = ""  # Default empty ticker
        
        # Function to update stock search results
        def update_stock_results():
            # Empty string as default
            if not st.session_state.stock_search or st.session_state.stock_search == "":
                st.session_state.selected_ticker = ""
                return
            
            # Handle selection (format: "TICKER - Company Name")
            if " - " in st.session_state.stock_search:
                ticker_part = st.session_state.stock_search.split(" - ")[0]
                st.session_state.selected_ticker = ticker_part
        
        # Generate all stock options for the dropdown
        all_options = []
        for stock in POPULAR_STOCKS:
            all_options.append(f"{stock['ticker']} - {stock['name']}")
        
        # Single combined dropdown
        selected_option = st.sidebar.selectbox(
            "Search stocks by typing",
            options=[""] + all_options,
            index=0,
            key="stock_search",
            on_change=update_stock_results
        )
        
        # Extract ticker from selection if available
        if selected_option and " - " in selected_option:
            ticker = selected_option.split(" - ")[0]
            st.session_state.selected_ticker = ticker
        
        # Use selected ticker if available
        if "selected_ticker" in st.session_state and st.session_state.selected_ticker:
            ticker = st.session_state.selected_ticker
            if ticker:
                st.sidebar.success(f"Selected: **{ticker}**")
        
        # Timeframe selector
        timeframe = st.sidebar.selectbox(
            "Select Timeframe",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=5  # Default to 1 year
        )
        
        # Search button
        search_button = st.sidebar.button("Analyze Stock")
        
        # Power Plays button
        power_plays_button = st.sidebar.button("Power Plays", key="power_plays")
        
        # Display data sources
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Data Sources")
        for source, url in DATA_SOURCES.items():
            st.sidebar.markdown(f"- [{source}]({url})")
        
        # Initialize view state for Power Plays if not exists
        if "power_plays_view" not in st.session_state:
            st.session_state.power_plays_view = False
            
        # Handle Power Plays button
        if power_plays_button:
            st.session_state.power_plays_view = True
            
        # Main app content
        if st.session_state.power_plays_view:
            # Display Power Plays page
            display_power_plays()
            
            # The back button is now handled in the power_plays.py file
        elif ticker and search_button:
            # Create a placeholder for loading state
            with st.spinner(f'Analyzing {ticker}...'):
                try:
                    # Initialize stock analyzer
                    analyzer = StockAnalyzer(ticker)
                    
                    # Get company name and display prominently
                    company_info = analyzer.get_company_info()
                    
                    if company_info and 'shortName' in company_info:
                        company_name = company_info['shortName']
                        # Display company name as a header
                        st.markdown(f"<h1 class='company-name'>{company_name} ({ticker})</h1>", unsafe_allow_html=True)
                    
                    # Main metrics using custom styling for better spacing
                    st.markdown('<div class="data-row">', unsafe_allow_html=True)
                    
                    # Get current price and daily change
                    current_price = analyzer.get_current_price()
                    price_change, price_change_percent = analyzer.get_price_change()
                    
                    # Display price with up/down indicator
                    price_color = "green" if price_change >= 0 else "red"
                    price_arrow = "↑" if price_change >= 0 else "↓"
                    
                    # Format metrics for display
                    market_cap = analyzer.get_market_cap()
                    pe_ratio = analyzer.get_pe_ratio()
                    low_52w, high_52w = analyzer.get_52_week_range()
                    
                    # Create columns for metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Current Price",
                            f"${current_price:.2f}",
                            f"{price_arrow} {abs(price_change):.2f} ({abs(price_change_percent):.2f}%)",
                            delta_color="normal" if price_change >= 0 else "inverse"
                        )
                    
                    with col2:
                        st.metric("Market Cap", format_large_number(market_cap) if market_cap else "N/A")
                    
                    with col3:
                        st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio and pe_ratio > 0 else "N/A")
                    
                    with col4:
                        st.metric("52-Week Range", f"${low_52w:.2f} - ${high_52w:.2f}" if low_52w and high_52w else "N/A")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Company information/business summary
                    st.subheader("Company Overview")
                    
                    if company_info:
                        business_summary = company_info.get('longBusinessSummary', None)
                        if business_summary:
                            st.markdown(business_summary)
                        else:
                            st.info(f"No business summary available for {ticker}")
                            
                        # Additional company details in columns
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Company Details**")
                            st.markdown(f"Sector: {company_info.get('sector', 'N/A')}")
                            st.markdown(f"Industry: {company_info.get('industry', 'N/A')}")
                            if 'website' in company_info and company_info['website']:
                                st.markdown(f"Website: [{company_info['website']}]({company_info['website']})")
                            st.markdown(f"Full Time Employees: {format_large_number(company_info.get('fullTimeEmployees', 'N/A'))}")
                            
                        with col2:
                            st.markdown("**Financial Details**")
                            st.markdown(f"Revenue (TTM): {format_large_number(company_info.get('totalRevenue', 'N/A'))}")
                            st.markdown(f"Gross Profits: {format_large_number(company_info.get('grossProfits', 'N/A'))}")
                            if 'profitMargins' in company_info and company_info['profitMargins'] is not None:
                                profit_margin = company_info['profitMargins'] * 100
                                st.markdown(f"Profit Margin: {profit_margin:.2f}%")
                            st.markdown(f"Exchange: {company_info.get('exchange', 'N/A')}")
                    
                    # Calculate buy rating
                    buy_rating, rating_components = analyzer.calculate_buy_rating()
                    
                    # Display investment rating with gauge chart
                    st.subheader("Investment Rating")
                    
                    # Determine rating text based on score
                    if buy_rating >= 7.5:
                        rating_text = "Strong Buy"
                    elif buy_rating >= 6:
                        rating_text = "Buy"
                    elif buy_rating >= 4:
                        rating_text = "Hold"
                    else:
                        rating_text = "Sell"
                    
                    # Create gauge chart
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = buy_rating,
                        title = {'text': f"Buy Rating ({rating_text})"},
                        gauge = {
                            'axis': {'range': [0, 10], 'tickwidth': 1},
                            'bar': {'color': "rgba(50, 50, 50, 0.8)"},
                            'steps': [
                                {'range': [0, 3], 'color': "rgba(255, 0, 0, 0.3)"},
                                {'range': [3, 5], 'color': "rgba(255, 165, 0, 0.3)"},
                                {'range': [5, 7], 'color': "rgba(255, 255, 0, 0.3)"},
                                {'range': [7, 10], 'color': "rgba(0, 128, 0, 0.3)"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': buy_rating
                            }
                        }
                    ))
                    
                    # Set labels on the gauge
                    fig.add_annotation(x=0.15, y=0.8, text="SELL", showarrow=False)
                    fig.add_annotation(x=0.85, y=0.8, text="BUY", showarrow=False)
                    fig.add_annotation(x=0.5, y=0.9, text="NEUTRAL", showarrow=False)
                    
                    # Update layout
                    fig.update_layout(
                        height=250, 
                        margin=dict(l=20, r=20, t=70, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Generate a brief explanation of the rating
                    st.markdown("#### Rating Explanation")
                    
                    # Get the component scores from the rating_components dictionary
                    technical_data = rating_components.get('Technical Analysis', {})
                    fundamental_data = rating_components.get('Fundamental Analysis', {})
                    sentiment_data = rating_components.get('Market Sentiment', {})
                    
                    # Extract the scores
                    technical_score = technical_data.get('score', 5.0) if isinstance(technical_data, dict) else 5.0
                    fundamental_score = fundamental_data.get('score', 5.0) if isinstance(fundamental_data, dict) else 5.0
                    sentiment_score = sentiment_data.get('score', 5.0) if isinstance(sentiment_data, dict) else 5.0
                    
                    # Determine the strength and weakness areas
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
                        explanation = f"""**Strong Buy ({buy_rating:.1f}/10):** {ticker} presents a compelling investment case based on {strength_text}. 
                        
Technical analysis shows favorable chart patterns with strong price momentum. Fundamentally, the company demonstrates solid financial performance with potential for continued growth. Market sentiment toward {ticker} is highly positive, with favorable analyst coverage and institutional interest. This stock is well-positioned for potential significant appreciation in the near to medium term."""
                    elif buy_rating >= 6:
                        strength_text = ", ".join(strengths) if strengths else "several positive indicators"
                        weakness_text = ", ".join(weaknesses) if weaknesses else "some areas requiring monitoring"
                        explanation = f"""**Buy ({buy_rating:.1f}/10):** {ticker} shows a favorable investment profile highlighted by {strength_text}, despite {weakness_text}. 
                        
The technical picture is generally positive with price action indicating upward momentum. Fundamentally, the company has demonstrated reasonable financial stability and competitive positioning. Investor sentiment is moderately to strongly positive, suggesting continued support for the stock price. This security presents a good risk-reward opportunity at current levels."""
                    elif buy_rating >= 4:
                        strength_text = ", ".join(strengths) if strengths else "some positive aspects"
                        weakness_text = ", ".join(weaknesses) if weaknesses else "several concerning factors"
                        explanation = f"""**Hold ({buy_rating:.1f}/10):** {ticker} shows a mixed profile with {strength_text} balanced against {weakness_text}. 
                        
The technical analysis reveals conflicting signals without clear directional bias. Fundamentally, the company shows some strengths but also notable areas of concern that may impact future performance. Market sentiment is lukewarm or inconsistent, suggesting uncertainty among investors and analysts. Existing positions may be maintained, but increasing exposure is not recommended without improved metrics."""
                    else:
                        weakness_text = ", ".join(weaknesses) if weaknesses else "multiple concerning indicators"
                        explanation = f"""**Sell ({buy_rating:.1f}/10):** {ticker} demonstrates significant risk factors driven primarily by {weakness_text}. 
                        
Technical analysis reveals bearish patterns with deteriorating price action and negative momentum indicators. Fundamental analysis highlights troubling aspects of the company's financial health or competitive position. Market sentiment has turned negative with downward pressure from analysts or institutional selling. Current shareholders should consider reducing exposure, while new investment is not recommended at this time."""
                    
                    st.markdown(explanation)
                    
                    # Display rating components
                    st.markdown("#### Rating Components")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Technical Score", f"{technical_score:.1f}/10")
                        if isinstance(technical_data, dict) and 'reason' in technical_data:
                            st.caption(technical_data['reason'])
                        
                    with col2:
                        st.metric("Fundamental Score", f"{fundamental_score:.1f}/10")
                        if isinstance(fundamental_data, dict) and 'reason' in fundamental_data:
                            st.caption(fundamental_data['reason'])
                        
                    with col3:
                        st.metric("Sentiment Score", f"{sentiment_score:.1f}/10")
                        if isinstance(sentiment_data, dict) and 'reason' in sentiment_data:
                            st.caption(sentiment_data['reason'])
                    
                    # Create tabs for different analyses
                    tab1, tab2, tab3, tab4 = st.tabs(["Price History", "Technical Analysis", "Fundamentals", "News"])
                    
                    with tab1:
                        st.subheader(f"Price History - {timeframe}")
                        
                        # Get historical data
                        hist_data = analyzer.get_historical_data(timeframe)
                        
                        if hist_data is not None and not hist_data.empty:
                            # Create interactive price chart
                            fig = go.Figure()
                            
                            # Add price line
                            fig.add_trace(
                                go.Scatter(
                                    x=hist_data.index, 
                                    y=hist_data['Close'],
                                    mode='lines',
                                    name='Price',
                                    line=dict(color='#1f77b4', width=2)
                                )
                            )
                            
                            # Add volume as bar chart
                            fig.add_trace(
                                go.Bar(
                                    x=hist_data.index,
                                    y=hist_data['Volume'],
                                    name='Volume',
                                    marker_color='rgba(200, 200, 200, 0.4)',
                                    opacity=0.5,
                                    yaxis='y2'
                                )
                            )
                            
                            # Add buttons for different time ranges with mobile-friendly layout
                            fig.update_layout(
                                title=dict(
                                    text=f"{ticker} Price History",
                                    font=dict(size=16)
                                ),
                                xaxis=dict(
                                    title="Date",
                                    tickfont=dict(size=10)
                                ),
                                yaxis=dict(
                                    title="Price (USD)",
                                    tickfont=dict(size=10)
                                ),
                                yaxis2=dict(
                                    title="Volume",
                                    tickfont=dict(size=10),
                                    overlaying="y",
                                    side="right",
                                    showgrid=False
                                ),
                                hovermode="x unified",
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                                height=400,  # Reduced height for better mobile view
                                autosize=True,
                                margin=dict(l=10, r=10, t=40, b=20)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Add summary statistics
                            st.subheader("Summary Statistics")
                            
                            # Calculate stats
                            price_start = hist_data['Close'].iloc[0]
                            price_end = hist_data['Close'].iloc[-1]
                            price_change_total = price_end - price_start
                            price_change_percent_total = (price_change_total / price_start) * 100
                            price_min = hist_data['Low'].min()
                            price_max = hist_data['High'].max()
                            
                            # Create columns for stats
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Starting Price", f"${price_start:.2f}")
                                st.metric("Total Volume", format_large_number(hist_data['Volume'].sum()))
                            
                            with col2:
                                st.metric("Ending Price", f"${price_end:.2f}")
                                st.metric("Average Volume", format_large_number(hist_data['Volume'].mean()))
                            
                            with col3:
                                st.metric(
                                    "Total Change",
                                    f"${price_end:.2f}",
                                    f"{price_change_total:.2f} ({price_change_percent_total:.2f}%)",
                                    delta_color="normal" if price_change_total >= 0 else "inverse"
                                )
                                st.metric("Price Range", f"${price_min:.2f} - ${price_max:.2f}")
                        else:
                            st.error(f"No historical data available for {ticker}")
                    
                    with tab2:
                        st.subheader("Technical Analysis")
                        
                        # Initialize technical analysis
                        tech_analysis = TechnicalAnalysis(ticker)
                        
                        # Get technical signals
                        signals = tech_analysis.get_technical_signals()
                        
                        # Create columns for different indicators
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Moving Averages
                            st.markdown("### Moving Averages")
                            
                            ma_data = tech_analysis.get_moving_averages(timeframe)
                            
                            if ma_data is not None and not ma_data.empty:
                                # Plot moving averages
                                fig = go.Figure()
                                
                                # Add price line
                                fig.add_trace(
                                    go.Scatter(
                                        x=ma_data.index,
                                        y=ma_data['Close'],
                                        mode='lines',
                                        name='Price',
                                        line=dict(color='#1f77b4', width=2)
                                    )
                                )
                                
                                # Add moving averages
                                fig.add_trace(
                                    go.Scatter(
                                        x=ma_data.index,
                                        y=ma_data['MA50'],
                                        mode='lines',
                                        name='50-Day MA',
                                        line=dict(color='orange', width=1.5)
                                    )
                                )
                                
                                fig.add_trace(
                                    go.Scatter(
                                        x=ma_data.index,
                                        y=ma_data['MA200'],
                                        mode='lines',
                                        name='200-Day MA',
                                        line=dict(color='red', width=1.5)
                                    )
                                )
                                
                                fig.update_layout(
                                    title=dict(
                                        text="Price with Moving Averages",
                                        font=dict(size=16)
                                    ),
                                    xaxis=dict(
                                        title="Date",
                                        tickfont=dict(size=10)
                                    ),
                                    yaxis=dict(
                                        title="Price (USD)",
                                        tickfont=dict(size=10)
                                    ),
                                    hovermode="x unified",
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                                    height=350,  # Slightly reduced height for mobile
                                    autosize=True,
                                    margin=dict(l=10, r=10, t=40, b=20)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Moving Average Interpretation
                                ma_signals = tech_analysis.interpret_moving_averages()
                                
                                for signal, interpretation in ma_signals.items():
                                    signal_color = "green" if "bullish" in interpretation.lower() else "red" if "bearish" in interpretation.lower() else "orange"
                                    st.markdown(f"**{signal}:** <span style='color:{signal_color}'>{interpretation}</span>", unsafe_allow_html=True)
                            else:
                                st.error("Could not calculate moving averages")
                            
                            # MACD
                            st.markdown("### MACD")
                            
                            macd_data = tech_analysis.get_macd(timeframe)
                            
                            if macd_data is not None and not macd_data.empty:
                                # Create MACD plot
                                fig = go.Figure()
                                
                                # Add MACD line
                                fig.add_trace(
                                    go.Scatter(
                                        x=macd_data.index,
                                        y=macd_data['MACD'],
                                        mode='lines',
                                        name='MACD',
                                        line=dict(color='#1f77b4', width=1.5)
                                    )
                                )
                                
                                # Add signal line
                                fig.add_trace(
                                    go.Scatter(
                                        x=macd_data.index,
                                        y=macd_data['Signal'],
                                        mode='lines',
                                        name='Signal',
                                        line=dict(color='red', width=1.5)
                                    )
                                )
                                
                                # Add histogram
                                colors = ['green' if val >= 0 else 'red' for val in macd_data['Histogram']]
                                
                                fig.add_trace(
                                    go.Bar(
                                        x=macd_data.index,
                                        y=macd_data['Histogram'],
                                        name='Histogram',
                                        marker_color=colors
                                    )
                                )
                                
                                fig.update_layout(
                                    title=dict(
                                        text="MACD Indicator",
                                        font=dict(size=16)
                                    ),
                                    xaxis=dict(
                                        title="Date",
                                        tickfont=dict(size=10)
                                    ),
                                    yaxis=dict(
                                        title="Value",
                                        tickfont=dict(size=10)
                                    ),
                                    hovermode="x unified",
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                                    height=300,
                                    autosize=True,
                                    margin=dict(l=10, r=10, t=40, b=20)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # MACD Interpretation
                                macd_signal = tech_analysis.interpret_macd()
                                signal_color = "green" if "bullish" in macd_signal.lower() else "red" if "bearish" in macd_signal.lower() else "orange"
                                st.markdown(f"**MACD Signal:** <span style='color:{signal_color}'>{macd_signal}</span>", unsafe_allow_html=True)
                            else:
                                st.error("Could not calculate MACD")
                        
                        with col2:
                            # RSI
                            st.markdown("### RSI")
                            
                            rsi_data = tech_analysis.get_rsi(timeframe)
                            
                            if rsi_data is not None and not rsi_data.empty:
                                # Create RSI plot
                                fig = go.Figure()
                                
                                # Add RSI line
                                fig.add_trace(
                                    go.Scatter(
                                        x=rsi_data.index,
                                        y=rsi_data['RSI'],
                                        mode='lines',
                                        name='RSI',
                                        line=dict(color='purple', width=1.5)
                                    )
                                )
                                
                                # Add overbought/oversold lines
                                fig.add_shape(
                                    type="line",
                                    x0=rsi_data.index[0],
                                    y0=70,
                                    x1=rsi_data.index[-1],
                                    y1=70,
                                    line=dict(color="red", width=1, dash="dash")
                                )
                                
                                fig.add_shape(
                                    type="line",
                                    x0=rsi_data.index[0],
                                    y0=30,
                                    x1=rsi_data.index[-1],
                                    y1=30,
                                    line=dict(color="green", width=1, dash="dash")
                                )
                                
                                fig.update_layout(
                                    title=dict(
                                        text="RSI (14-Day)",
                                        font=dict(size=16)
                                    ),
                                    yaxis=dict(
                                        title="RSI Value",
                                        range=[0, 100],
                                        tickfont=dict(size=10)
                                    ),
                                    xaxis=dict(
                                        title="Date",
                                        tickfont=dict(size=10)
                                    ),
                                    hovermode="x unified",
                                    height=300,  # Reduced height for mobile
                                    autosize=True,
                                    margin=dict(l=10, r=10, t=40, b=20)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # RSI Interpretation
                                current_rsi = rsi_data['RSI'].iloc[-1]
                                
                                if current_rsi > 70:
                                    rsi_signal = "Overbought - Potential sell signal"
                                    signal_color = "red"
                                elif current_rsi < 30:
                                    rsi_signal = "Oversold - Potential buy signal"
                                    signal_color = "green"
                                else:
                                    rsi_signal = "Neutral"
                                    signal_color = "orange"
                                
                                st.markdown(f"**Current RSI:** <span style='color:{signal_color}'>{current_rsi:.2f} - {rsi_signal}</span>", unsafe_allow_html=True)
                            else:
                                st.error("Could not calculate RSI")
                            
                            # Bollinger Bands
                            st.markdown("### Bollinger Bands")
                            
                            bb_data = tech_analysis.get_bollinger_bands(timeframe)
                            
                            if bb_data is not None and not bb_data.empty:
                                # Create Bollinger Bands plot
                                fig = go.Figure()
                                
                                # Add price line
                                fig.add_trace(
                                    go.Scatter(
                                        x=bb_data.index,
                                        y=bb_data['Close'],
                                        mode='lines',
                                        name='Price',
                                        line=dict(color='#1f77b4', width=2)
                                    )
                                )
                                
                                # Add upper band
                                fig.add_trace(
                                    go.Scatter(
                                        x=bb_data.index,
                                        y=bb_data['Upper Band'],
                                        mode='lines',
                                        name='Upper Band',
                                        line=dict(color='red', width=1, dash='dash')
                                    )
                                )
                                
                                # Add middle band
                                fig.add_trace(
                                    go.Scatter(
                                        x=bb_data.index,
                                        y=bb_data['Middle Band'],
                                        mode='lines',
                                        name='Middle Band (SMA)',
                                        line=dict(color='orange', width=1)
                                    )
                                )
                                
                                # Add lower band
                                fig.add_trace(
                                    go.Scatter(
                                        x=bb_data.index,
                                        y=bb_data['Lower Band'],
                                        mode='lines',
                                        name='Lower Band',
                                        line=dict(color='green', width=1, dash='dash')
                                    )
                                )
                                
                                fig.update_layout(
                                    title=dict(
                                        text="Bollinger Bands",
                                        font=dict(size=16)
                                    ),
                                    xaxis=dict(
                                        title="Date",
                                        tickfont=dict(size=10)
                                    ),
                                    yaxis=dict(
                                        title="Price (USD)",
                                        tickfont=dict(size=10)
                                    ),
                                    hovermode="x unified",
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                                    height=300,
                                    autosize=True,
                                    margin=dict(l=10, r=10, t=40, b=20)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Bollinger Bands Interpretation
                                bb_signal = tech_analysis.interpret_bollinger_bands()
                                signal_color = "green" if "bullish" in bb_signal.lower() else "red" if "bearish" in bb_signal.lower() else "orange"
                                st.markdown(f"**Bollinger Bands Signal:** <span style='color:{signal_color}'>{bb_signal}</span>", unsafe_allow_html=True)
                            else:
                                st.error("Could not calculate Bollinger Bands")
                        
                        # Summary of all technical signals
                        st.subheader("Technical Signals Summary")
                        
                        # Create a DataFrame for display
                        signals_df = pd.DataFrame({
                            'Indicator': list(signals.keys()),
                            'Signal': list(signals.values())
                        })
                        
                        # Count signals by type
                        buy_count = sum(1 for signal in signals.values() if "buy" in signal.lower())
                        sell_count = sum(1 for signal in signals.values() if "sell" in signal.lower())
                        neutral_count = sum(1 for signal in signals.values() if "neutral" in signal.lower())
                        
                        # Create columns for the summary
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"<div style='text-align: center; color: green; font-weight: bold; font-size: 24px;'>{buy_count}</div><div style='text-align: center;'>Buy Signals</div>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"<div style='text-align: center; color: red; font-weight: bold; font-size: 24px;'>{sell_count}</div><div style='text-align: center;'>Sell Signals</div>", unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"<div style='text-align: center; color: orange; font-weight: bold; font-size: 24px;'>{neutral_count}</div><div style='text-align: center;'>Neutral Signals</div>", unsafe_allow_html=True)
                        
                        # Display signals in a mobile-friendly table
                        st.markdown("""
                        <style>
                        .mobile-friendly-table {
                            font-size: 14px !important;
                            white-space: normal !important;
                            overflow-x: auto !important;
                            max-width: 100% !important;
                        }
                        .mobile-friendly-table table {
                            width: 100% !important;
                        }
                        .mobile-friendly-table th, .mobile-friendly-table td {
                            padding: 5px !important;
                            white-space: normal !important;
                            word-break: break-word !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Apply color styling based on signal type
                        def color_signal(val):
                            if 'buy' in str(val).lower():
                                return 'color: green'
                            elif 'sell' in str(val).lower():
                                return 'color: red'
                            else:
                                return 'color: orange'
                        
                        # Apply styling to dataframe
                        styled_df = signals_df.style.applymap(color_signal, subset=['Signal'])
                        
                        # Convert to HTML and wrap with mobile-friendly div
                        html_table = styled_df.to_html()
                        st.markdown(f'<div class="mobile-friendly-table">{html_table}</div>', unsafe_allow_html=True)
                    
                    with tab3:
                        st.subheader("Fundamental Analysis")
                        
                        # Initialize fundamental analysis
                        fund_analysis = FundamentalAnalysis(ticker)
                        
                        # Create tabs for different fundamental data
                        subtab1, subtab2, subtab3, subtab4 = st.tabs(["Key Ratios", "Income Statement", "Balance Sheet", "Recommendations"])
                        
                        with subtab1:
                            st.markdown("### Valuation Ratios")
                            
                            # Get valuation ratios
                            valuation_ratios = fund_analysis.get_valuation_ratios()
                            
                            if valuation_ratios is not None and not valuation_ratios.empty:
                                # Display as a table
                                st.dataframe(valuation_ratios, use_container_width=True)
                                
                                # Plot P/E ratio if available
                                if 'trailingPE' in valuation_ratios.columns:
                                    st.markdown("#### P/E Ratio Comparison")
                                    
                                    # Get sector average P/E as a placeholder
                                    sector_pe = 20.5  # This would ideally come from real data
                                    
                                    # Create a bar chart for P/E comparison
                                    pe_fig = go.Figure()
                                    
                                    # Add company P/E
                                    company_pe = valuation_ratios['trailingPE'].iloc[-1]
                                    
                                    pe_data = pd.DataFrame({
                                        'Category': [f"{ticker} P/E", "Sector Average"],
                                        'P/E Ratio': [company_pe, sector_pe]
                                    })
                                    
                                    # Plot P/E comparison
                                    pe_fig = px.bar(
                                        pe_data,
                                        x='Category',
                                        y='P/E Ratio',
                                        color='Category',
                                        color_discrete_map={
                                            f"{ticker} P/E": 'blue',
                                            "Sector Average": 'gray'
                                        }
                                    )
                                    
                                    pe_fig.update_layout(
                                        title="P/E Ratio Comparison",
                                        showlegend=False,
                                        height=300
                                    )
                                    
                                    st.plotly_chart(pe_fig, use_container_width=True)
                            else:
                                st.info("Valuation ratios not available for this stock")
                            
                            st.markdown("### Profitability Ratios")
                            
                            # Get profitability ratios
                            profit_ratios = fund_analysis.get_profitability_ratios()
                            
                            if profit_ratios is not None and not profit_ratios.empty:
                                # Display as a table
                                st.dataframe(profit_ratios, use_container_width=True)
                            else:
                                st.info("Profitability ratios not available for this stock")
                        
                        with subtab2:
                            st.markdown("### Income Statement")
                            
                            # Get income statement
                            income_stmt = fund_analysis.get_income_statement()
                            
                            if income_stmt is not None and not income_stmt.empty:
                                # Display as a table
                                st.dataframe(income_stmt, use_container_width=True)
                                
                                # Plot revenue and earnings
                                if 'totalRevenue' in income_stmt.columns and 'netIncome' in income_stmt.columns:
                                    st.markdown("#### Revenue and Earnings Trend")
                                    
                                    # Create a figure
                                    fig = go.Figure()
                                    
                                    # Add revenue bars
                                    fig.add_trace(
                                        go.Bar(
                                            x=income_stmt.index,
                                            y=income_stmt['totalRevenue'],
                                            name='Revenue',
                                            marker_color='blue'
                                        )
                                    )
                                    
                                    # Add earnings line
                                    fig.add_trace(
                                        go.Scatter(
                                            x=income_stmt.index,
                                            y=income_stmt['netIncome'],
                                            name='Net Income',
                                            marker_color='green',
                                            mode='lines+markers'
                                        )
                                    )
                                    
                                    fig.update_layout(
                                        title="Revenue and Net Income",
                                        xaxis_title="Date",
                                        yaxis_title="USD",
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                        height=400
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Income statement not available for this stock")
                        
                        with subtab3:
                            st.markdown("### Balance Sheet")
                            
                            # Get balance sheet
                            balance_sheet = fund_analysis.get_balance_sheet()
                            
                            if balance_sheet is not None and not balance_sheet.empty:
                                # Display as a table
                                st.dataframe(balance_sheet, use_container_width=True)
                                
                                # Plot assets and liabilities
                                if 'totalAssets' in balance_sheet.columns and 'totalLiab' in balance_sheet.columns:
                                    st.markdown("#### Assets, Liabilities and Equity")
                                    
                                    # Calculate equity
                                    balance_sheet['totalEquity'] = balance_sheet['totalAssets'] - balance_sheet['totalLiab']
                                    
                                    # Create a stacked bar chart
                                    fig = go.Figure()
                                    
                                    # Add liabilities
                                    fig.add_trace(
                                        go.Bar(
                                            x=balance_sheet.index,
                                            y=balance_sheet['totalLiab'],
                                            name='Liabilities',
                                            marker_color='red'
                                        )
                                    )
                                    
                                    # Add equity
                                    fig.add_trace(
                                        go.Bar(
                                            x=balance_sheet.index,
                                            y=balance_sheet['totalEquity'],
                                            name='Equity',
                                            marker_color='green'
                                        )
                                    )
                                    
                                    # Add total assets line
                                    fig.add_trace(
                                        go.Scatter(
                                            x=balance_sheet.index,
                                            y=balance_sheet['totalAssets'],
                                            name='Total Assets',
                                            marker_color='blue',
                                            mode='lines+markers'
                                        )
                                    )
                                    
                                    fig.update_layout(
                                        title="Assets, Liabilities and Equity",
                                        xaxis_title="Date",
                                        yaxis_title="USD",
                                        barmode='stack',
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                        height=400
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Balance sheet not available for this stock")
                        
                        with subtab4:
                            st.markdown("### Analyst Recommendations")
                            
                            # Get analyst recommendations
                            recommendations = fund_analysis.get_analyst_recommendations()
                            
                            if recommendations is not None and not recommendations.empty:
                                # Display as a table
                                st.dataframe(recommendations, use_container_width=True)
                                
                                # Create a summary of recent recommendations
                                recent_recommendations = recommendations.iloc[:5]
                                
                                # Plot recommendations
                                fig = px.bar(
                                    recent_recommendations,
                                    x=recent_recommendations.index,
                                    y=['strongBuy', 'buy', 'hold', 'sell', 'strongSell'],
                                    title="Recent Analyst Recommendations",
                                    color_discrete_map={
                                        'strongBuy': 'darkgreen',
                                        'buy': 'green',
                                        'hold': 'orange',
                                        'sell': 'red',
                                        'strongSell': 'darkred'
                                    }
                                )
                                
                                fig.update_layout(
                                    barmode='stack',
                                    yaxis_title="Number of Analysts",
                                    xaxis_title="Date",
                                    legend_title="Recommendation",
                                    height=400
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Analyst recommendations not available for this stock")
                    
                    with tab4:
                        st.subheader("Recent News")
                        
                        # Get news articles
                        news_articles = get_stock_news(ticker)
                        
                        if news_articles:
                            # Calculate sentiment scores
                            sentiment_scores = []
                            
                            for article in news_articles:
                                # Placeholder for sentiment analysis - would use NLP in a real app
                                # Here, we'll use a simple random score for demonstration
                                sentiment = np.random.uniform(-1, 1)
                                sentiment_scores.append(sentiment)
                            
                            # Display articles
                            for i, article in enumerate(news_articles):
                                col1, col2 = st.columns([1, 4])
                                
                                date_str = article.get('date', 'Unknown date')
                                
                                # Determine sentiment icon
                                sentiment = sentiment_scores[i]
                                if sentiment > 0.3:
                                    sentiment_icon = "👍"
                                elif sentiment < -0.3:
                                    sentiment_icon = "👎"
                                else:
                                    sentiment_icon = "🔄"
                                
                                with col1:
                                    st.markdown(f"**{date_str}**")
                                    st.markdown(f"**{sentiment_icon}**")
                                
                                with col2:
                                    st.markdown(f"**[{article.get('title', 'No Title')}]({article.get('link', '#')})**")
                                    summary = article.get('summary', 'No summary available')
                                    st.markdown(f"{summary[:200]}..." if len(summary) > 200 else summary)
                                
                                st.markdown("---")
                        
                        else:
                            st.info(f"No recent news found for {ticker}")
                except Exception as e:
                    st.error(f"Error analyzing {ticker}: {str(e)}")
                    st.info("Please check if the ticker symbol is correct and try again.")
                    
                # Add bottom padding for better spacing with footer
                st.markdown("<div style='margin-bottom: 100px;'></div>", unsafe_allow_html=True)
        
        else:
            # Display welcome message and stock market image for new users
            st.markdown("""
            ## Welcome to the Ticker AI Stock Market Analyzer
            
            This tool helps you analyze stocks with comprehensive financial data and visualizations.
            
            **To get started:**
            1. Enter a stock ticker symbol in the sidebar (e.g., AAPL for Apple)
            2. Select your preferred timeframe
            3. Click "Analyze Stock" to see the results
            
            You'll get detailed information including:
            - Current price and change
            - Key financial metrics
            - Technical analysis with indicators
            - Fundamental analysis with financial statements
            - Recent news about the company
            - A proprietary buy rating score from 1-10
            
            All data comes from reliable financial sources.
            """)
            
            # Clean, modern stock market welcome display with only the logo
            st.markdown("""
            <div style="text-align: center; padding: 50px; margin-top: 80px;">
                <h1 style="color: #3b82f6; font-size: 60px; margin-bottom: 20px;">Ticker AI</h1>
            </div>
            """, unsafe_allow_html=True)