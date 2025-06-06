"""
Ticker AI - Simplified Modern Interface
Clean Streamlit interface without complex HTML
"""

import streamlit as st
from user_management import is_authenticated, register_user, authenticate_user, get_total_user_count, logout_user, get_session_user
from stock_analyzer import StockAnalyzer
from power_plays import get_top_stocks
from search_utils import search_stocks
from ai_analysis import generate_ai_buy_analysis, get_recommendation_color, get_recommendation_text
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Ticker AI - AI-Powered Investment Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean styling
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
    
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 0.75rem;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
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
    
    .analysis-container {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 1rem;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def render_header(is_authenticated=False, user_data=None):
    """Render simple header"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("# Ticker AI")
    
    with col2:
        if is_authenticated and user_data:
            # Get only the user's name from the data
            if isinstance(user_data, dict):
                user_name = user_data.get('name', 'User')
            elif isinstance(user_data, tuple) and len(user_data) > 1:
                user_name = user_data[1]
            else:
                user_name = 'User'
            
            st.write(f"Welcome, {user_name}")
            if st.button("Sign Out", key="header_signout"):
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
                    success, user_data = authenticate_user(email_or_phone, password)
                    if success:
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
        if st.button("Reset Search", use_container_width=True):
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
                    'rating_breakdown': rating_breakdown,
                    'analyzer': analyzer
                }
                
            except Exception as e:
                st.error(f"Error analyzing {st.session_state.selected_ticker}: {str(e)}")
    
    # Display results
    if st.session_state.analysis_results:
        render_analysis_results(st.session_state.analysis_results)

def render_analysis_results(results):
    """Render comprehensive analysis results"""
    ticker = results['ticker']
    name = results['name']
    current_price = results['current_price']
    price_change = results['price_change']
    market_cap = results['market_cap']
    pe_ratio = results['pe_ratio']
    buy_rating = results['buy_rating']
    rating_breakdown = results['rating_breakdown']
    analyzer = results.get('analyzer')
    
    st.markdown(f"### {name} ({ticker})")
    
    # AI Buy Rating Section
    st.markdown("#### 🤖 AI Buy Rating")
    
    # Determine rating text
    if buy_rating >= 7.5:
        rating_text = "Strong Buy"
        rating_color = "#10b981"
    elif buy_rating >= 6:
        rating_text = "Buy"
        rating_color = "#059669"
    elif buy_rating >= 4:
        rating_text = "Hold"
        rating_color = "#f59e0b"
    else:
        rating_text = "Sell"
        rating_color = "#ef4444"
    
    # Create gauge with modern styling
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = buy_rating,
        title = {'text': f"{rating_text}", 'font': {'size': 18, 'color': rating_color}},
        number = {'font': {'size': 36, 'color': rating_color}},
        gauge = {
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#64748b"},
            'bar': {'color': rating_color, 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, 4], 'color': '#fef2f2'},
                {'range': [4, 7], 'color': '#fefce8'},
                {'range': [7, 10], 'color': '#f0fdf4'}
            ],
            'threshold': {
                'line': {'color': rating_color, 'width': 3},
                'thickness': 0.8,
                'value': buy_rating
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    # Rating components section
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Rating Components:**")
        
        # Get correct scores from rating breakdown
        tech_score = 0
        fund_score = 0
        sent_score = 0
        
        if isinstance(rating_breakdown, dict):
            # Try different possible keys for the scores
            for key, value in rating_breakdown.items():
                if 'technical' in key.lower():
                    if isinstance(value, dict) and 'score' in value:
                        tech_score = value['score']
                    elif isinstance(value, (int, float)):
                        tech_score = value
                elif 'fundamental' in key.lower():
                    if isinstance(value, dict) and 'score' in value:
                        fund_score = value['score']
                    elif isinstance(value, (int, float)):
                        fund_score = value
                elif 'sentiment' in key.lower():
                    if isinstance(value, dict) and 'score' in value:
                        sent_score = value['score']
                    elif isinstance(value, (int, float)):
                        sent_score = value
        
        # Technical Analysis
        tech_color = "#10b981" if tech_score >= 7 else "#f59e0b" if tech_score >= 4 else "#ef4444"
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; font-size: 16px;">
            <span style="font-weight: 500;">📊 Technical Analysis</span>
            <span style="color: {tech_color}; font-weight: 700; font-size: 18px;">{tech_score:.1f}/10</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Fundamental Analysis
        fund_color = "#10b981" if fund_score >= 7 else "#f59e0b" if fund_score >= 4 else "#ef4444"
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; font-size: 16px;">
            <span style="font-weight: 500;">💰 Fundamental Analysis</span>
            <span style="color: {fund_color}; font-weight: 700; font-size: 18px;">{fund_score:.1f}/10</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Market Sentiment
        sent_color = "#10b981" if sent_score >= 7 else "#f59e0b" if sent_score >= 4 else "#ef4444"
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; font-size: 16px;">
            <span style="font-weight: 500;">🏪 Market Sentiment</span>
            <span style="color: {sent_color}; font-weight: 700; font-size: 18px;">{sent_score:.1f}/10</span>
        </div>
        """, unsafe_allow_html=True)
    
    # AI Buy Analysis Section
    st.markdown("#### 🤖 AI Buy Analysis")
    
    try:
        # Generate AI analysis using the rating components
        rating_components = {
            'overall_rating': buy_rating,
            'technical_score': tech_score,
            'fundamental_score': fund_score,
            'sentiment_score': sent_score
        }
        
        with st.spinner("Generating AI analysis..."):
            ai_analysis = generate_ai_buy_analysis(ticker, analyzer, rating_components)
        
        # Get recommendation details
        recommendation = get_recommendation_text(buy_rating)
        rec_color = get_recommendation_color(buy_rating)
        
        # Display recommendation badge and analysis
        st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 12px; border-left: 4px solid {'#10b981' if recommendation == 'BUY' else '#f59e0b' if recommendation == 'HOLD' else '#ef4444'}; margin: 16px 0;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 20px; margin-right: 8px;">{rec_color}</span>
                <span style="font-size: 18px; font-weight: 700; color: {'#10b981' if recommendation == 'BUY' else '#f59e0b' if recommendation == 'HOLD' else '#ef4444'};">{recommendation}</span>
            </div>
            <p style="margin: 0; font-size: 16px; line-height: 1.6; color: #374151;">{ai_analysis}</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Unable to generate AI analysis. Please check your OpenAI API key configuration.")
    
    # Key Financials Section
    st.markdown("#### 💰 Key Financials")
    
    try:
        # Get additional financial data
        info = analyzer.stock.info if analyzer else {}
        
        # First row of metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if price_change and len(price_change) > 1:
                change_delta = price_change[1]
            else:
                change_delta = 0
            st.metric("Price", f"${current_price:.2f}", delta=f"{change_delta:.2f}%")
        
        with col2:
            target_price = info.get('targetMeanPrice')
            if target_price and target_price > 0:
                upside = ((target_price / current_price) - 1) * 100
                upside_text = f"({upside:+.1f}% upside)" if upside > 0 else f"({upside:.1f}% downside)"
                st.metric("Analyst Target", f"${target_price:.2f} {upside_text}")
            else:
                st.metric("Analyst Target", "N/A")
        
        with col3:
            st.metric("Market Cap", format_market_cap(market_cap))
        
        with col4:
            pe_display = f"{pe_ratio:.2f}" if pe_ratio and pe_ratio > 0 else "N/A"
            st.metric("P/E Ratio", pe_display)
        
        # Second row of metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            forward_pe = info.get('forwardPE')
            if forward_pe:
                st.metric("Forward P/E", f"{forward_pe:.2f}")
            else:
                st.metric("Forward P/E", "N/A")
        
        with col2:
            profit_margin = info.get('profitMargins')
            if profit_margin:
                st.metric("Profit Margin", f"{profit_margin * 100:.2f}%")
            else:
                st.metric("Profit Margin", "N/A")
        
        with col3:
            revenue = info.get('totalRevenue')
            if revenue:
                st.metric("Net Revenue", format_market_cap(revenue))
            else:
                st.metric("Net Revenue", "N/A")
        
        with col4:
            dividend_yield = info.get('dividendYield')
            if dividend_yield:
                st.metric("Dividend", f"{dividend_yield:.2f}%")
            else:
                st.metric("Dividend", "N/A")
    
    except Exception as e:
        st.error(f"Error loading financial data: {str(e)}")
    
    # Detailed Analysis Tabs
    render_detailed_analysis_tabs(ticker, analyzer)

