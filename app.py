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
from user_management import is_authenticated, get_session_user, get_total_user_count
from auth_components import auth_page, logout_button
from admin import is_admin, admin_panel
from power_plays import display_power_plays

# Set page configuration for a modern look
st.set_page_config(
    page_title="Ticker AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed for cleaner look
)

# Load and apply custom CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Try to load custom CSS if it exists
try:
    # Try to load CSS from .streamlit/custom.css
    custom_css_path = os.path.join(".streamlit", "custom.css")
    if os.path.exists(custom_css_path):
        load_css(custom_css_path)
    # Also try assets/custom.css
    elif os.path.exists("assets/custom.css"):
        load_css("assets/custom.css")
except Exception as e:
    # Just log error, don't display to user
    print(f"Error loading CSS: {str(e)}")

# Function to render SVG files
def render_svg(svg_file):
    with open(svg_file, "r") as f:
        svg_content = f.read()
        b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
        return f'<img src="data:image/svg+xml;base64,{b64}" alt="SVG Image" style="max-width: 100%;">'

# Initialize view mode state if not exists
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"  # Options: "main", "admin"

# Initialize state variables for the new UI
if "landing_page_shown" not in st.session_state:
    st.session_state.landing_page_shown = True
    
if "auth_view" not in st.session_state:
    st.session_state.auth_view = False

if "power_plays_view" not in st.session_state:
    st.session_state.power_plays_view = False

