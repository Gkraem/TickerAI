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
    # Defense and Aerospace companies
    {"ticker": "NOC", "name": "Northrop Grumman Corporation"},
    {"ticker": "GD", "name": "General Dynamics Corporation"},
    {"ticker": "HII", "name": "Huntington Ingalls Industries Inc."},
    {"ticker": "TDG", "name": "TransDigm Group Inc."},
    {"ticker": "TXT", "name": "Textron Inc."},
    {"ticker": "SPR", "name": "Spirit AeroSystems Holdings Inc."},
    # Tech companies
    {"ticker": "ORCL", "name": "Oracle Corporation"},
    {"ticker": "CRM", "name": "Salesforce Inc."},
    {"ticker": "SAP", "name": "SAP SE"},
    {"ticker": "IBM", "name": "International Business Machines Corp."},
    {"ticker": "NOW", "name": "ServiceNow Inc."},
    {"ticker": "TEAM", "name": "Atlassian Corporation"},
    {"ticker": "WDAY", "name": "Workday Inc."},
    {"ticker": "ZS", "name": "Zscaler Inc."},
    {"ticker": "OKTA", "name": "Okta Inc."},
    {"ticker": "NET", "name": "Cloudflare Inc."},
    {"ticker": "CRWD", "name": "CrowdStrike Holdings Inc."},
    {"ticker": "SNOW", "name": "Snowflake Inc."},
    {"ticker": "DDOG", "name": "Datadog Inc."},
    {"ticker": "TWLO", "name": "Twilio Inc."},
    {"ticker": "MDB", "name": "MongoDB Inc."},
    # Energy sector
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
    {"ticker": "COP", "name": "ConocoPhillips"},
    {"ticker": "SLB", "name": "Schlumberger Limited"},
    {"ticker": "EOG", "name": "EOG Resources Inc."},
    {"ticker": "OXY", "name": "Occidental Petroleum Corporation"},
    {"ticker": "HAL", "name": "Halliburton Company"},
    {"ticker": "MPC", "name": "Marathon Petroleum Corporation"},
    {"ticker": "PSX", "name": "Phillips 66"},
    {"ticker": "VLO", "name": "Valero Energy Corporation"},
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
    
    # If not enough local matches, try a more direct approach for specific companies
    if query_lower in ["northrop", "grumman", "northrop grumman"]:
        # Ensure Northrop Grumman is in results
        if not any(stock['ticker'] == "NOC" for stock in local_matches):
            local_matches.append({
                "ticker": "NOC",
                "name": "Northrop Grumman Corporation"
            })
    
    # Try common variations and abbreviations
    ticker_mappings = {
        "citi": "C",
        "citigroup": "C",
        "coke": "KO",
        "coca cola": "KO",
        "cocacola": "KO",
        "coca-cola": "KO",
        "boeing": "BA",
        "lockheed": "LMT",
        "raytheon": "RTX",
        "defense": ["NOC", "LMT", "GD", "RTX", "HII"],  # Defense contractors
        "airlines": ["AAL", "DAL", "UAL", "LUV"],  # Major airlines
        "tech": ["AAPL", "MSFT", "GOOGL", "META", "AMZN", "NVDA"],  # Big tech
        "semiconductors": ["NVDA", "AMD", "INTC", "MU", "TSM", "AVGO"],  # Semiconductor companies
        "banks": ["JPM", "BAC", "WFC", "C", "GS", "MS"],  # Major banks
        "energy": ["XOM", "CVX", "COP", "SLB", "BP", "OXY"],  # Energy companies
        "retail": ["WMT", "TGT", "COST", "AMZN", "HD", "LOW"],  # Retail companies
    }
    
    for key, value in ticker_mappings.items():
        if query_lower in key or key in query_lower:
            if isinstance(value, list):
                # Add all related companies for category searches
                for ticker in value:
                    # Find the company name in our database
                    for stock in POPULAR_STOCKS:
                        if stock["ticker"] == ticker and not any(m["ticker"] == ticker for m in local_matches):
                            local_matches.append(stock)
                            break
            else:
                # Add the specific company
                for stock in POPULAR_STOCKS:
                    if stock["ticker"] == value and not any(m["ticker"] == value for m in local_matches):
                        local_matches.append(stock)
                        break
    
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

