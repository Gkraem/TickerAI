"""
Modern Ticker AI Application - Complete UI Redesign
Clean, responsive interface connecting to existing backend functionality
"""

import streamlit as st
import plotly.graph_objects as go
from modern_auth import render_modern_header, load_modern_css
from user_management import is_authenticated, get_session_user, logout_user
from stock_analyzer import StockAnalyzer
from power_plays import get_top_stocks
from app import search_stocks

def render_modern_stock_analyzer():
    """Render modern Stock Analyzer section"""
    st.markdown("""
    <div id="analyzer" class="content-section">
        <div class="section-container">
            <div class="section-header">
                <h2 class="section-title">Stock Analyzer</h2>
                <p class="section-subtitle">
                    Get comprehensive AI-powered analysis of any stock with real-time data
                </p>
            </div>
    """, unsafe_allow_html=True)
    
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
        # Search input with modern styling
        input_value = ""
        if st.session_state.selected_ticker:
            if st.session_state.selected_stock_name:
                input_value = f"{st.session_state.selected_ticker} - {st.session_state.selected_stock_name}"
            else:
                input_value = st.session_state.selected_ticker
        
        search_input = st.text_input(
            "",
            value=input_value,
            placeholder="Search stocks by ticker or company name...",
            key="stock_search_input",
            label_visibility="collapsed"
        )
        
        # Show search results
        if search_input and len(search_input) >= 1 and not (
            st.session_state.selected_ticker and 
            st.session_state.selected_ticker in search_input
        ):
            results = search_stocks(search_input)
            if results:
                st.markdown('<div class="modern-form" style="margin-top: 1rem; max-height: 200px; overflow-y: auto;">', unsafe_allow_html=True)
                for i, stock in enumerate(results[:3]):
                    if st.button(
                        f"{stock['ticker']} - {stock['name']}", 
                        key=f"stock_result_{i}",
                        use_container_width=True
                    ):
                        st.session_state.selected_ticker = stock['ticker']
                        st.session_state.selected_stock_name = stock['name']
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    
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
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_analysis_results(results):
    """Render modern analysis results"""
    ticker = results['ticker']
    name = results['name']
    current_price = results['current_price']
    price_change = results['price_change']
    market_cap = results['market_cap']
    pe_ratio = results['pe_ratio']
    buy_rating = results['buy_rating']
    rating_breakdown = results['rating_breakdown']
    
    # Analysis container
    st.markdown(f"""
    <div class="analysis-container fade-in">
        <div class="analysis-header">
            <div class="analysis-title">
                <span>📊</span>
                <span>{ticker} - {name}</span>
            </div>
        </div>
        <div class="analysis-content">
    """, unsafe_allow_html=True)
    
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
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Key metrics
        change_color = "metric-positive" if price_change and len(price_change) > 1 and price_change[1] > 0 else "metric-negative"
        
        st.markdown(f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Current Price</div>
                <div class="metric-value">${current_price:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Price Change</div>
                <div class="metric-value {change_color}">
                    {price_change[0]:.2f if price_change and len(price_change) > 0 else 'N/A'} ({price_change[1]:.2f if price_change and len(price_change) > 1 else 0:.2f}%)
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Market Cap</div>
                <div class="metric-value">{format_market_cap(market_cap)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">P/E Ratio</div>
                <div class="metric-value">{pe_ratio:.2f if pe_ratio else 'N/A'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Rating breakdown
    if rating_breakdown:
        st.markdown("### Rating Breakdown")
        
        breakdown_cols = st.columns(3)
        
        with breakdown_cols[0]:
            st.metric(
                "Technical Score", 
                f"{rating_breakdown.get('technical_score', 0):.1f}/10",
                help="Based on moving averages, RSI, MACD, and other technical indicators"
            )
        
        with breakdown_cols[1]:
            st.metric(
                "Fundamental Score", 
                f"{rating_breakdown.get('fundamental_score', 0):.1f}/10",
                help="Based on P/E ratio, market cap, financial health"
            )
        
        with breakdown_cols[2]:
            st.metric(
                "Sentiment Score", 
                f"{rating_breakdown.get('sentiment_score', 0):.1f}/10",
                help="Based on market momentum and price trends"
            )
    
    st.markdown("</div></div>", unsafe_allow_html=True)

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

def render_modern_power_plays():
    """Render modern Power Plays section"""
    st.markdown("""
    <div id="power-plays" class="content-section">
        <div class="section-container">
            <div class="section-header">
                <h2 class="section-title">Power Plays</h2>
                <p class="section-subtitle">
                    Discover top investment opportunities from major stock indices
                </p>
            </div>
    """, unsafe_allow_html=True)
    
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
            "",
            options=available_indices,
            index=available_indices.index(st.session_state.power_plays_index),
            key="power_plays_index_select",
            label_visibility="collapsed"
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
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_power_plays_results(results):
    """Render Power Plays results in modern format"""
    index_name = results['index']
    stocks = results['stocks']
    
    st.markdown(f"""
    <div class="analysis-container fade-in">
        <div class="analysis-header">
            <div class="analysis-title">
                <span>🚀</span>
                <span>Top 5 Opportunities - {index_name}</span>
            </div>
        </div>
        <div class="analysis-content">
    """, unsafe_allow_html=True)
    
    if stocks:
        for i, stock in enumerate(stocks, 1):
            ticker = stock.get('ticker', 'N/A')
            name = stock.get('name', 'Unknown Company')
            buy_rating = stock.get('buy_rating', 0)
            current_price = stock.get('current_price', 0)
            
            # Rating color
            rating_color = "var(--accent-green)" if buy_rating >= 7 else "var(--accent-blue)" if buy_rating >= 4 else "var(--accent-red)"
            
            st.markdown(f"""
            <div class="modern-card" style="margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0 0 0.5rem 0; color: var(--text-primary);">
                            #{i} {ticker} - {name}
                        </h3>
                        <p style="margin: 0; color: var(--text-secondary);">
                            Current Price: ${current_price:.2f}
                        </p>
                    </div>
                    <div style="text-align: center;">
                        <div style="background: {rating_color}; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 600;">
                            {buy_rating:.1f}/10
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No results found. Try scanning a different index.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_about_section():
    """Render modern About section"""
    st.markdown("""
    <div id="about" class="content-section">
        <div class="section-container">
            <div class="section-header">
                <h2 class="section-title">About Ticker AI</h2>
                <p class="section-subtitle">
                    Advanced AI technology meets comprehensive financial analysis
                </p>
            </div>
            
            <div class="modern-form" style="max-width: 800px; margin: 0 auto;">
                <h3 style="color: var(--text-primary); margin-bottom: 1.5rem;">How Our Buy Rating Works</h3>
                
                <p style="color: var(--text-secondary); line-height: 1.7; margin-bottom: 1.5rem;">
                    Our proprietary AI algorithm analyzes multiple factors to generate accurate buy ratings on a scale of 1-10:
                </p>
                
                <div style="margin-bottom: 2rem;">
                    <h4 style="color: var(--accent-blue); margin-bottom: 0.75rem;">📊 Technical Analysis (40%)</h4>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                        Moving averages, RSI, MACD, Bollinger Bands, and momentum indicators to assess price trends and entry points.
                    </p>
                    
                    <h4 style="color: var(--accent-blue); margin-bottom: 0.75rem;">💰 Fundamental Analysis (40%)</h4>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                        P/E ratios, market capitalization, earnings growth, revenue trends, and financial health metrics.
                    </p>
                    
                    <h4 style="color: var(--accent-blue); margin-bottom: 0.75rem;">📈 Market Sentiment (20%)</h4>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                        Price momentum, trading volume, market positioning, and overall market conditions.
                    </p>
                </div>
                
                <div style="background: var(--secondary-bg); padding: 1.5rem; border-radius: 0.75rem; border-left: 4px solid var(--accent-blue);">
                    <h4 style="color: var(--text-primary); margin-bottom: 1rem;">🎯 Rating Scale</h4>
                    <ul style="color: var(--text-secondary); line-height: 1.7;">
                        <li><strong>8-10:</strong> Strong Buy - Excellent investment opportunity</li>
                        <li><strong>6-7:</strong> Buy - Good investment potential</li>
                        <li><strong>4-5:</strong> Hold - Neutral recommendation</li>
                        <li><strong>1-3:</strong> Sell - Consider avoiding or selling</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_modern_main_app():
    """Main application renderer for authenticated users"""
    load_modern_css()
    
    # Get user data
    user_data = get_session_user()
    
    # Render header
    render_modern_header(is_authenticated=True, user_data=user_data)
    
    # Main content
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Render all sections
    render_modern_stock_analyzer()
    render_modern_power_plays()
    render_about_section()
    
    st.markdown('</div>', unsafe_allow_html=True)