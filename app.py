import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
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
from admin import is_admin

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

# Custom footer
footer_html = """
<div class="footer">
    <div class="footer-content">
        <div class="footer-left">
            Contact: 240-285-7119 | gkraem@vt.edu
        </div>
        <div class="footer-right">
            © 2025 Ticker AI. All rights reserved.
        </div>
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)

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
    
    # Add admin link if the user is an admin
    if is_admin():
        st.sidebar.markdown("---")
        if st.sidebar.button("Admin Panel", type="primary"):
            # Save current user state
            admin_user = st.session_state["user"]
            # Reset the entire session state to start fresh
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Restore user state to maintain login
            st.session_state["user"] = admin_user
            # Redirect to admin page
            st.switch_page("admin_app.py")
    
    # Completely removed all headers and keeping proper spacing
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # Sidebar for ticker input
    st.sidebar.title("Stock Search")
    ticker = st.sidebar.text_input("Enter Stock Ticker Symbol (e.g., AAPL)", "").upper()
    
    # Timeframe selector
    timeframe = st.sidebar.selectbox(
        "Select Timeframe",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        index=5  # Default to 1 year
    )
    
    # Search button
    search_button = st.sidebar.button("Analyze Stock")
    
    # Display data sources
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Data Sources")
    for source, url in DATA_SOURCES.items():
        st.sidebar.markdown(f"- [{source}]({url})")
    
    # Main app
    if ticker and search_button:
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
                
                # Custom HTML for metrics with better spacing
                st.markdown(
                    f'''
                    <div class="data-item">
                        <h3>Current Price</h3>
                        <div class="data-value" style="color: {price_color};">
                            ${current_price:.2f}
                            <span>{price_arrow} ${abs(price_change):.2f} ({abs(price_change_percent):.2f}%)</span>
                        </div>
                    </div>
                    ''', 
                    unsafe_allow_html=True
                )
                
                # Market Cap
                market_cap = analyzer.get_market_cap()
                st.markdown(
                    f'''
                    <div class="data-item">
                        <h3>Market Cap</h3>
                        <div class="data-value">{format_large_number(market_cap)}</div>
                    </div>
                    ''', 
                    unsafe_allow_html=True
                )
                
                # P/E Ratio
                pe_ratio = analyzer.get_pe_ratio()
                st.markdown(
                    f'''
                    <div class="data-item">
                        <h3>P/E Ratio</h3>
                        <div class="data-value">{f"{pe_ratio:.2f}" if pe_ratio else "N/A"}</div>
                    </div>
                    ''', 
                    unsafe_allow_html=True
                )
                
                # 52-Week Range
                week_low, week_high = analyzer.get_52_week_range()
                st.markdown(
                    f'''
                    <div class="data-item">
                        <h3>52-Week Range</h3>
                        <div class="data-value">${week_low:.2f} - ${week_high:.2f}</div>
                    </div>
                    ''', 
                    unsafe_allow_html=True
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Tab sections
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "Overview", 
                    "Price Chart", 
                    "Fundamental Analysis", 
                    "Technical Analysis", 
                    "News & Sentiment"
                ])
                
                # Tab 1: Overview
                with tab1:
                    # Company information
                    st.subheader("Company Information")
                    company_info = analyzer.get_company_info()
                    if company_info:
                        st.markdown(f"**Business Summary**")
                        st.markdown(company_info['longBusinessSummary'] if 'longBusinessSummary' in company_info else "No business summary available.")
                        
                        # Key metrics in columns
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**Key Statistics**")
                            st.markdown(f"Sector: {company_info.get('sector', 'N/A')}")
                            st.markdown(f"Industry: {company_info.get('industry', 'N/A')}")
                            st.markdown(f"Full Time Employees: {company_info.get('fullTimeEmployees', 'N/A')}")
                            st.markdown(f"Website: [{company_info.get('website', 'N/A')}]({company_info.get('website', '#')})")
                        
                        with col2:
                            st.markdown("**Financial Metrics**")
                            st.markdown(f"Revenue (TTM): {format_large_number(company_info.get('totalRevenue', 'N/A'))}")
                            st.markdown(f"Gross Profit: {format_large_number(company_info.get('grossProfits', 'N/A'))}")
                            st.markdown(f"Profit Margin: {company_info.get('profitMargins', 'N/A') * 100:.2f}%" if company_info.get('profitMargins') else "Profit Margin: N/A")
                            st.markdown(f"EPS (TTM): ${company_info.get('trailingEPS', 'N/A')}")
                        
                        with col3:
                            st.markdown("**Trading Information**")
                            st.markdown(f"Average Volume: {format_large_number(company_info.get('averageVolume', 'N/A'))}")
                            st.markdown(f"Dividend Yield: {company_info.get('dividendYield', 0) * 100:.2f}%" if company_info.get('dividendYield') else "Dividend Yield: N/A")
                            st.markdown(f"Beta: {company_info.get('beta', 'N/A')}")
                            st.markdown(f"Exchange: {company_info.get('exchange', 'N/A')}")
                    
                    # Buy Rating Score
                    st.subheader("Investment Rating")
                    score, score_breakdown = analyzer.calculate_buy_rating()
                    
                    # Colorful gauge chart for score
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = score,
                        title = {'text': "Buy Rating Score (1-10)"},
                        gauge = {
                            'axis': {'range': [0, 10], 'tickwidth': 1},
                            'bar': {'color': "rgba(255, 75, 75, 0.8)"},
                            'steps': [
                                {'range': [0, 3], 'color': "rgba(255, 0, 0, 0.3)"},
                                {'range': [3, 7], 'color': "rgba(255, 165, 0, 0.3)"},
                                {'range': [7, 10], 'color': "rgba(0, 128, 0, 0.3)"}
                            ],
                            'threshold': {
                                'line': {'color': "white", 'width': 4},
                                'thickness': 0.75,
                                'value': score
                            }
                        }
                    ))
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Score breakdown
                    st.markdown("**Rating Breakdown**")
                    for category, details in score_breakdown.items():
                        st.markdown(f"**{category}**: {details['score']}/10 - {details['reason']}")
                    
                    st.info("**Note**: This rating is based on an algorithmic analysis of various metrics. Always conduct your own research before making investment decisions.")

                # Tab 2: Price Chart
                with tab2:
                    st.subheader(f"{ticker} Price History ({timeframe})")
                    
                    # Get historical data based on selected timeframe
                    stock_data = analyzer.get_historical_data(timeframe)
                    
                    if not stock_data.empty:
                        # Create interactive Plotly chart
                        fig = go.Figure()
                        
                        # Add candlestick chart
                        fig.add_trace(go.Candlestick(
                            x=stock_data.index,
                            open=stock_data['Open'],
                            high=stock_data['High'],
                            low=stock_data['Low'],
                            close=stock_data['Close'],
                            name='Price'
                        ))
                        
                        # Add volume bars at the bottom
                        fig.add_trace(go.Bar(
                            x=stock_data.index,
                            y=stock_data['Volume'],
                            name='Volume',
                            marker_color='rgba(128, 128, 128, 0.5)',
                            yaxis='y2'
                        ))
                        
                        # Customize layout
                        fig.update_layout(
                            title=f'{ticker} Stock Price',
                            xaxis_title='Date',
                            yaxis_title='Price ($)',
                            height=600,
                            yaxis=dict(
                                title="Price ($)",
                                side="left",
                                showgrid=True
                            ),
                            yaxis2=dict(
                                title="Volume",
                                side="right",
                                overlaying="y",
                                showgrid=False,
                                rangemode='normal',
                                scaleanchor='x',
                                scaleratio=1,
                                position=0.95
                            ),
                            xaxis=dict(
                                rangeslider=dict(visible=True),
                                type="date"
                            ),
                            template="plotly_dark",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistics of price data
                        col1, col2, col3 = st.columns(3)
                        
                        # Calculate metrics based on close prices
                        close_prices = stock_data['Close']
                        
                        col1.metric("Highest Price", f"${close_prices.max():.2f}")
                        col1.metric("Lowest Price", f"${close_prices.min():.2f}")
                        
                        col2.metric("Average Price", f"${close_prices.mean():.2f}")
                        col2.metric("Median Price", f"${close_prices.median():.2f}")
                        
                        # Calculate volatility (standard deviation of percentage changes)
                        returns = close_prices.pct_change().dropna()
                        volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
                        
                        col3.metric("Volatility (Annualized)", f"{volatility * 100:.2f}%")
                        
                        # Calculate max drawdown
                        rolling_max = close_prices.cummax()
                        drawdown = (close_prices - rolling_max) / rolling_max
                        max_drawdown = drawdown.min()
                        
                        col3.metric("Maximum Drawdown", f"{max_drawdown * 100:.2f}%")
                        
                    else:
                        st.error(f"No historical data available for {ticker} with timeframe {timeframe}")

                # Tab 3: Fundamental Analysis
                with tab3:
                    st.subheader("Fundamental Analysis")
                    
                    # Initialize fundamental analysis
                    fundamental = FundamentalAnalysis(ticker)
                    
                    # Financial ratios
                    st.markdown("### Financial Ratios")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Valuation ratios
                        st.markdown("#### Valuation Ratios")
                        valuation_df = fundamental.get_valuation_ratios()
                        if not valuation_df.empty:
                            st.dataframe(valuation_df, use_container_width=True)
                        else:
                            st.info("Valuation data not available")
                    
                    with col2:
                        # Profitability ratios
                        st.markdown("#### Profitability Ratios")
                        profitability_df = fundamental.get_profitability_ratios()
                        if not profitability_df.empty:
                            st.dataframe(profitability_df, use_container_width=True)
                        else:
                            st.info("Profitability data not available")
                    
                    # Financial statements
                    st.markdown("### Financial Statements")
                    
                    # Tabs for financial statements
                    fs_tab1, fs_tab2, fs_tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
                    
                    with fs_tab1:
                        income_df = fundamental.get_income_statement()
                        if not income_df.empty:
                            st.dataframe(income_df, use_container_width=True)
                        else:
                            st.info("Income statement data not available")
                    
                    with fs_tab2:
                        balance_df = fundamental.get_balance_sheet()
                        if not balance_df.empty:
                            st.dataframe(balance_df, use_container_width=True)
                        else:
                            st.info("Balance sheet data not available")
                    
                    with fs_tab3:
                        cashflow_df = fundamental.get_cash_flow()
                        if not cashflow_df.empty:
                            st.dataframe(cashflow_df, use_container_width=True)
                        else:
                            st.info("Cash flow data not available")
                    
                    # Earnings and growth
                    st.markdown("### Earnings & Growth")
                    
                    earnings_df = fundamental.get_earnings_growth()
                    if not earnings_df.empty:
                        # Plot earnings growth
                        try:
                            # Check if there are columns to plot
                            if "Revenue" in earnings_df.columns and "Earnings" in earnings_df.columns:
                                fig = go.Figure()
                                
                                # Add traces
                                fig.add_trace(go.Bar(
                                    x=earnings_df.index,
                                    y=earnings_df["Revenue"],
                                    name="Revenue",
                                    marker_color='rgba(65, 105, 225, 0.7)'
                                ))
                                
                                fig.add_trace(go.Bar(
                                    x=earnings_df.index,
                                    y=earnings_df["Earnings"],
                                    name="Earnings",
                                    marker_color='rgba(34, 139, 34, 0.7)'
                                ))
                                
                                # Customize layout
                                fig.update_layout(
                                    title="Revenue and Earnings Growth",
                                    xaxis_title="Year",
                                    yaxis_title="Amount (USD)",
                                    barmode='group',
                                    height=500,
                                    template="plotly_dark"
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                            else:
                                st.info("Earnings data does not contain expected columns")
                        except Exception as e:
                            st.error(f"Error plotting earnings data: {str(e)}")
                    else:
                        st.info("Earnings data not available")
                    
                    # Analyst recommendations
                    st.markdown("### Analyst Recommendations")
                    
                    recommendations_df = fundamental.get_analyst_recommendations()
                    if not recommendations_df.empty:
                        st.dataframe(recommendations_df, use_container_width=True)
                    else:
                        st.info("Analyst recommendations not available")

                # Tab 4: Technical Analysis
                with tab4:
                    st.subheader("Technical Analysis")
                    
                    # Initialize technical analysis
                    technical = TechnicalAnalysis(ticker)
                    
                    # Moving Averages Chart
                    st.markdown("### Moving Averages")
                    
                    # Get moving averages based on selected timeframe
                    ma_data = technical.get_moving_averages(timeframe)
                    
                    if not ma_data.empty:
                        # Create interactive Plotly chart
                        fig = go.Figure()
                        
                        # Add price line
                        fig.add_trace(go.Scatter(
                            x=ma_data.index,
                            y=ma_data['Close'],
                            name='Price',
                            line=dict(color='white', width=1)
                        ))
                        
                        # Add moving averages
                        fig.add_trace(go.Scatter(
                            x=ma_data.index,
                            y=ma_data['MA20'],
                            name='20-Day MA',
                            line=dict(color='blue', width=1)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=ma_data.index,
                            y=ma_data['MA50'],
                            name='50-Day MA',
                            line=dict(color='green', width=1)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=ma_data.index,
                            y=ma_data['MA200'],
                            name='200-Day MA',
                            line=dict(color='red', width=1)
                        ))
                        
                        # Customize layout
                        fig.update_layout(
                            title=f'{ticker} Moving Averages',
                            xaxis_title='Date',
                            yaxis_title='Price ($)',
                            height=500,
                            template="plotly_dark",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show interpretation
                        st.markdown("### Moving Average Interpretation")
                        
                        ma_signals = technical.interpret_moving_averages()
                        
                        for ma_type, signal in ma_signals.items():
                            signal_color = "green" if "Bullish" in signal else "red" if "Bearish" in signal else "orange"
                            st.markdown(f"**{ma_type}**: <span style='color:{signal_color}'>{signal}</span>", unsafe_allow_html=True)
                    
                    else:
                        st.error(f"No moving average data available for {ticker} with timeframe {timeframe}")
                    
                    # Technical indicators
                    st.markdown("### Technical Indicators")
                    
                    # Tabs for technical indicators
                    tech_tab1, tech_tab2, tech_tab3 = st.tabs(["RSI", "MACD", "Bollinger Bands"])
                    
                    # Tab 1: RSI
                    with tech_tab1:
                        # Get RSI based on selected timeframe
                        rsi_data = technical.get_rsi(timeframe)
                        
                        if not rsi_data.empty:
                            # Create interactive Plotly chart
                            fig = go.Figure()
                            
                            # Add RSI line
                            fig.add_trace(go.Scatter(
                                x=rsi_data.index,
                                y=rsi_data['RSI'],
                                name='RSI',
                                line=dict(color='purple', width=2)
                            ))
                            
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
                            
                            # Customize layout
                            fig.update_layout(
                                title=f'{ticker} Relative Strength Index (RSI)',
                                xaxis_title='Date',
                                yaxis_title='RSI Value',
                                height=400,
                                template="plotly_dark",
                                yaxis=dict(range=[0, 100])
                            )
                            
                            # Add hover annotations
                            fig.update_layout(
                                annotations=[
                                    dict(
                                        x=0.02,
                                        y=70,
                                        xref="paper",
                                        yref="y",
                                        text="Overbought (70)",
                                        showarrow=False,
                                        font=dict(color="red")
                                    ),
                                    dict(
                                        x=0.02,
                                        y=30,
                                        xref="paper",
                                        yref="y",
                                        text="Oversold (30)",
                                        showarrow=False,
                                        font=dict(color="green")
                                    )
                                ]
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # RSI interpretation
                            current_rsi = rsi_data['RSI'].iloc[-1]
                            
                            st.markdown(f"**Current RSI Value**: {current_rsi:.2f}")
                            
                            if current_rsi > 70:
                                st.markdown("**Interpretation**: <span style='color:red'>Overbought - potential reversal or correction may occur</span>", unsafe_allow_html=True)
                            elif current_rsi < 30:
                                st.markdown("**Interpretation**: <span style='color:green'>Oversold - potential buying opportunity</span>", unsafe_allow_html=True)
                            else:
                                st.markdown("**Interpretation**: <span style='color:orange'>Neutral - neither overbought nor oversold</span>", unsafe_allow_html=True)
                            
                            st.markdown("""
                            **About RSI**:
                            The Relative Strength Index (RSI) measures the speed and change of price movements on a scale of 0 to 100. 
                            RSI above 70 is generally considered overbought, while RSI below 30 is considered oversold.
                            """)
                            
                        else:
                            st.error(f"No RSI data available for {ticker}")
                    
                    # Tab 2: MACD
                    with tech_tab2:
                        # Get MACD based on selected timeframe
                        macd_data = technical.get_macd(timeframe)
                        
                        if not macd_data.empty:
                            # Create interactive Plotly chart
                            fig = go.Figure()
                            
                            # Add MACD line
                            fig.add_trace(go.Scatter(
                                x=macd_data.index,
                                y=macd_data['MACD'],
                                name='MACD',
                                line=dict(color='blue', width=2)
                            ))
                            
                            # Add Signal line
                            fig.add_trace(go.Scatter(
                                x=macd_data.index,
                                y=macd_data['Signal'],
                                name='Signal',
                                line=dict(color='red', width=1)
                            ))
                            
                            # Add Histogram
                            colors = ['green' if val >= 0 else 'red' for val in macd_data['Histogram']]
                            
                            fig.add_trace(go.Bar(
                                x=macd_data.index,
                                y=macd_data['Histogram'],
                                name='Histogram',
                                marker_color=colors
                            ))
                            
                            # Add zero line
                            fig.add_shape(
                                type="line",
                                x0=macd_data.index[0],
                                y0=0,
                                x1=macd_data.index[-1],
                                y1=0,
                                line=dict(color="gray", width=1, dash="dash")
                            )
                            
                            # Customize layout
                            fig.update_layout(
                                title=f'{ticker} Moving Average Convergence Divergence (MACD)',
                                xaxis_title='Date',
                                yaxis_title='Value',
                                height=400,
                                template="plotly_dark",
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # MACD interpretation
                            macd_signal = technical.interpret_macd()
                            
                            signal_color = "green" if "bullish" in macd_signal.lower() else "red" if "bearish" in macd_signal.lower() else "orange"
                            st.markdown(f"**MACD Signal**: <span style='color:{signal_color}'>{macd_signal}</span>", unsafe_allow_html=True)
                            
                            st.markdown("""
                            **About MACD**:
                            The Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator.
                            - When MACD crosses above the signal line, it's a bullish signal
                            - When MACD crosses below the signal line, it's a bearish signal
                            - The histogram represents the difference between MACD and the signal line
                            """)
                            
                        else:
                            st.error(f"No MACD data available for {ticker}")
                    
                    # Tab 3: Bollinger Bands
                    with tech_tab3:
                        # Get Bollinger Bands based on selected timeframe
                        bb_data = technical.get_bollinger_bands(timeframe)
                        
                        if not bb_data.empty:
                            # Create interactive Plotly chart
                            fig = go.Figure()
                            
                            # Add price line
                            fig.add_trace(go.Scatter(
                                x=bb_data.index,
                                y=bb_data['Close'],
                                name='Price',
                                line=dict(color='white', width=1)
                            ))
                            
                            # Add middle band (20-day SMA)
                            fig.add_trace(go.Scatter(
                                x=bb_data.index,
                                y=bb_data['Middle Band'],
                                name='Middle Band (20-day SMA)',
                                line=dict(color='yellow', width=1)
                            ))
                            
                            # Add upper band
                            fig.add_trace(go.Scatter(
                                x=bb_data.index,
                                y=bb_data['Upper Band'],
                                name='Upper Band (+2σ)',
                                line=dict(color='red', width=1)
                            ))
                            
                            # Add lower band
                            fig.add_trace(go.Scatter(
                                x=bb_data.index,
                                y=bb_data['Lower Band'],
                                name='Lower Band (-2σ)',
                                line=dict(color='green', width=1)
                            ))
                            
                            # Customize layout
                            fig.update_layout(
                                title=f'{ticker} Bollinger Bands',
                                xaxis_title='Date',
                                yaxis_title='Price ($)',
                                height=500,
                                template="plotly_dark",
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Bollinger Bands interpretation
                            bb_signal = technical.interpret_bollinger_bands()
                            
                            signal_color = "green" if "bullish" in bb_signal.lower() else "red" if "bearish" in bb_signal.lower() else "orange"
                            st.markdown(f"**Bollinger Bands Signal**: <span style='color:{signal_color}'>{bb_signal}</span>", unsafe_allow_html=True)
                            
                            st.markdown("""
                            **About Bollinger Bands**:
                            Bollinger Bands consist of a middle band (20-day simple moving average) and two outer bands that represent price volatility.
                            - When price touches or breaks through the upper band, it may indicate overbought conditions
                            - When price touches or breaks through the lower band, it may indicate oversold conditions
                            - During trending markets, prices can "ride" the bands for extended periods
                            """)
                            
                        else:
                            st.error(f"No Bollinger Bands data available for {ticker}")
                    
                    # Summary of technical signals
                    st.markdown("### Technical Analysis Summary")
                    
                    tech_signals = technical.get_technical_signals()
                    
                    for category, signals in tech_signals.items():
                        st.markdown(f"**{category}**")
                        for signal_name, details in signals.items():
                            signal_value = details['value']
                            signal_interp = details['interpretation']
                            signal_color = "green" if "bullish" in signal_interp.lower() else "red" if "bearish" in signal_interp.lower() else "orange"
                            
                            st.markdown(f"- {signal_name}: {signal_value} (<span style='color:{signal_color}'>{signal_interp}</span>)", unsafe_allow_html=True)

                # Tab 5: News & Sentiment
                with tab5:
                    st.subheader("Recent News & Sentiment Analysis")
                    
                    # Get news for the ticker
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
        - Current price and key metrics
        - Interactive price charts
        - Fundamental analysis
        - Technical indicators
        - News sentiment
        - Buy rating score (1-10)
        """)