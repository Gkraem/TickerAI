import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import base64
import os
import time
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

# Configure page
st.set_page_config(
    page_title="Ticker AI - Investment Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Comprehensive stock database with major companies from all indices
POPULAR_STOCKS = [
    # Mega Cap Tech
    {"ticker": "AAPL", "name": "Apple Inc."},
    {"ticker": "MSFT", "name": "Microsoft Corporation"},
    {"ticker": "AMZN", "name": "Amazon.com Inc."},
    {"ticker": "GOOGL", "name": "Alphabet Inc. (Google Class A)"},
    {"ticker": "GOOG", "name": "Alphabet Inc. (Google Class C)"},
    {"ticker": "META", "name": "Meta Platforms Inc."},
    {"ticker": "TSLA", "name": "Tesla Inc."},
    {"ticker": "NVDA", "name": "NVIDIA Corporation"},
    {"ticker": "NFLX", "name": "Netflix Inc."},
    {"ticker": "ADBE", "name": "Adobe Inc."},
    {"ticker": "CRM", "name": "Salesforce Inc."},
    {"ticker": "ORCL", "name": "Oracle Corporation"},
    {"ticker": "INTC", "name": "Intel Corporation"},
    {"ticker": "AMD", "name": "Advanced Micro Devices Inc."},
    {"ticker": "QCOM", "name": "Qualcomm Inc."},
    {"ticker": "CSCO", "name": "Cisco Systems Inc."},
    {"ticker": "AVGO", "name": "Broadcom Inc."},
    {"ticker": "TXN", "name": "Texas Instruments Inc."},
    {"ticker": "INTU", "name": "Intuit Inc."},
    {"ticker": "NOW", "name": "ServiceNow Inc."},
    
    # Industrials Sector (including RSG)
    {"ticker": "RSG", "name": "Republic Services Inc."},
    {"ticker": "WM", "name": "Waste Management Inc."},
    {"ticker": "WCN", "name": "Waste Connections Inc."},
    {"ticker": "ROP", "name": "Roper Technologies Inc."},
    {"ticker": "ITW", "name": "Illinois Tool Works Inc."},
    {"ticker": "DHI", "name": "D.R. Horton Inc."},
    {"ticker": "LEN", "name": "Lennar Corporation"},
    {"ticker": "PHM", "name": "PulteGroup Inc."},
    {"ticker": "NVR", "name": "NVR Inc."},
    {"ticker": "TOL", "name": "Toll Brothers Inc."},
    {"ticker": "BLD", "name": "TopBuild Corp."},
    {"ticker": "PWR", "name": "Quanta Services Inc."},
    {"ticker": "EME", "name": "EMCOR Group Inc."},
    {"ticker": "MLM", "name": "Martin Marietta Materials Inc."},
    {"ticker": "VMC", "name": "Vulcan Materials Company"},
    
    # Financial Services
    {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
    {"ticker": "BAC", "name": "Bank of America Corp."},
    {"ticker": "WFC", "name": "Wells Fargo & Company"},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc."},
    {"ticker": "MS", "name": "Morgan Stanley"},
    {"ticker": "C", "name": "Citigroup Inc."},
    {"ticker": "BLK", "name": "BlackRock Inc."},
    {"ticker": "SCHW", "name": "Charles Schwab Corporation"},
    {"ticker": "AXP", "name": "American Express Company"},
    {"ticker": "V", "name": "Visa Inc."},
    {"ticker": "MA", "name": "Mastercard Incorporated"},
    
    # Healthcare & Pharmaceuticals
    {"ticker": "JNJ", "name": "Johnson & Johnson"},
    {"ticker": "PFE", "name": "Pfizer Inc."},
    {"ticker": "UNH", "name": "UnitedHealth Group Inc."},
    {"ticker": "CVS", "name": "CVS Health Corporation"},
    {"ticker": "ABBV", "name": "AbbVie Inc."},
    {"ticker": "BMY", "name": "Bristol-Myers Squibb Company"},
    {"ticker": "MRK", "name": "Merck & Co. Inc."},
    {"ticker": "LLY", "name": "Eli Lilly and Company"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific Inc."},
    {"ticker": "ABT", "name": "Abbott Laboratories"},
    
    # Energy & Utilities
    {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "COP", "name": "ConocoPhillips"},
    {"ticker": "EOG", "name": "EOG Resources Inc."},
    {"ticker": "SLB", "name": "Schlumberger Limited"},
    {"ticker": "HAL", "name": "Halliburton Company"},
    {"ticker": "BKR", "name": "Baker Hughes Company"},
    {"ticker": "VLO", "name": "Valero Energy Corporation"},
    {"ticker": "PSX", "name": "Phillips 66"},
    {"ticker": "MPC", "name": "Marathon Petroleum Corporation"},
    
    # Consumer Goods & Retail
    {"ticker": "PG", "name": "Procter & Gamble Company"},
    {"ticker": "KO", "name": "Coca-Cola Company"},
    {"ticker": "PEP", "name": "PepsiCo Inc."},
    {"ticker": "WMT", "name": "Walmart Inc."},
    {"ticker": "TGT", "name": "Target Corporation"},
    {"ticker": "COST", "name": "Costco Wholesale Corporation"},
    {"ticker": "HD", "name": "Home Depot Inc."},
    {"ticker": "LOW", "name": "Lowe's Companies Inc."},
]

def apply_modern_css():
    """Apply modern CSS styling"""
    st.markdown("""
    <style>
    /* Hide Streamlit elements */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    button[data-testid="collapsedControl"] { display: none !important; }
    
    /* Custom color scheme */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #10b981;
        --accent: #f59e0b;
        --background: #f8fafc;
        --surface: #ffffff;
        --text: #1e293b;
        --text-light: #64748b;
        --border: #e2e8f0;
        --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* Main layout */
    .stApp {
        background: var(--background);
        color: var(--text);
    }
    
    /* Navigation header */
    .nav-header {
        background: var(--surface);
        padding: 1rem 2rem;
        border-bottom: 1px solid var(--border);
        box-shadow: var(--shadow);
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-logo {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--primary);
    }
    
    .nav-menu {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-link {
        color: var(--text-light);
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.2s;
    }
    
    .nav-link:hover {
        color: var(--primary);
        background: #f1f5f9;
    }
    
    /* Content sections */
    .section {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .section-title {
        font-size: 2rem;
        font-weight: bold;
        color: var(--text);
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .section-subtitle {
        color: var(--text-light);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Cards */
    .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
        padding: 2rem;
        box-shadow: var(--shadow);
        margin-bottom: 2rem;
    }
    
    /* Buy rating */
    .rating-display {
        text-align: center;
        margin: 2rem 0;
        padding: 2rem;
        background: var(--surface);
        border: 3px solid var(--primary);
        border-radius: 1rem;
        box-shadow: var(--shadow);
    }
    
    .rating-score {
        font-size: 3rem;
        font-weight: bold;
        color: var(--primary);
        margin-bottom: 0.5rem;
    }
    
    .rating-text {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text);
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .nav-header {
            padding: 1rem;
            flex-direction: column;
            gap: 1rem;
        }
        
        .section {
            padding: 1rem;
        }
        
        .section-title {
            font-size: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session states
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"

def search_stocks(query):
    """Search for stocks by partial ticker or company name match"""
    if not query:
        return []
    
    query_upper = query.upper()
    query_lower = query.lower()
    local_matches = []
    
    for stock in POPULAR_STOCKS:
        if stock["ticker"] == query_upper or stock["ticker"].startswith(query_upper):
            local_matches.append(stock)
        elif query_lower in stock["name"].lower():
            local_matches.append(stock)
    
    # Sort matches: exact ticker matches first
    local_matches.sort(key=lambda x: (
        0 if x["ticker"] == query_upper else 
        1 if x["ticker"].startswith(query_upper) else 
        2
    ))
    
    return local_matches[:10]

def main():
    # Apply modern CSS
    apply_modern_css()
    
    # Check if user is authenticated
    if not is_authenticated():
        auth_page()
        return
    
    # Navigation
    st.markdown("""
    <div class="nav-header">
        <div class="nav-logo">📊 TICKER AI</div>
        <div class="nav-menu">
            <a href="#analyzer" class="nav-link">Stock Analyzer</a>
            <a href="#powerplays" class="nav-link">Power Plays</a>
            <a href="#about" class="nav-link">About</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check view mode
    if st.session_state.view_mode == "admin" and is_admin():
        # Admin Panel
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<h1 class="section-title">Admin Panel</h1>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">User Management & System Controls</p>', unsafe_allow_html=True)
        
        user = get_session_user()
        if user and isinstance(user, dict):
            st.markdown(f"**Logged in as:** {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        admin_panel()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # About Section
        st.markdown('<div class="section" id="about">', unsafe_allow_html=True)
        st.markdown('<h1 class="section-title">About Ticker AI</h1>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Advanced AI-powered investment platform</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        A powerful stock analysis platform that combines real-time data with advanced AI to help you make smarter investment decisions. It analyzes price trends, technical indicators, and historical patterns to predict market movements with precision. Ticker AI also monitors breaking news and social media to gauge sentiment shifts, while factoring in key financial metrics like earnings growth, valuations, and insider activity.
        
        Ticker AI's buy rating engine is powered by a weighted algorithm that evaluates each stock through a multi-layered scoring system. The model assigns 40% weight to technical indicators—such as RSI, MACD, moving averages, and Bollinger Bands—calculating bullish momentum based on the ratio of confirming signals. Another 40% is dedicated to fundamental analysis, where key financial metrics like P/E ratio, profit margins, revenue growth, and debt-to-equity are benchmarked and scored relative to industry norms. The remaining 20% draws on market sentiment, translating analyst recommendations into a normalized confidence score.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Stock Analyzer Section
        st.markdown('<div class="section" id="analyzer">', unsafe_allow_html=True)
        st.markdown('<h1 class="section-title">Stock Analyzer 📊</h1>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Analyze individual stocks with AI-powered insights</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Initialize session states for stock search
        if "search_query" not in st.session_state:
            st.session_state.search_query = ""
        if "selected_ticker" not in st.session_state:
            st.session_state.selected_ticker = ""
        
        # Stock search interface
        col1, col2 = st.columns([3, 1.5])
        
        with col1:
            search_input = st.text_input(
                "Search stocks by ticker or company name",
                placeholder="Type ticker (e.g., AAPL) or company name...",
                key="stock_search_input"
            )
            
            # Show matching stocks if search input exists
            if search_input and len(search_input) >= 1:
                matching_stocks = search_stocks(search_input)
                
                if matching_stocks:
                    st.write("**Select a stock:**")
                    for i, stock in enumerate(matching_stocks[:3]):  # Show only 3 results
                        if st.button(f"{stock['ticker']} - {stock['name']}", key=f"stock_btn_{i}"):
                            st.session_state.selected_ticker = stock['ticker']
                            st.session_state.selected_stock_name = stock['name']
                            st.rerun()
        
        with col2:
            search_button = st.button("Analyze Stock", type="primary", disabled=not st.session_state.get('selected_ticker'))
        
        # Stock analysis display
        if search_button and st.session_state.get('selected_ticker'):
            ticker = st.session_state.selected_ticker
            
            try:
                # Initialize analyzer
                analyzer = StockAnalyzer(ticker)
                
                # Get basic stock info
                stock = yf.Ticker(ticker)
                company_info = stock.info
                current_price = company_info.get('currentPrice', company_info.get('regularMarketPrice', 0))
                market_cap = company_info.get('marketCap', 0)
                pe_ratio = company_info.get('trailingPE', 0)
                
                # Calculate buy rating
                buy_rating, rating_breakdown = analyzer.calculate_buy_rating()
                
                # Display buy rating
                if buy_rating >= 7:
                    recommendation = "STRONG BUY"
                    rating_color = "#10b981"
                elif buy_rating >= 5:
                    recommendation = "BUY"
                    rating_color = "#6366f1"
                elif buy_rating >= 3:
                    recommendation = "HOLD"
                    rating_color = "#f59e0b"
                else:
                    recommendation = "SELL"
                    rating_color = "#ef4444"
                
                st.markdown(f"""
                <div class="rating-display" style="border-color: {rating_color};">
                    <div style="font-size: 0.875rem; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">BUY RATING</div>
                    <div style="font-size: 3rem; font-weight: bold; color: {rating_color}; margin-bottom: 0.5rem;">{buy_rating:.1f}</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: var(--text);">{recommendation}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Key Financials
                st.markdown("### 💰 Key Financials")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Price", f"${current_price:.2f}" if current_price else "N/A")
                    st.metric("Market Cap", format_large_number(market_cap) if market_cap else "N/A")
                
                with col2:
                    st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
                    profit_margin = company_info.get('profitMargins', 0)
                    st.metric("Profit Margin", f"{profit_margin*100:.2f}%" if profit_margin else "N/A")
                
                with col3:
                    dividend_yield = company_info.get('dividendYield', 0)
                    st.metric("Dividend Yield", f"{dividend_yield*100:.2f}%" if dividend_yield else "N/A")
                    total_revenue = company_info.get('totalRevenue', 0)
                    st.metric("Revenue", format_large_number(total_revenue) if total_revenue else "N/A")
                
                # Technical Analysis
                st.markdown("### 📈 Technical Analysis")
                technical = TechnicalAnalysis(ticker)
                signals = technical.get_technical_signals()
                
                if signals:
                    for signal_name, signal_data in signals.items():
                        if isinstance(signal_data, dict) and 'signal' in signal_data:
                            st.write(f"**{signal_name}:** {signal_data['signal']}")
                
                # AI Analysis Summary
                st.markdown("### 🤖 AI Analysis Summary")
                
                company_name = company_info.get('longName', ticker)
                sector = company_info.get('sector', 'Unknown')
                
                # Create size category
                if market_cap > 200_000_000_000:
                    size_category = "mega-cap"
                elif market_cap > 50_000_000_000:
                    size_category = "large-cap"
                elif market_cap > 10_000_000_000:
                    size_category = "mid-cap"
                else:
                    size_category = "small-cap"
                
                # Generate summary
                if buy_rating >= 7:
                    recommendation_text = "presents a compelling investment opportunity"
                elif buy_rating >= 4:
                    recommendation_text = "warrants careful consideration with mixed signals"
                else:
                    recommendation_text = "faces significant headwinds and risks"
                
                st.markdown(f"""
                **BUY RATING: {buy_rating:.1f}/10**
                
                {company_name} is a {size_category} {sector.lower()} company that {recommendation_text}. Our analysis indicates {rating_breakdown.get('Technical Analysis', {}).get('reason', 'mixed technical signals').lower()}, while the company's fundamentals show {rating_breakdown.get('Fundamental Analysis', {}).get('reason', 'average financial health').lower()}. Market sentiment suggests {rating_breakdown.get('Market Sentiment', {}).get('reason', 'neutral investor confidence').lower()}, which combined with the technical and fundamental picture supports our {buy_rating:.1f}/10 rating.
                """)
                
            except Exception as e:
                st.error(f"Error analyzing stock: {str(e)}")
                st.info("Please try again with a different stock symbol or check if the ticker is valid.")
            
            # Reset search button
            if st.button("Reset Search", key="reset_stock_search"):
                if "selected_ticker" in st.session_state:
                    del st.session_state.selected_ticker
                if "stock_search" in st.session_state:
                    del st.session_state.stock_search
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Power Plays Section
        st.markdown('<div class="section" id="powerplays">', unsafe_allow_html=True)
        st.markdown('<h1 class="section-title">Power Plays 🚀</h1>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Top investment opportunities from major indices</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        display_power_plays()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data Sources section
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<h1 class="section-title">Data Sources 📊</h1>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Trusted financial data providers</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("All our financial data comes from trusted, professional sources: **[Yahoo Finance](https://finance.yahoo.com/)**, **[Bloomberg](https://www.bloomberg.com/)**, **[MarketWatch](https://www.marketwatch.com/)**, **[CNBC](https://www.cnbc.com/)**, **[SEC EDGAR Database](https://sec.gov/)**, and **[Morningstar](https://www.morningstar.com/)**.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Logout button
        logout_button()

if __name__ == "__main__":
    main()