def render_detailed_analysis_tabs(ticker, analyzer):
    """Render comprehensive analysis tabs"""
    tab1, tab2, tab3 = st.tabs(["📊 Sector Analysis", "📈 Historical Performance", "🔍 Upcoming Earnings"])
    
    with tab1:
        render_sector_analysis(ticker, analyzer)
    
    with tab2:
        render_historical_performance(ticker, analyzer)
    
    with tab3:
        render_earnings_section(ticker, analyzer)

def render_sector_analysis(ticker, analyzer):
    """Render sector analysis section"""
    try:
        info = analyzer.stock.info
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        
        st.markdown(f"**Sector:** {sector}")
        st.markdown(f"**Industry:** {industry}")
        
        if sector != 'N/A':
            st.markdown("#### Sector Comparison")
            
            # Get sector peers for comparison
            sector_peers = get_sector_peers(ticker, sector)
            
            if sector_peers:
                st.markdown("**Similar Companies in Sector:**")
                
                for peer in sector_peers[:3]:  # Show top 3 peers
                    try:
                        peer_analyzer = StockAnalyzer(peer['ticker'])
                        peer_info = peer_analyzer.stock.info
                        peer_price = peer_analyzer.get_current_price()
                        peer_market_cap = peer_analyzer.get_market_cap()
                        peer_pe = peer_analyzer.get_pe_ratio()
                        
                        with st.container():
                            st.markdown(f"**{peer['name']} ({peer['ticker']})**")
                            
                            col1, col2, col3, col4, col5, col6 = st.columns(6)
                            
                            with col1:
                                st.metric("Price", f"${peer_price:.2f}")
                            
                            with col2:
                                st.metric("Market Cap", format_market_cap(peer_market_cap))
                            
                            with col3:
                                pe_display = f"{peer_pe:.2f}" if peer_pe and peer_pe > 0 else "N/A"
                                st.metric("P/E", pe_display)
                            
                            with col4:
                                profit_margin = peer_info.get('profitMargins')
                                if profit_margin:
                                    st.metric("Profit Margin", f"{profit_margin * 100:.2f}%")
                                else:
                                    st.metric("Profit Margin", "N/A")
                            
                            with col5:
                                revenue = peer_info.get('totalRevenue')
                                if revenue:
                                    st.metric("Net Revenue", format_market_cap(revenue))
                                else:
                                    st.metric("Net Revenue", "N/A")
                            
                            with col6:
                                dividend_yield = peer_info.get('dividendYield')
                                if dividend_yield:
                                    st.metric("Dividend", f"{dividend_yield:.2f}%")
                                else:
                                    st.metric("Dividend", "N/A")
                            
                            st.markdown("---")
                    
                    except Exception as e:
                        st.warning(f"Could not load data for {peer['ticker']}")
                        continue
            else:
                st.info("Sector peer data not available")
        
    except Exception as e:
        st.error(f"Error loading sector analysis: {str(e)}")