# Set page configuration for single page layout
st.set_page_config(
    page_title="Ticker AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load and apply custom CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

load_css("assets/custom.css")

# Convert image to base64 for inline CSS
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Initialize view mode state if not exists
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"

def main():
    # Check if user is authenticated
    if not is_authenticated():
        auth_page()
        return
    
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
        # === MAIN SINGLE PAGE LAYOUT ===
        
        # Get base64 encoded background image
        bg_image = get_base64_image("assets/ticker.jpg")
        
        # Create navigation header
        st.markdown(f"""
        <style>
        .main-nav {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background-color: rgba(17, 24, 39, 0.95);
            backdrop-filter: blur(10px);
            padding: 5px 0;
            border-bottom: 1px solid rgba(59, 130, 246, 0.3);
        }}
        .nav-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 40px;
            width: 100%;
        }}
        .nav-logo {{
            margin: 0;
            color: #3b82f6;
            font-size: 24px;
            font-weight: bold;
            margin-left: -20px;
        }}
        .nav-menu {{
            display: flex;
            gap: 30px;
            margin-right: -20px;
        }}
        .nav-menu a {{
            color: #e5e7eb;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
            transition: color 0.3s;
        }}
        .nav-menu a:hover {{
            color: #3b82f6;
        }}
        .nav-toggle {{
            display: none;
            background: none;
            border: none;
            color: #e5e7eb;
            font-size: 20px;
            cursor: pointer;
            position: relative;
        }}
        .nav-dropdown {{
            display: none;
            position: absolute;
            top: 100%;
            right: 0;
            background-color: rgba(17, 24, 39, 0.95);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 8px;
            padding: 10px 0;
            min-width: 150px;
            z-index: 1001;
        }}
        .nav-dropdown a {{
            display: block;
            padding: 10px 20px;
            color: #e5e7eb;
            text-decoration: none;
            font-size: 14px;
            transition: background-color 0.3s;
        }}
        .nav-dropdown a:hover {{
            background-color: rgba(59, 130, 246, 0.2);
        }}
        @media (max-width: 768px) {{
            .nav-menu {{
                display: none;
            }}
            .nav-toggle {{
                display: block;
            }}
            .nav-toggle:hover + .nav-dropdown,
            .nav-dropdown:hover {{
                display: block;
            }}
        }}
        .hero-section {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('data:image/jpeg;base64,{bg_image}') center/cover;
            height: 100vh;
            width: 100vw;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            margin: 0 calc(-50vw + 50%);
            padding: 0 2rem;
            position: relative;
        }}
        .hero-title {{
            font-size: 4rem;
            font-weight: bold;
            color: white;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }}
        .hero-subtitle {{
            font-size: 1.5rem;
            color: #e5e7eb;
            max-width: 600px;
            margin-bottom: 2rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        }}
        .hero-button {{
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white !important;
            padding: 15px 30px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: all 0.3s;
            display: inline-block;
        }}
        .hero-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
            color: white !important;
        }}
        .section-spacer {{
            height: 60px;
        }}
        .section-header {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #3b82f6;
            margin: 40px 0 30px 0;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(59, 130, 246, 0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .section-emoji {{
            font-size: 2rem;
            margin-left: 15px;
        }}
        .footer {{
            background-color: rgba(17, 24, 39, 0.95);
            border-top: 1px solid rgba(59, 130, 246, 0.3);
            padding: 20px 0;
            margin-top: 50px;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
        }}
        .footer-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 40px;
            flex-wrap: wrap;
            width: 100%;
        }}
        .footer-logo {{
            color: #3b82f6;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .footer-info {{
            color: #e5e7eb;
            font-size: 14px;
        }}
        @media (max-width: 768px) {{
            .footer-content {{
                flex-direction: column;
                text-align: center;
            }}
            .hero-title {{
                font-size: 2.5rem;
            }}
            .hero-subtitle {{
                font-size: 1.2rem;
            }}
        }}
        </style>
        
        <div class="main-nav">
            <div class="nav-content">
                <h1 class="nav-logo">Ticker AI</h1>
                <nav class="nav-menu">
                    <a href="#howitworks">How It Works</a>
                    <a href="#analyzer">Stock Analyzer</a>
                    <a href="#powerplays">Power Plays</a>
                </nav>
                <div style="position: relative;">
                    <button class="nav-toggle">☰</button>
                    <div class="nav-dropdown">
                        <a href="#howitworks">How It Works</a>
                        <a href="#analyzer">Stock Analyzer</a>
                        <a href="#powerplays">Power Plays</a>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add top spacing to account for fixed header
        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
        
        # Hero Section with background image
        st.markdown("""
        <div id="home" class="hero-section">
            <h1 class="hero-title">TICKER AI</h1>
            <p class="hero-subtitle">
                Transform complex financial data into actionable insights with AI-powered stock analysis
            </p>
            <a href="#analyzer" class="hero-button">
                Start Analyzing →
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # How It Works Section
        st.markdown('<div id="howitworks" class="section-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">How It Works<span class="section-emoji">🔍</span></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            ### 1. Search & Select
            Simply type any company name or ticker symbol to find and select the stock you want to analyze.
            """)
        
        with col2:
            st.markdown("""
            ### 2. AI Analysis
            Our advanced AI algorithms analyze technical indicators, fundamental data, and market sentiment.
            """)
        
        with col3:
            st.markdown("""
            ### 3. Actionable Insights
            Get a comprehensive buy/sell rating with detailed explanations and investment recommendations.
            """)
        
        # Stock Analyzer Section
        st.markdown('<div id="analyzer" class="section-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Stock Analyzer<span class="section-emoji">📊</span></div>', unsafe_allow_html=True)
        
        # Initialize session states for stock search
        if "search_query" not in st.session_state:
            st.session_state.search_query = ""
        if "selected_ticker" not in st.session_state:
            st.session_state.selected_ticker = ""
        
        # Stock search interface
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            # Generate all stock options for the dropdown
            all_options = []
            for stock in POPULAR_STOCKS:
                all_options.append(f"{stock['ticker']} - {stock['name']}")
            
            # Function to update stock search results
            def update_stock_results():
                if not st.session_state.stock_search or st.session_state.stock_search == "":
                    st.session_state.selected_ticker = ""
                    return
                if " - " in st.session_state.stock_search:
                    ticker_part = st.session_state.stock_search.split(" - ")[0]
                    st.session_state.selected_ticker = ticker_part
            
            # Single combined dropdown
            selected_option = st.selectbox(
                "Search stocks by typing",
                options=[""] + all_options,
                index=0,
                key="stock_search",
                on_change=update_stock_results
            )
            
            # Extract ticker from selection if available
            ticker = ""
            if selected_option and " - " in selected_option:
                ticker = selected_option.split(" - ")[0]
                st.session_state.selected_ticker = ticker
        
        with col2:
            # Timeframe selector
            timeframe = st.selectbox(
                "Select Timeframe",
                ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                index=5  # Default to 1 year
            )
        
        with col3:
            # Search button
            search_button = st.button("Analyze Stock", type="primary")
        
        # Display selected ticker
        if "selected_ticker" in st.session_state and st.session_state.selected_ticker:
            ticker = st.session_state.selected_ticker
            st.success(f"Selected: **{ticker}**")
        
        # Stock analysis display
        if search_button and ticker:
            try:
                analyzer = StockAnalyzer(ticker)
                
                # Get company info
                company_info = analyzer.get_company_info()
                
                # Display company name prominently
                if company_info and 'longName' in company_info:
                    st.markdown(f'<div class="company-name">{company_info["longName"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="company-name">{ticker}</div>', unsafe_allow_html=True)
                
                # Calculate buy rating
                buy_rating, rating_breakdown = analyzer.calculate_buy_rating()
                
                # Display the rating prominently
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col2:
                    # Determine color and recommendation based on rating
                    if buy_rating >= 7:
                        color = "#10B981"  # Green
                        recommendation = "BUY"
                        border_color = "#10B981"
                    elif buy_rating >= 4:
                        color = "#F59E0B"  # Orange
                        recommendation = "HOLD"
                        border_color = "#F59E0B"
                    else:
                        color = "#EF4444"  # Red
                        recommendation = "SELL"
                        border_color = "#EF4444"
                    
                    # Create a beautiful rating display
                    rating_html = f"""
                    <div style="display: flex; justify-content: center; margin: 30px 0;">
                        <div style="display: flex; flex-direction: column; align-items: center; 
                                   background-color: rgba(17, 24, 39, 0.7); border-radius: 12px; 
                                   padding: 25px 30px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); 
                                   border: 3px solid {border_color}; width: 180px;">
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
                                {recommendation}
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(rating_html, unsafe_allow_html=True)
                
                # Basic stock info
                current_price = analyzer.get_current_price()
                price_change = analyzer.get_price_change()
                market_cap = analyzer.get_market_cap()
                pe_ratio = analyzer.get_pe_ratio()
                
                # Display key metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if current_price:
                        st.metric("Current Price", f"${current_price:.2f}")
                
                with col2:
                    if price_change:
                        change_value = price_change.get('change', 0)
                        change_percent = price_change.get('changePercent', 0)
                        delta_color = "normal" if change_value >= 0 else "inverse"
                        st.metric("Daily Change", f"${change_value:.2f}", f"{change_percent:.2f}%", delta_color=delta_color)
                
                with col3:
                    if market_cap:
                        st.metric("Market Cap", format_large_number(market_cap))
                
                with col4:
                    if pe_ratio:
                        st.metric("P/E Ratio", f"{pe_ratio:.2f}")
            
            except Exception as e:
                st.error(f"Error analyzing {ticker}: {str(e)}")
                st.info("Please check if the ticker symbol is correct and try again.")
        
        elif search_button and not ticker:
            st.warning("Please select a stock from the dropdown before analyzing.")
        
        # Power Plays Section
        st.markdown('<div id="powerplays" class="section-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Power Plays<span class="section-emoji">🚀</span></div>', unsafe_allow_html=True)
        display_power_plays()
        
        # Data Sources section
        st.markdown('<div class="section-header">Data Sources<span class="section-emoji">📊</span></div>', unsafe_allow_html=True)
        st.markdown("All our financial data comes from trusted, professional sources:")
        st.markdown("• **[Yahoo Finance](https://finance.yahoo.com/)** - Real-time stock prices, historical data, and company information")
        st.markdown("• **[yfinance Python Library](https://pypi.org/project/yfinance/)** - Yahoo Finance API wrapper for data retrieval")
        st.markdown("• **[Plotly](https://plotly.com/)** - Interactive charting and data visualization")
        st.markdown("• **[Technical Analysis Algorithms](https://ta-lib.org/)** - RSI, MACD, Bollinger Bands, and moving averages")
        st.markdown("• **[Financial Statement APIs](https://sec.gov/)** - Income statements, balance sheets, and cash flow data")
        st.markdown("• **[Market News Aggregators](https://newsapi.org/)** - Recent news articles and market sentiment analysis")
        
        # Logout button
        logout_button()
        
        # Footer Section (Contact Us)
        st.markdown("""
        <div class="footer">
            <div class="footer-content">
                <div>
                    <div class="footer-logo">Ticker AI</div>
                    <div class="footer-info">AI-powered stock analysis and investment insights</div>
                </div>
                <div class="footer-info">
                    <div><strong>Contact Us:</strong></div>
                    <div>Email: gkraem@vt.edu</div>
                    <div>Phone: 240-285-7119</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()