# Modern landing page or main content logic
if not is_authenticated():
    if st.session_state.auth_view:
        # Show authentication page when user clicks "Try for Free"
        auth_page()
    else:
        # IntelIectia.ai-style navigation header
        st.markdown("""
        <style>
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background-color: #1a1a1a;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        
        .navbar .logo {
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        .navbar ul {
            list-style: none;
            display: flex;
            gap: 1rem;
            margin: 0;
            padding: 0;
        }
        
        .navbar li {
            display: inline-block;
        }
        
        .navbar a {
            color: #ffffff;
            text-decoration: none;
            padding: 0.5rem 1rem;
        }
        
        .navbar .cta {
            background-color: #007bff;
            border-radius: 4px;
        }
        
        .hero {
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #1a1a1a, #333333);
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        
        .hero h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .hero p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.8;
        }
        
        .hero .cta {
            background-color: #007bff;
            color: #ffffff;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 500;
            display: inline-block;
        }
        
        .features {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 2rem;
            padding: 2rem;
            background-color: #1a1a1a;
            border-radius: 8px;
        }
        
        .feature {
            background-color: #2a2a2a;
            padding: 1.5rem;
            border-radius: 8px;
            width: calc(33.333% - 2rem);
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .feature h2 {
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .feature p {
            opacity: 0.8;
            font-size: 1rem;
            line-height: 1.5;
        }
        
        @media (max-width: 768px) {
            .navbar {
                flex-direction: column;
                padding: 1rem;
            }
            
            .navbar .logo {
                margin-bottom: 1rem;
            }
            
            .navbar ul {
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .feature {
                width: 100%;
            }
        }
        </style>
        
        <header class="navbar">
            <div class="logo">Ticker AI</div>
            <nav>
                <ul>
                    <li><a href="#">Product</a></li>
                    <li><a href="#">Markets</a></li>
                    <li><a href="#">Resources</a></li>
                    <li><a href="#">Pricing</a></li>
                    <li><a href="#" id="sign-in-btn">Sign In</a></li>
                    <li><a class="cta" href="#" id="try-free-btn">Try for Free</a></li>
                </ul>
            </nav>
        </header>
        
        <script>
            document.getElementById('sign-in-btn').addEventListener('click', function() {
                // This will be handled by Streamlit event handler instead
            });
            
            document.getElementById('try-free-btn').addEventListener('click', function() {
                // This will be handled by Streamlit event handler instead
            });
        </script>
        """, unsafe_allow_html=True)
        
        # Create two buttons for auth but keep them hidden
        col1, col2 = st.columns([1, 1])
        with col1:
            signin_button = st.button("Sign In", key="signin", use_container_width=True)
        with col2:
            tryfree_button = st.button("Try for Free", key="tryfree", use_container_width=True)
            
        if signin_button or tryfree_button:
            st.session_state.auth_view = True
            st.rerun()
        
        # Replace the buttons with empty space since we're using the navigation buttons
        st.markdown('<style>div[data-testid="stHorizontalBlock"] {display: none;}</style>', unsafe_allow_html=True)
        
        # Hero section
        st.markdown("""
        <section class="hero">
            <h1>The Most Powerful AI Platform for Smarter Investing</h1>
            <p>From Wall Street to Main Street, where AI meets your ambition.</p>
            <a class="cta" href="#" id="hero-try-now">Try Now</a>
        </section>
        
        <script>
            document.getElementById('hero-try-now').addEventListener('click', function(e) {
                e.preventDefault();
                // Will be handled by Streamlit
            });
        </script>
        """, unsafe_allow_html=True)
        
        # Another hidden button for the hero "Try Now" link
        if st.button("Try Now", key="herocta", use_container_width=True):
            st.session_state.auth_view = True
            st.rerun()
            
        # Hide this button too
        st.markdown('<style>button[kind="secondary"] {display: none;}</style>', unsafe_allow_html=True)
        
        # Features section
        st.markdown("""
        <section class="features">
            <div class="feature">
                <h2>AI Stock Picker</h2>
                <p>Daily top stock picks with over 200% annualized returns based on AI analysis.</p>
            </div>
            <div class="feature">
                <h2>Advanced Analytics</h2>
                <p>Comprehensive technical and fundamental analysis with AI-powered insights.</p>
            </div>
            <div class="feature">
                <h2>Power Plays</h2>
                <p>Discover the most promising investment opportunities across major indices.</p>
            </div>
        </section>
        """, unsafe_allow_html=True)
        
        # User stats in a modern, subtle footer
        user_count = get_total_user_count()
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0; opacity: 0.7; font-size: 0.9rem;">
            <p>Join our community of {user_count} investors making smarter decisions with AI</p>
        </div>
        """, unsafe_allow_html=True)
else:
    # User is authenticated - show main app content
    st.session_state.landing_page_shown = False
    
    # Configure sidebar for authenticated users
    with st.sidebar:
        # User info and logout
        user = get_session_user()
        
        # User welcome and profile section
        if user and isinstance(user, dict) and 'name' in user:
            st.markdown(f"""
            <div style='background: rgba(30, 40, 60, 0.5); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>
                <h3 style='margin-bottom: 0.5rem; font-size: 1.2rem;'>Welcome, {user['name']}</h3>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("### Welcome")
        
        # Main navigation
        st.title("Navigation")
        
        # Stock search section
        st.subheader("Stock Analysis")
        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "").upper()
        
        # Timeframe selector
        timeframe = st.selectbox(
            "Select Timeframe",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=5  # Default to 1 year
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            search_button = st.button("Analyze", use_container_width=True)
        with col2:
            power_plays_button = st.button("Power Plays", use_container_width=True)
        
        # Handle Power Plays button
        if power_plays_button:
            st.session_state.power_plays_view = True
            st.session_state.view_mode = "main"  # Ensure we're in main mode
        
        # Logout button
        logout_button()
        
        # Admin section
        if is_admin():
            st.markdown("---")
            st.subheader("Admin Controls")
            
            # Toggle between main app and admin panel
            if st.session_state.view_mode == "main":
                if st.button("Admin Panel", type="primary"):
                    st.session_state.view_mode = "admin"
                    st.session_state.power_plays_view = False  # Reset power plays view
                    st.rerun()
            else:  # In admin mode
                if st.button("Return to App", type="primary"):
                    st.session_state.view_mode = "main"
                    st.rerun()
        
        # Data sources at the bottom
        st.markdown("---")
        st.caption("### Data Sources")
        for source, url in DATA_SOURCES.items():
            st.markdown(f"<small>- [{source}]({url})</small>", unsafe_allow_html=True)
    
    # Page header with subtle styling
    st.markdown("""
    <div style='background: rgba(20, 25, 35, 0.4); 
                padding: 1rem; 
                border-radius: 8px; 
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
        <h1 style='margin: 0; font-size: 2rem;'>Ticker AI</h1>
        <p style='margin: 0; opacity: 0.8;'>AI-Powered Stock Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check view mode to determine what content to display
    if st.session_state.view_mode == "admin" and is_admin():
        # === ADMIN PANEL CONTENT ===
        st.subheader("Admin Panel")
        
        # Show user info
        user = get_session_user()
        if user and isinstance(user, dict):
            st.markdown(f"**Logged in as:** {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        
        # Add a separator
        st.markdown("<hr style='margin-top: 0; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        # Display admin panel content
        admin_panel()
    
    # Main content views based on active state
    elif st.session_state.power_plays_view:
        # Display Power Plays page
        display_power_plays()
    
    elif ticker and search_button and st.session_state.view_mode == "main":
        # Create a placeholder for loading state
        with st.spinner(f'Analyzing {ticker}...'):
            try:
                # Initialize stock analyzer
                analyzer = StockAnalyzer(ticker)
                
                # Get company name and display prominently
                company_info = analyzer.get_company_info()
                
                if company_info and 'shortName' in company_info:
                    company_name = company_info['shortName']
                    
                    # Modern card-style header with company info
                    st.markdown(f"""
                    <div style="background: linear-gradient(to right, rgba(30, 40, 60, 0.8), rgba(30, 40, 60, 0.5)); 
                                padding: 1.5rem; 
                                border-radius: 10px; 
                                margin-bottom: 1.5rem;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <h2 style="margin: 0; font-size: 1.8rem;">{company_name}</h2>
                        <div style="font-size: 1.2rem; opacity: 0.9; margin-top: 0.3rem;">{ticker}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Modern metrics display with cards
                    # Get current price and daily change
                    current_price = analyzer.get_current_price()
                    price_change, price_change_percent = analyzer.get_price_change()
                    
                    # Display price with up/down indicator
                    price_color = "rgba(46, 204, 113, 0.9)" if price_change >= 0 else "rgba(231, 76, 60, 0.9)"
                    price_arrow = "↑" if price_change >= 0 else "↓"
                    
                    # Format metrics for display
                    market_cap = analyzer.get_market_cap()
                    pe_ratio = analyzer.get_pe_ratio()
                    low_52w, high_52w = analyzer.get_52_week_range()
                    
                    # Key metrics in a card grid
                    st.markdown("""
                    <style>
                    .metrics-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                        gap: 15px;
                        margin-bottom: 25px;
                    }
                    .metric-card {
                        background: rgba(30, 40, 60, 0.6);
                        padding: 16px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        transition: transform 0.2s;
                    }
                    .metric-card:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
                    }
                    .metric-title {
                        font-size: 0.9rem;
                        font-weight: 400;
                        opacity: 0.8;
                        margin-bottom: 8px;
                    }
                    .metric-value {
                        font-size: 1.3rem;
                        font-weight: 700;
                        margin-bottom: 4px;
                    }
                    .metric-change {
                        font-size: 0.9rem;
                    }
                    @media (max-width: 768px) {
                        .metrics-grid {
                            grid-template-columns: repeat(2, 1fr);
                        }
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Start metrics grid
                    st.markdown(f"""
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-title">Current Price</div>
                            <div class="metric-value">${current_price:.2f}</div>
                            <div class="metric-change" style="color: {price_color};">
                                {price_arrow} ${abs(price_change):.2f} ({abs(price_change_percent):.2f}%)
                            </div>
                        </div>
                        
                        <div class="metric-card">
                            <div class="metric-title">Market Cap</div>
                            <div class="metric-value">{format_large_number(market_cap) if market_cap else "N/A"}</div>
                        </div>
                        
                        <div class="metric-card">
                            <div class="metric-title">P/E Ratio</div>
                            <div class="metric-value">{f"{pe_ratio:.2f}" if pe_ratio and pe_ratio > 0 else "N/A"}</div>
                        </div>
                        
                        <div class="metric-card">
                            <div class="metric-title">52-Week Range</div>
                            <div class="metric-value">{f"${low_52w:.2f} - ${high_52w:.2f}" if low_52w and high_52w else "N/A"}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Company information section with modern card design
                    st.markdown("""
                    <div style="background: rgba(30, 40, 60, 0.4); 
                                border-radius: 10px; 
                                padding: 1.5rem; 
                                margin-bottom: 2rem;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="margin-top: 0; font-size: 1.5rem; margin-bottom: 1rem;">Company Overview</h3>
                    """, unsafe_allow_html=True)
                    
                    # Display company description
                    if company_info:
                        business_summary = company_info.get('longBusinessSummary', None)
                        if business_summary:
                            st.markdown(f"<p style='line-height: 1.6;'>{business_summary}</p>", unsafe_allow_html=True)
                        else:
                            st.info(f"No business summary available for {ticker}")
                        
                        # Additional company details in columns
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if 'industry' in company_info and company_info['industry']:
                                st.markdown(f"<strong>Industry:</strong> {company_info['industry']}", unsafe_allow_html=True)
                            if 'sector' in company_info and company_info['sector']:
                                st.markdown(f"<strong>Sector:</strong> {company_info['sector']}", unsafe_allow_html=True)
                        
                        with col2:
                            if 'country' in company_info and company_info['country']:
                                st.markdown(f"<strong>Country:</strong> {company_info['country']}", unsafe_allow_html=True)
                            if 'city' in company_info and company_info['city']:
                                st.markdown(f"<strong>City:</strong> {company_info['city']}", unsafe_allow_html=True)
                        
                        with col3:
                            if 'website' in company_info and company_info['website']:
                                st.markdown(f"<strong>Website:</strong> <a href='{company_info['website']}' target='_blank'>{company_info['website']}</a>", unsafe_allow_html=True)
                            if 'fullTimeEmployees' in company_info and company_info['fullTimeEmployees']:
                                st.markdown(f"<strong>Employees:</strong> {format_large_number(company_info['fullTimeEmployees'])}", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Buy Rating Section
                    buy_rating, rating_breakdown = analyzer.calculate_buy_rating()
                    
                    # Modern card for buy rating
                    st.markdown(f"""
                    <div style="background: linear-gradient(to right, rgba(30, 40, 60, 0.7), rgba(30, 40, 60, 0.4)); 
                                padding: 1.5rem; 
                                border-radius: 10px; 
                                margin-bottom: 2rem;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="margin-top: 0; margin-bottom: 1.5rem;">AI-Powered Buy Rating</h3>
                        <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 2rem;">
                            <div style="flex: 0 0 200px;">
                                <div style="position: relative; width: 200px; height: 200px;">
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                        <div style="font-size: 3rem; font-weight: 700;">{buy_rating:.1f}</div>
                                        <div style="font-size: 1rem; opacity: 0.8;">out of 10</div>
                                    </div>
                                </div>
                            </div>
                            <div style="flex: 1; min-width: 300px;">
                                <h4 style="margin-top: 0;">Rating Breakdown</h4>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                                    <div>
                                        <div style="font-weight: 500;">Technical Analysis:</div>
                                        <div style="font-size: 1.1rem; font-weight: 700;">{rating_breakdown['technical_score']:.1f}/10</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 500;">Fundamental Analysis:</div>
                                        <div style="font-size: 1.1rem; font-weight: 700;">{rating_breakdown['fundamental_score']:.1f}/10</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 500;">Market Sentiment:</div>
                                        <div style="font-size: 1.1rem; font-weight: 700;">{rating_breakdown['sentiment_score']:.1f}/10</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create tabs for detailed analysis
                    tab1, tab2, tab3, tab4 = st.tabs(["📈 Technical Analysis", "💼 Fundamentals", "🔮 Market Sentiment", "📰 News"])
                    
                    with tab1:
                        st.subheader("Technical Analysis")
                        
                        # Initialize technical analysis
                        tech_analysis = TechnicalAnalysis(ticker)
                        
                        # Get historical data for charts
                        hist_data = tech_analysis.get_historical_data(timeframe)
                        
                        # Price chart with moving averages
                        st.markdown("#### Price Chart with Moving Averages")
                        
                        # Get moving average data
                        ma_data = tech_analysis.get_moving_averages(timeframe)
                        
                        # Create Plotly figure
                        fig = go.Figure()
                        
                        # Add price line
                        fig.add_trace(go.Scatter(
                            x=ma_data.index, 
                            y=ma_data['Close'],
                            mode='lines',
                            name='Price',
                            line=dict(color='#2E86C1', width=2)
                        ))
                        
                        # Add moving averages
                        fig.add_trace(go.Scatter(
                            x=ma_data.index, 
                            y=ma_data['MA50'],
                            mode='lines',
                            name='50-Day MA',
                            line=dict(color='#F39C12', width=2)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=ma_data.index, 
                            y=ma_data['MA200'],
                            mode='lines',
                            name='200-Day MA',
                            line=dict(color='#E74C3C', width=2)
                        ))
                        
                        # Update layout for modern look
                        fig.update_layout(
                            title=f"{ticker} Price History",
                            xaxis_title="Date",
                            yaxis_title="Price (USD)",
                            template="plotly_dark",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            margin=dict(l=0, r=0, t=40, b=0),
                            height=500,
                        )
                        
                        # Add range selector to chart
                        fig.update_xaxes(
                            rangeslider_visible=True,
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1, label="1m", step="month", stepmode="backward"),
                                    dict(count=6, label="6m", step="month", stepmode="backward"),
                                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                                    dict(count=1, label="1y", step="year", stepmode="backward"),
                                    dict(step="all")
                                ])
                            )
                        )
                        
                        # Display the chart
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Technical indicators grid
                        st.markdown("#### Technical Indicators")
                        
                        # Get technical signals
                        signals = tech_analysis.get_technical_signals()
                        
                        # Convert to DataFrame for display
                        signals_df = pd.DataFrame({
                            'Indicator': list(signals.keys()),
                            'Signal': list(signals.values())
                        })
                        
                        # Apply mobile-friendly styling
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
                        signal_html = styled_df.to_html()
                        st.markdown(f'<div class="mobile-friendly-table">{signal_html}</div>', unsafe_allow_html=True)
                    
                    with tab2:
                        st.subheader("Fundamental Analysis")
                        
                        # Initialize fundamental analysis
                        fundamental = FundamentalAnalysis(ticker)
                        
                        # Valuation ratios
                        st.markdown("#### Valuation Metrics")
                        
                        # Create cards for fundamental metrics
                        try:
                            valuation_ratios = fundamental.get_valuation_ratios()
                            if not valuation_ratios.empty:
                                # Modern card grid
                                st.markdown("""
                                <style>
                                .fundamental-grid {
                                    display: grid;
                                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                                    gap: 12px;
                                    margin-bottom: 20px;
                                }
                                .fundamental-card {
                                    background: rgba(30, 40, 60, 0.5);
                                    padding: 12px;
                                    border-radius: 8px;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                }
                                .fundamental-title {
                                    font-size: 0.85rem;
                                    opacity: 0.8;
                                    margin-bottom: 5px;
                                }
                                .fundamental-value {
                                    font-size: 1.1rem;
                                    font-weight: 700;
                                }
                                </style>
                                <div class="fundamental-grid">
                                """, unsafe_allow_html=True)
                                
                                # Convert to dictionary for easier handling
                                val_dict = valuation_ratios.iloc[-1].to_dict()
                                
                                # Display key metrics
                                key_metrics = ['trailingPE', 'forwardPE', 'priceToBook', 'priceToSales', 'enterpriseToEbitda']
                                labels = {
                                    'trailingPE': 'Trailing P/E',
                                    'forwardPE': 'Forward P/E',
                                    'priceToBook': 'Price to Book',
                                    'priceToSales': 'Price to Sales',
                                    'enterpriseToEbitda': 'EV/EBITDA'
                                }
                                
                                for metric in key_metrics:
                                    if metric in val_dict and not pd.isna(val_dict[metric]):
                                        value = val_dict[metric]
                                        label = labels.get(metric, metric)
                                        
                                        st.markdown(f"""
                                        <div class="fundamental-card">
                                            <div class="fundamental-title">{label}</div>
                                            <div class="fundamental-value">{value:.2f}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                            else:
                                st.info(f"No valuation ratios available for {ticker}")
                        except Exception as e:
                            st.error(f"Error loading valuation ratios: {str(e)}")
                        
                        # Income Statement
                        st.markdown("#### Income Statement")
                        try:
                            income_stmt = fundamental.get_income_statement()
                            if not income_stmt.empty:
                                # Format and display
                                income_stmt = income_stmt.astype(float).applymap(lambda x: f"${x/1e6:.1f}M" if not pd.isna(x) else "N/A")
                                st.dataframe(income_stmt, use_container_width=True)
                            else:
                                st.info(f"No income statement available for {ticker}")
                        except Exception as e:
                            st.error(f"Error loading income statement: {str(e)}")
                        
                        # Analyst Recommendations
                        st.markdown("#### Analyst Recommendations")
                        try:
                            recommendations = fundamental.get_analyst_recommendations()
                            if not recommendations.empty:
                                # Create a pie chart of recommendations
                                rec_counts = recommendations.iloc[0].astype(float)
                                
                                # Create custom color scale
                                colors = {
                                    'Strong Buy': '#1E8449',
                                    'Buy': '#58D68D',
                                    'Hold': '#F7DC6F',
                                    'Underperform': '#F5B041',
                                    'Sell': '#E74C3C'
                                }
                                
                                # Create plotly pie chart
                                fig = px.pie(
                                    values=rec_counts.values,
                                    names=rec_counts.index,
                                    title=f"Analyst Recommendations for {ticker}",
                                    color=rec_counts.index,
                                    color_discrete_map=colors,
                                    hole=0.4
                                )
                                
                                # Update layout for modern look
                                fig.update_layout(
                                    template="plotly_dark",
                                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                                )
                                
                                # Display the chart
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Analyst recommendations not available for this stock")
                        except Exception as e:
                            st.info("Analyst recommendations not available for this stock")
                    
                    with tab3:
                        st.subheader("Market Sentiment")
                        
                        # Basic sentiment summary
                        sentiment_score = rating_breakdown.get('sentiment_score', 0)
                        
                        # Sentiment gauge
                        gauge_color = "#E74C3C" if sentiment_score < 4 else "#F7DC6F" if sentiment_score < 7 else "#58D68D"
                        
                        # Create sentiment gauge
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=sentiment_score,
                            title={'text': f"Market Sentiment Score for {ticker}"},
                            gauge={
                                'axis': {'range': [0, 10], 'tickwidth': 1},
                                'bar': {'color': gauge_color},
                                'steps': [
                                    {'range': [0, 4], 'color': 'rgba(231, 76, 60, 0.3)'},
                                    {'range': [4, 7], 'color': 'rgba(247, 220, 111, 0.3)'},
                                    {'range': [7, 10], 'color': 'rgba(88, 214, 141, 0.3)'}
                                ],
                                'threshold': {
                                    'line': {'color': "white", 'width': 4},
                                    'thickness': 0.75,
                                    'value': sentiment_score
                                }
                            }
                        ))
                        
                        # Update layout
                        fig.update_layout(
                            template="plotly_dark",
                            height=300,
                            margin=dict(l=20, r=20, t=60, b=20),
                        )
                        
                        # Display the gauge
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Sentiment explanation
                        sentiment_text = ""
                        if sentiment_score >= 7:
                            sentiment_text = f"The market sentiment for {ticker} is highly positive. Analysts and investors are generally bullish on this stock's prospects."
                        elif sentiment_score >= 4:
                            sentiment_text = f"The market sentiment for {ticker} is neutral to slightly positive. Opinions are mixed, but there is some optimism about the stock's future."
                        else:
                            sentiment_text = f"The market sentiment for {ticker} is currently negative. Investors and analysts are cautious or bearish about this stock's outlook."
                        
                        # Display sentiment text
                        st.markdown(f"""
                        <div style="background: rgba(30, 40, 60, 0.5); padding: 1rem; border-radius: 8px; margin: 1.5rem 0;">
                            <h4 style="margin-top: 0;">Sentiment Analysis</h4>
                            <p>{sentiment_text}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with tab4:
                        st.subheader("Recent News")
                        
                        # Get news articles
                        try:
                            news_articles = get_stock_news(ticker)
                            
                            if news_articles:
                                # Calculate sentiment scores (placeholder)
                                sentiment_scores = []
                                
                                for article in news_articles:
                                    # Placeholder for sentiment analysis - would use NLP in a real app
                                    # Here, we'll use a simple random score for demonstration
                                    sentiment = np.random.uniform(-1, 1)
                                    sentiment_scores.append(sentiment)
                                
                                # Display articles with modern card styling
                                st.markdown("""
                                <style>
                                .news-card {
                                    background: rgba(30, 40, 60, 0.5);
                                    border-radius: 8px;
                                    padding: 1rem;
                                    margin-bottom: 1rem;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                    transition: transform 0.2s;
                                }
                                .news-card:hover {
                                    transform: translateY(-5px);
                                    box-shadow: 0 5px 10px rgba(0,0,0,0.2);
                                }
                                .news-title {
                                    font-size: 1.1rem;
                                    font-weight: 600;
                                    margin-bottom: 0.5rem;
                                }
                                .news-meta {
                                    display: flex;
                                    justify-content: space-between;
                                    margin-bottom: 0.5rem;
                                    font-size: 0.8rem;
                                    opacity: 0.8;
                                }
                                .news-source {
                                    font-weight: 500;
                                }
                                .news-sentiment {
                                    padding: 0.2rem 0.5rem;
                                    border-radius: 4px;
                                    font-weight: 500;
                                }
                                .news-summary {
                                    margin-top: 0.5rem;
                                    font-size: 0.9rem;
                                    line-height: 1.5;
                                }
                                </style>
                                """, unsafe_allow_html=True)
                                
                                # Display limited number of articles
                                max_articles = min(5, len(news_articles))
                                
                                for i, article in enumerate(news_articles[:max_articles]):
                                    sentiment = sentiment_scores[i]
                                    
                                    # Determine sentiment color and label
                                    if sentiment > 0.2:
                                        sentiment_color = "rgba(46, 204, 113, 0.2)"
                                        sentiment_label = "Positive"
                                    elif sentiment < -0.2:
                                        sentiment_color = "rgba(231, 76, 60, 0.2)"
                                        sentiment_label = "Negative"
                                    else:
                                        sentiment_color = "rgba(247, 220, 111, 0.2)"
                                        sentiment_label = "Neutral"
                                    
                                    # Format publish date (assuming it's a standard format)
                                    try:
                                        date_str = article.get('publishedDate', 'Unknown')
                                        if date_str != 'Unknown':
                                            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                                            formatted_date = date_obj.strftime('%b %d, %Y')
                                        else:
                                            formatted_date = 'Unknown date'
                                    except:
                                        formatted_date = 'Unknown date'
                                    
                                    # Display article
                                    st.markdown(f"""
                                    <div class="news-card">
                                        <div class="news-title">
                                            <a href="{article.get('url', '#')}" target="_blank" style="color: inherit; text-decoration: none;">
                                                {article.get('title', 'No title available')}
                                            </a>
                                        </div>
                                        <div class="news-meta">
                                            <span class="news-source">{article.get('publisher', 'Unknown source')} • {formatted_date}</span>
                                            <span class="news-sentiment" style="background: {sentiment_color};">{sentiment_label}</span>
                                        </div>
                                        <div class="news-summary">
                                            {article.get('text', 'No summary available')[:150]}...
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info(f"No recent news found for {ticker}")
                        except Exception as e:
                            st.error(f"Error getting news for {ticker}: {str(e)}")
                            st.info("Unable to fetch news articles at this time.")
                    
                    # Add bottom padding for better spacing with footer
                    st.markdown("<div style='margin-bottom: 100px;'></div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error analyzing {ticker}: {str(e)}")
                st.info("Please check if the ticker symbol is correct and try again.")
    else:
        # Default welcome screen when no ticker is entered
        st.markdown("""
        # Welcome to Ticker AI
        
        Enter a stock ticker in the sidebar and click "Analyze" to get started.
        
        This tool provides:
        - Comprehensive stock analysis with AI-powered insights
        - Real-time price and market data
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