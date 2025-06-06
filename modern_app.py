import streamlit as st

# Configure Streamlit page FIRST
st.set_page_config(
    page_title="Ticker AI - Modern Investment Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Now import other modules
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
from modern_auth import modern_auth_page, modern_logout_button
from admin import is_admin, admin_panel
from power_plays import display_power_plays

# Import stock database from main app
from app import POPULAR_STOCKS, search_stocks

def load_modern_css():
    """Load modern CSS framework"""
    st.markdown("""
    <style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* CSS Variables for theming */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;
        --border-color: #e2e8f0;
        --accent-primary: #3b82f6;
        --accent-secondary: #06b6d4;
        --accent-hover: #2563eb;
        --success: #22c55e;
        --warning: #f59e0b;
        --error: #ef4444;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }
    
    [data-theme="dark"] {
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --border-color: #475569;
        --accent-primary: #60a5fa;
        --accent-secondary: #22d3ee;
        --accent-hover: #3b82f6;
        --success: #4ade80;
        --warning: #fbbf24;
        --error: #f87171;
    }
    
    /* Base styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* Hide default Streamlit components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Modern header */
    .modern-header {
        background: var(--bg-primary);
        border-bottom: 1px solid var(--border-color);
        padding: 1rem 0;
        position: sticky;
        top: 0;
        z-index: 1000;
        backdrop-filter: blur(8px);
        box-shadow: var(--shadow-sm);
    }
    
    .header-container {
        max-width: 1280px;
        margin: 0 auto;
        padding: 0 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent-primary);
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .logo-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
    }
    
    .nav-menu {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-link {
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .nav-link:hover, .nav-link.active {
        color: var(--accent-primary);
        background-color: var(--bg-secondary);
    }
    
    .theme-toggle {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 0.5rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        transition: all 0.2s ease;
        font-size: 1.2rem;
    }
    
    .theme-toggle:hover {
        background: var(--bg-tertiary);
        border-color: var(--accent-primary);
    }
    
    /* Modern sections */
    .section {
        padding: 4rem 0;
    }
    
    .container {
        max-width: 1280px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .hero {
        background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
        padding: 6rem 0;
        text-align: center;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }
    
    /* Modern cards */
    .card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 2rem;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: var(--accent-primary);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        min-height: 44px;
    }
    
    .stButton > button:hover {
        background: var(--accent-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Modern inputs */
    .stTextInput > div > div > input {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Grid layout */
    .grid {
        display: grid;
        gap: 2rem;
    }
    
    .grid-2 {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .grid-3 {
        grid-template-columns: repeat(3, 1fr);
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .header-container {
            padding: 0 1rem;
        }
        
        .nav-menu {
            display: none;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .grid-2, .grid-3 {
            grid-template-columns: 1fr;
        }
        
        .container {
            padding: 0 1rem;
        }
        
        .section {
            padding: 2rem 0;
        }
        
        .hero {
            padding: 4rem 0;
        }
    }
    
    /* Smooth transitions */
    * {
        transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

def modern_header():
    """Modern header with navigation and theme toggle"""
    user = get_session_user()
    
    st.markdown(f"""
    <header class="modern-header">
        <div class="header-container">
            <div class="logo">
                <div class="logo-icon">T</div>
                Ticker AI
            </div>
            
            <nav class="nav-menu">
                <a href="#stock-analyzer" class="nav-link">Stock Analyzer</a>
                <a href="#power-plays" class="nav-link">Power Plays</a>
                <a href="#about" class="nav-link">About</a>
                {f'<span style="color: var(--text-secondary);">Welcome, {user.get("name", "User")}</span>' if user else ''}
            </nav>
            
            <div style="display: flex; align-items: center; gap: 1rem;">
                <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">
                    <span id="theme-icon">🌙</span>
                </button>
                {f'<button onclick="signOut()" style="background: var(--error); color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">Sign Out</button>' if user else ''}
            </div>
        </div>
    </header>
    
    <script>
    function toggleTheme() {{
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        document.getElementById('theme-icon').textContent = newTheme === 'dark' ? '☀️' : '🌙';
        localStorage.setItem('theme', newTheme);
    }}
    
    function signOut() {{
        if (confirm('Are you sure you want to sign out?')) {{
            // Trigger Streamlit rerun to handle logout
            window.parent.postMessage({{type: 'streamlit:logout'}}, '*');
        }}
    }}
    
    // Initialize theme
    document.addEventListener('DOMContentLoaded', function() {{
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        document.getElementById('theme-icon').textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }});
    </script>
    """, unsafe_allow_html=True)

def modern_hero():
    """Modern hero section"""
    st.markdown("""
    <section class="hero">
        <div class="container">
            <h1 class="hero-title">AI-Powered Investment Intelligence</h1>
            <p class="hero-subtitle">
                Unlock market insights with advanced AI algorithms. Analyze stocks, discover opportunities, 
                and make data-driven investment decisions with confidence.
            </p>
        </div>
    </section>
    """, unsafe_allow_html=True)

def modern_stock_analyzer():
    """Modern stock analyzer section"""
    st.markdown('<section id="stock-analyzer" class="section">', unsafe_allow_html=True)
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h2 class="card-title">📈 Stock Analyzer</h2>
        <p style="color: var(--text-secondary); margin-bottom: 2rem;">
            Get comprehensive analysis of any stock with AI-powered insights, technical indicators, and fundamental metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search functionality
    col1, col2 = st.columns([3, 1.5])
    
    with col1:
        search_input = st.text_input(
            "Search stocks by ticker or company name",
            placeholder="Type ticker (e.g., AAPL) or company name...",
            key="modern_stock_search"
        )
    
    with col2:
        if st.session_state.get("analysis_performed"):
            if st.button("Reset Search", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith("selected_") or key == "analysis_performed":
                        del st.session_state[key]
                st.rerun()
    
    # Show search results
    if search_input and len(search_input) >= 1:
        results = search_stocks(search_input)
        if results:
            st.markdown("**Search Results:**")
            for i, stock in enumerate(results[:3]):
                if st.button(f"{stock['ticker']} - {stock['name']}", key=f"stock_select_{i}"):
                    st.session_state.selected_ticker = stock['ticker']
                    st.session_state.selected_stock_name = stock['name']
                    st.session_state.analysis_performed = True
                    st.rerun()
    
    # Display analysis if stock is selected
    if st.session_state.get("selected_ticker"):
        display_modern_stock_analysis(st.session_state.selected_ticker)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

def display_modern_stock_analysis(ticker):
    """Display modern stock analysis"""
    try:
        analyzer = StockAnalyzer(ticker)
        
        # Basic info
        current_price = analyzer.get_current_price()
        price_change = analyzer.get_price_change()
        
        st.markdown(f"""
        <div class="card" style="margin-top: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <div>
                    <h3 style="margin: 0; color: var(--text-primary);">{ticker}</h3>
                    <p style="margin: 0; color: var(--text-secondary);">{st.session_state.get('selected_stock_name', '')}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">${current_price:.2f}</div>
                    <div style="color: {'var(--success)' if price_change['change'] >= 0 else 'var(--error)'};">
                        {'+' if price_change['change'] >= 0 else ''}{price_change['change']:.2f} ({price_change['percent_change']:.2f}%)
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Buy rating
        buy_rating, breakdown = analyzer.calculate_buy_rating()
        
        st.markdown(f"""
        <div class="card" style="margin-top: 1rem;">
            <h4 style="color: var(--text-primary);">AI Buy Rating</h4>
            <div style="display: flex; align-items: center; gap: 1rem; margin: 1rem 0;">
                <div style="font-size: 3rem; font-weight: 700; color: var(--accent-primary);">{buy_rating:.1f}/10</div>
                <div>
                    <div style="color: var(--text-secondary);">Technical: {breakdown['technical']:.1f}/10</div>
                    <div style="color: var(--text-secondary);">Fundamental: {breakdown['fundamental']:.1f}/10</div>
                    <div style="color: var(--text-secondary);">Sentiment: {breakdown['sentiment']:.1f}/10</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Key financials
        try:
            info = analyzer.ticker.info
            st.markdown("""
            <div class="card" style="margin-top: 1rem;">
                <h4 style="color: var(--text-primary);">Key Financials</h4>
                <div class="grid grid-3" style="margin-top: 1rem;">
            """, unsafe_allow_html=True)
            
            metrics = [
                ("Market Cap", info.get('marketCap', 'N/A')),
                ("P/E Ratio", info.get('trailingPE', 'N/A')),
                ("EPS", info.get('trailingEps', 'N/A')),
                ("Revenue", info.get('totalRevenue', 'N/A')),
                ("Profit Margin", info.get('profitMargins', 'N/A')),
                ("52W High", info.get('fiftyTwoWeekHigh', 'N/A'))
            ]
            
            for label, value in metrics:
                if isinstance(value, (int, float)) and label == "Market Cap":
                    value = format_large_number(value)
                elif isinstance(value, (int, float)) and label == "Revenue":
                    value = format_large_number(value)
                elif isinstance(value, float) and label in ["P/E Ratio", "EPS", "52W High"]:
                    value = f"{value:.2f}"
                elif isinstance(value, float) and label == "Profit Margin":
                    value = f"{value:.1%}"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--text-primary);">{value}</div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem;">{label}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)
        except:
            pass
            
    except Exception as e:
        st.error(f"Error analyzing {ticker}: {str(e)}")

def modern_power_plays():
    """Modern power plays section"""
    st.markdown('<section id="power-plays" class="section">', unsafe_allow_html=True)
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h2 class="card-title">🚀 Power Plays</h2>
        <p style="color: var(--text-secondary); margin-bottom: 2rem;">
            Discover top-rated investment opportunities from major market indices with AI-powered screening.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Power plays content
    display_power_plays()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

def modern_about():
    """Modern about section"""
    st.markdown('<section id="about" class="section">', unsafe_allow_html=True)
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h2 class="card-title">About Ticker AI</h2>
        <div style="color: var(--text-secondary); line-height: 1.6;">
            <p>Ticker AI leverages advanced artificial intelligence to provide comprehensive stock market analysis and investment insights. Our platform combines multiple data sources and analytical methods to help investors make informed decisions.</p>
            
            <h4 style="color: var(--text-primary); margin-top: 2rem;">Key Features:</h4>
            <ul>
                <li><strong>AI-Powered Analysis:</strong> Advanced algorithms analyze technical patterns, fundamentals, and market sentiment</li>
                <li><strong>Real-Time Data:</strong> Live market data from trusted financial sources</li>
                <li><strong>Comprehensive Screening:</strong> Scan major market indices for top opportunities</li>
                <li><strong>Risk Assessment:</strong> Detailed risk analysis and rating methodology</li>
            </ul>
            
            <h4 style="color: var(--text-primary); margin-top: 2rem;">Buy Rating Methodology:</h4>
            <p>Our AI buy rating (1-10 scale) combines:</p>
            <ul>
                <li><strong>Technical Analysis (40%):</strong> Price trends, momentum indicators, and chart patterns</li>
                <li><strong>Fundamental Analysis (40%):</strong> Financial metrics, valuation ratios, and growth indicators</li>
                <li><strong>Market Sentiment (20%):</strong> News sentiment, analyst recommendations, and market dynamics</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

def main():
    """Main application with modern UI"""
    
    # Load modern CSS
    load_modern_css()
    
    # Check authentication
    if not is_authenticated():
        modern_auth_page()
        return
    
    # Handle logout
    if st.query_params.get("logout") == "true":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Modern layout
    modern_header()
    modern_hero()
    modern_stock_analyzer()
    modern_power_plays()
    modern_about()
    
    # Admin panel (if admin)
    if is_admin():
        st.markdown('<section class="section">', unsafe_allow_html=True)
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <h2 class="card-title">🔧 Admin Panel</h2>
        </div>
        """, unsafe_allow_html=True)
        admin_panel()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</section>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()