def get_sector_peers(ticker, sector):
    """Get sector peers for comparison"""
    # Technology sector peers
    tech_peers = [
        {"ticker": "AAPL", "name": "Apple Inc."},
        {"ticker": "MSFT", "name": "Microsoft Corporation"},
        {"ticker": "GOOGL", "name": "Alphabet Inc."},
        {"ticker": "META", "name": "Meta Platforms"},
        {"ticker": "NVDA", "name": "NVIDIA Corporation"},
        {"ticker": "AMZN", "name": "Amazon.com Inc."},
        {"ticker": "TSLA", "name": "Tesla Inc."},
        {"ticker": "NFLX", "name": "Netflix Inc."},
        {"ticker": "CRM", "name": "Salesforce Inc."},
        {"ticker": "ORCL", "name": "Oracle Corporation"}
    ]
    
    # Financial sector peers
    financial_peers = [
        {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
        {"ticker": "BAC", "name": "Bank of America Corp"},
        {"ticker": "WFC", "name": "Wells Fargo & Company"},
        {"ticker": "GS", "name": "Goldman Sachs Group Inc"},
        {"ticker": "MS", "name": "Morgan Stanley"},
        {"ticker": "C", "name": "Citigroup Inc."},
        {"ticker": "BRK.B", "name": "Berkshire Hathaway Inc."},
        {"ticker": "V", "name": "Visa Inc."},
        {"ticker": "MA", "name": "Mastercard Inc."},
        {"ticker": "AXP", "name": "American Express Company"}
    ]
    
    # Healthcare sector peers
    healthcare_peers = [
        {"ticker": "JNJ", "name": "Johnson & Johnson"},
        {"ticker": "PFE", "name": "Pfizer Inc."},
        {"ticker": "UNH", "name": "UnitedHealth Group Inc"},
        {"ticker": "ABBV", "name": "AbbVie Inc."},
        {"ticker": "LLY", "name": "Eli Lilly and Company"},
        {"ticker": "MRK", "name": "Merck & Co. Inc."},
        {"ticker": "BMY", "name": "Bristol-Myers Squibb"},
        {"ticker": "AMGN", "name": "Amgen Inc."},
        {"ticker": "GILD", "name": "Gilead Sciences Inc."},
        {"ticker": "CVS", "name": "CVS Health Corporation"}
    ]
    
    # Return appropriate peers based on sector
    if 'Technology' in sector:
        return [peer for peer in tech_peers if peer['ticker'] != ticker]
    elif 'Financial' in sector or 'Bank' in sector:
        return [peer for peer in financial_peers if peer['ticker'] != ticker]
    elif 'Healthcare' in sector or 'Pharmaceutical' in sector:
        return [peer for peer in healthcare_peers if peer['ticker'] != ticker]
    else:
        # Return a mix for other sectors
        return [peer for peer in tech_peers[:3] + financial_peers[:3] if peer['ticker'] != ticker]

def render_historical_performance(ticker, analyzer):
    """Render historical performance section"""
    st.markdown("#### Select Time Period")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        timeframe = st.selectbox(
            "Time Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,  # Default to 1 year
            key=f"timeframe_{ticker}"
        )
    
    try:
        # Get historical data
        hist_data = analyzer.get_historical_data(timeframe)
        
        if hist_data is not None and not hist_data.empty:
            st.markdown(f"#### {ticker} - Market Price ({timeframe.upper()})")
            
            # Create interactive price chart
            fig = go.Figure()
            
            # Add price line
            fig.add_trace(
                go.Scatter(
                    x=hist_data.index,
                    y=hist_data['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#3b82f6', width=2),
                    hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: $%{y:.2f}<extra></extra>'
                )
            )
            
            # Update layout for mobile responsiveness
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=40),
                xaxis=dict(
                    title="Date",
                    showgrid=True,
                    gridcolor='rgba(128, 128, 128, 0.2)'
                ),
                yaxis=dict(
                    title="Price ($)",
                    showgrid=True,
                    gridcolor='rgba(128, 128, 128, 0.2)'
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance metrics
            st.markdown("#### Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate performance metrics
            start_price = hist_data['Close'].iloc[0]
            end_price = hist_data['Close'].iloc[-1]
            total_return = ((end_price / start_price) - 1) * 100
            
            high_price = hist_data['Close'].max()
            low_price = hist_data['Close'].min()
            
            volatility = hist_data['Close'].pct_change().std() * (252 ** 0.5) * 100  # Annualized volatility
            
            with col1:
                st.metric("Total Return", f"{total_return:.2f}%")
            
            with col2:
                st.metric("Period High", f"${high_price:.2f}")
            
            with col3:
                st.metric("Period Low", f"${low_price:.2f}")
            
            with col4:
                st.metric("Volatility", f"{volatility:.2f}%")
        
        else:
            st.warning("Historical data not available for this timeframe")
    
    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")



def render_earnings_section(ticker, analyzer):
    """Render earnings section"""
    st.markdown("#### Earnings Information")
    
    try:
        info = analyzer.stock.info
        
        # Earnings data
        earnings_date = info.get('earningsDate')
        if earnings_date:
            st.markdown(f"**Next Earnings Date:** {earnings_date}")
        else:
            st.markdown("**Next Earnings Date:** Not available")
        
        # Previous earnings
        earnings_quarterly = info.get('earningsQuarterlyGrowth')
        if earnings_quarterly:
            st.metric("Quarterly Earnings Growth", f"{earnings_quarterly * 100:.2f}%")
        
        revenue_quarterly = info.get('revenueQuarterlyGrowth')
        if revenue_quarterly:
            st.metric("Quarterly Revenue Growth", f"{revenue_quarterly * 100:.2f}%")
        
        # Additional earnings metrics
        col1, col2 = st.columns(2)
        
        with col1:
            eps_trailing = info.get('trailingEps')
            if eps_trailing:
                st.metric("Trailing EPS", f"${eps_trailing:.2f}")
            
            eps_forward = info.get('forwardEps')
            if eps_forward:
                st.metric("Forward EPS", f"${eps_forward:.2f}")
        
        with col2:
            peg_ratio = info.get('pegRatio')
            if peg_ratio:
                st.metric("PEG Ratio", f"{peg_ratio:.2f}")
            
            price_to_book = info.get('priceToBook')
            if price_to_book:
                st.metric("Price to Book", f"{price_to_book:.2f}")
    
    except Exception as e:
        st.error(f"Error loading earnings data: {str(e)}")

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
        if st.button("Reset", use_container_width=True):
            st.session_state.power_plays_results = None
            st.rerun()
    
    # Perform scanning
    if scan_clicked:
        with st.spinner(f"Scanning {selected_index} for top opportunities..."):
            try:
                # Create progress display
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(progress_percentage):
                    progress_bar.progress(progress_percentage)
                    status_text.text(f"Scanning {selected_index}... ({int(progress_percentage * 100)}% complete)")
                
                # Get top stocks
                top_stocks = get_top_stocks(
                    max_stocks=5,
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
    
    # Add global darker background styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #f1f5f9 !important;
    }
    .main > div {
        background-color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #e2e8f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
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