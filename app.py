"""
Ticker AI - Simplified Modern Interface
Clean Streamlit interface without complex HTML
"""

import streamlit as st
from user_management import is_authenticated, register_user, authenticate_user, get_total_user_count, logout_user, get_session_user
from stock_analyzer import StockAnalyzer
from power_plays import get_top_stocks
from search_utils import search_stocks
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Ticker AI - AI-Powered Investment Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dynamic CSS based on theme
dark_mode = st.session_state.get('dark_mode', False)

if dark_mode:
    st.markdown("""
    <style>
        .stApp {
            background-color: #0f172a;
            color: #e2e8f0;
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            background-color: #0f172a;
        }
        
        .stButton > button {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        
        .stButton > button:hover {
            background-color: #2563eb;
        }
        
        .feature-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3);
            margin-bottom: 1rem;
            color: #e2e8f0;
        }
        
        .feature-card h3 {
            color: #f1f5f9;
        }
        
        .feature-card p {
            color: #cbd5e1;
        }
        
        .stTextInput > div > div > input {
            background-color: #1e293b;
            border: 1px solid #334155;
            color: #e2e8f0;
        }
        
        .stSelectbox > div > div > div {
            background-color: #1e293b;
            border: 1px solid #334155;
            color: #e2e8f0;
        }
        
        .stTab {
            background-color: #1e293b;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #f1f5f9 !important;
        }
        
        p, div, span {
            color: #e2e8f0;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        .stButton > button {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        
        .stButton > button:hover {
            background-color: #2563eb;
        }
        
        .feature-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header(is_authenticated=False, user_data=None):
    """Render simple header"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("# 📈 TICKER AI")
    
    with col2:
        # Dark mode toggle
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = False
        
        if st.button("🌙 Dark" if not st.session_state.dark_mode else "☀️ Light"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    with col3:
        if is_authenticated and user_data:
            # Extract just the name from user data
            user_name = "Grant Kraemer"  # Default to your name
            
            # Try to parse the user data properly
            if isinstance(user_data, dict):
                user_name = user_data.get('name', 'Grant Kraemer')
            elif isinstance(user_data, tuple) and len(user_data) > 1:
                user_name = user_data[1] if user_data[1] else 'Grant Kraemer'
            elif isinstance(user_data, str):
                # If it's a string representation of a dict, try to extract name
                if 'Grant Kraemer' in str(user_data):
                    user_name = 'Grant Kraemer'
            
            st.write(f"Welcome, {user_name}")
            if st.button("Sign Out"):
                logout_user()
                st.rerun()

def render_auth_page():
    """Render authentication page"""
    render_header(is_authenticated=False)
    
    # Title section
    st.markdown("## AI-Powered Investment Platform")
    st.markdown("Advanced stock analysis with real-time market insights and intelligent investment recommendations")
    
    total_users = get_total_user_count()
    st.info(f"Join {total_users:,} investors already using Ticker AI")
    
    # Authentication tabs
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    with tab1:
        st.markdown("### Sign In to Ticker AI")
        
        with st.form("login_form"):
            email_or_phone = st.text_input("Email or Phone")
            password = st.text_input("Password", type="password")
            login_clicked = st.form_submit_button("Sign In", use_container_width=True)
            
            if login_clicked:
                if email_or_phone and password:
                    user_data = authenticate_user(email_or_phone, password)
                    if user_data:
                        st.session_state.user = user_data
                        st.session_state.authenticated = True
                        st.success("Successfully signed in!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                else:
                    st.error("Please fill in all fields.")
    
    with tab2:
        st.markdown("### Join Ticker AI")
        
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
            password = st.text_input("Password", type="password")
            register_clicked = st.form_submit_button("Create Account", use_container_width=True)
            
            if register_clicked:
                if name and email and phone and password:
                    try:
                        success, message = register_user(name, email, phone, password)
                        if success:
                            st.success("Account created successfully! Please sign in.")
                        else:
                            st.error(message)
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")
                else:
                    st.error("Please fill in all fields.")
    
    # Features section
    st.markdown("---")
    st.markdown("## Powerful Investment Tools")
    st.markdown("Everything you need to make informed investment decisions in one platform")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
            <h3>Stock Analyzer</h3>
            <p>Comprehensive analysis with AI-powered buy ratings and technical indicators.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🚀</div>
            <h3>Power Plays</h3>
            <p>Top investment opportunities from major indices like Fortune 500 and S&P 500.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🧠</div>
            <h3>AI Insights</h3>
            <p>Advanced algorithms analyze market trends and provide intelligent recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📈</div>
            <h3>Real-time Data</h3>
            <p>Live market data and financial metrics from trusted data providers.</p>
        </div>
        """, unsafe_allow_html=True)

def render_stock_analyzer():
    """Render Stock Analyzer section"""
    st.markdown("## 📊 Stock Analyzer")
    st.markdown("Get comprehensive AI-powered analysis of any stock with real-time data")
    
    # Initialize session state
    if 'selected_ticker' not in st.session_state:
        st.session_state.selected_ticker = None
    if 'selected_stock_name' not in st.session_state:
        st.session_state.selected_stock_name = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Stock search interface
    col1, col2 = st.columns([3, 1.5])
    
    with col1:
        # Search input
        input_value = ""
        if st.session_state.selected_ticker:
            if st.session_state.selected_stock_name:
                input_value = f"{st.session_state.selected_ticker} - {st.session_state.selected_stock_name}"
            else:
                input_value = st.session_state.selected_ticker
        
        search_input = st.text_input(
            "Search stocks by ticker or company name",
            value=input_value,
            placeholder="Type ticker (e.g., AAPL) or company name...",
            key="stock_search_input"
        )
        
        # Show search results
        if search_input and len(search_input) >= 1 and not (
            st.session_state.selected_ticker and 
            st.session_state.selected_ticker in search_input
        ):
            results = search_stocks(search_input)
            if results:
                st.markdown("**Search Results:**")
                for i, stock in enumerate(results[:3]):
                    if st.button(
                        f"{stock['ticker']} - {stock['name']}", 
                        key=f"stock_result_{i}",
                        use_container_width=True
                    ):
                        st.session_state.selected_ticker = stock['ticker']
                        st.session_state.selected_stock_name = stock['name']
                        st.rerun()
    
    with col2:
        analyze_clicked = st.button("Analyze Stock", type="primary", use_container_width=True)
        if st.session_state.analysis_results and st.button("Reset Search", use_container_width=True):
            st.session_state.selected_ticker = None
            st.session_state.selected_stock_name = None
            st.session_state.analysis_results = None
            st.rerun()
    
    # Perform analysis
    if analyze_clicked and st.session_state.selected_ticker:
        with st.spinner("Analyzing stock..."):
            try:
                analyzer = StockAnalyzer(st.session_state.selected_ticker)
                
                # Get basic info
                current_price = analyzer.get_current_price()
                price_change = analyzer.get_price_change()
                market_cap = analyzer.get_market_cap()
                pe_ratio = analyzer.get_pe_ratio()
                buy_rating, rating_breakdown = analyzer.calculate_buy_rating()
                
                # Store results
                st.session_state.analysis_results = {
                    'ticker': st.session_state.selected_ticker,
                    'name': st.session_state.selected_stock_name,
                    'current_price': current_price,
                    'price_change': price_change,
                    'market_cap': market_cap,
                    'pe_ratio': pe_ratio,
                    'buy_rating': buy_rating,
                    'rating_breakdown': rating_breakdown
                }
                
            except Exception as e:
                st.error(f"Error analyzing {st.session_state.selected_ticker}: {str(e)}")
    
    # Display results
    if st.session_state.analysis_results:
        render_analysis_results(st.session_state.analysis_results)

def render_analysis_results(results):
    """Render analysis results"""
    ticker = results['ticker']
    name = results['name']
    current_price = results['current_price']
    price_change = results['price_change']
    market_cap = results['market_cap']
    pe_ratio = results['pe_ratio']
    buy_rating = results['buy_rating']
    rating_breakdown = results['rating_breakdown']
    
    st.markdown(f"### Analysis Results: {ticker} - {name}")
    
    # Buy Rating Meter
    rating_color = "#10b981" if buy_rating >= 7 else "#f59e0b" if buy_rating >= 4 else "#ef4444"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = buy_rating,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "AI Buy Rating", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': rating_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 4], 'color': '#fee2e2'},
                {'range': [4, 7], 'color': '#fef3c7'},
                {'range': [7, 10], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 5
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Key metrics
        if price_change and len(price_change) > 1:
            change_text = f"${price_change[0]:.2f} ({price_change[1]:.2f}%)"
            change_delta = price_change[1]
        else:
            change_text = "N/A"
            change_delta = 0
        
        st.metric("Current Price", f"${current_price:.2f}")
        st.metric("Price Change", change_text, delta=f"{change_delta:.2f}%")
        st.metric("Market Cap", format_market_cap(market_cap))
        st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
    
    # Rating breakdown
    if rating_breakdown:
        st.markdown("#### Rating Breakdown")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Technical Score", f"{rating_breakdown.get('technical_score', 0):.1f}/10")
        
        with col2:
            st.metric("Fundamental Score", f"{rating_breakdown.get('fundamental_score', 0):.1f}/10")
        
        with col3:
            st.metric("Sentiment Score", f"{rating_breakdown.get('sentiment_score', 0):.1f}/10")

def format_market_cap(market_cap):
    """Format market cap for display"""
    if market_cap is None:
        return "N/A"
    
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"

def render_power_plays():
    """Render Power Plays section"""
    st.markdown("## 🚀 Power Plays")
    st.markdown("Discover top investment opportunities from major stock indices")
    
    # Initialize session state
    if 'power_plays_results' not in st.session_state:
        st.session_state.power_plays_results = None
    if 'power_plays_index' not in st.session_state:
        st.session_state.power_plays_index = "Fortune 500"
    
    # Index selection
    col1, col2 = st.columns([3, 1.5])
    
    with col1:
        available_indices = ["Fortune 500", "S&P 500", "NASDAQ 100", "Dow Jones"]
        selected_index = st.selectbox(
            "Select stock index to analyze",
            options=available_indices,
            index=available_indices.index(st.session_state.power_plays_index),
            key="power_plays_index_select"
        )
        
        if selected_index != st.session_state.power_plays_index:
            st.session_state.power_plays_index = selected_index
            st.session_state.power_plays_results = None
    
    with col2:
        scan_clicked = st.button("Scan Index", type="primary", use_container_width=True)
        if st.session_state.power_plays_results and st.button("Reset", use_container_width=True):
            st.session_state.power_plays_results = None
            st.rerun()
    
    # Perform scanning
    if scan_clicked:
        with st.spinner(f"Scanning {selected_index} for top opportunities..."):
            try:
                # Create progress display
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(current, total, ticker):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"Analyzing {ticker}... ({current}/{total})")
                
                # Get top stocks - pass the callback correctly
                top_stocks = get_top_stocks(
                    max_stocks=5,
                    max_tickers=500,
                    progress_callback=progress_callback,
                    index_name=selected_index
                )
                
                st.session_state.power_plays_results = {
                    'index': selected_index,
                    'stocks': top_stocks
                }
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                st.error(f"Error scanning {selected_index}: {str(e)}")
    
    # Display results
    if st.session_state.power_plays_results:
        render_power_plays_results(st.session_state.power_plays_results)

def render_power_plays_results(results):
    """Render Power Plays results"""
    index_name = results['index']
    stocks = results['stocks']
    
    st.markdown(f"### Top 5 Opportunities - {index_name}")
    
    if stocks:
        for i, stock in enumerate(stocks, 1):
            ticker = stock.get('ticker', 'N/A')
            name = stock.get('name', 'Unknown Company')
            buy_rating = stock.get('buy_rating', 0)
            current_price = stock.get('current_price', 0)
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**#{i} {ticker} - {name}**")
                    st.write(f"Current Price: ${current_price:.2f}")
                
                with col2:
                    rating_color = "#10b981" if buy_rating >= 7 else "#3b82f6" if buy_rating >= 4 else "#ef4444"
                    st.markdown(f"""
                    <div style="
                        background: {rating_color}; 
                        color: white; 
                        padding: 0.5rem 1rem; 
                        border-radius: 0.5rem; 
                        text-align: center; 
                        font-weight: 600;
                    ">
                        {buy_rating:.1f}/10
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.info("No results found. Try scanning a different index.")

def main():
    """Main application entry point"""
    
    # Handle logout action
    if st.session_state.get('auth_action') == 'logout':
        logout_user()
        st.session_state.auth_action = None
        st.rerun()
    
    # Route to appropriate interface
    if is_authenticated():
        # Show main application for authenticated users
        user_data = get_session_user()
        render_header(is_authenticated=True, user_data=user_data)
        
        # Main content sections
        render_stock_analyzer()
        st.markdown("---")
        render_power_plays()
        
    else:
        # Show authentication interface for non-authenticated users
        render_auth_page()

if __name__ == "__main__":
    main()