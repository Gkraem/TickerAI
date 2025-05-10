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

# Set page configuration
st.set_page_config(
    page_title="Ticker AI - Stock Market Analyzer",
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

# Custom navbar
navbar_html = f"""
<div class="navbar">
    <div class="navbar-container">
        <div class="navbar-logo">
            {render_svg("assets/logo.svg")}
            <div class="navbar-title">Ticker AI</div>
        </div>
        <div class="navbar-links">
            <a href="#" class="navbar-link">Overview</a>
            <a href="#" class="navbar-link">Price Charts</a>
            <a href="#" class="navbar-link">Fundamentals</a>
            <a href="#" class="navbar-link">Technicals</a>
            <a href="#" class="navbar-link">News</a>
            <a href="#" class="navbar-link">Watchlist</a>
        </div>
        <div class="navbar-icons">
            <a href="#" class="navbar-link">⚙️</a>
            <a href="#" class="navbar-link">👤</a>
        </div>
    </div>
</div>
"""
st.markdown(navbar_html, unsafe_allow_html=True)

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

# Main content container with proper spacing for header/footer
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# App title
st.title("Stock Market Analyzer")
st.markdown("### The New Standard in Financial Analysis")
st.markdown("Use Data to Get a 360-Degree View of Your Investment Opportunities")

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
            # Create a card-like container for content
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            # Initialize stock analyzer
            analyzer = StockAnalyzer(ticker)
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            # Get current price and daily change
            current_price = analyzer.get_current_price()
            price_change, price_change_percent = analyzer.get_price_change()
            
            # Display price with up/down indicator
            price_color = "green" if price_change >= 0 else "red"
            price_arrow = "↑" if price_change >= 0 else "↓"
            
            col1.metric(
                "Current Price", 
                f"${current_price:.2f}", 
                f"{price_arrow} ${abs(price_change):.2f} ({abs(price_change_percent):.2f}%)"
            )
            
            # Market Cap
            market_cap = analyzer.get_market_cap()
            col2.metric("Market Cap", format_large_number(market_cap))
            
            # P/E Ratio
            pe_ratio = analyzer.get_pe_ratio()
            col3.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
            
            # 52-Week Range
            week_low, week_high = analyzer.get_52_week_range()
            col4.metric("52-Week Range", f"${week_low:.2f} - ${week_high:.2f}")
            
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
                
                # Earnings and Revenue Growth Chart
                st.markdown("### Earnings & Revenue Growth")
                
                growth_data = fundamental.get_earnings_growth()
                if not growth_data.empty:
                    # Prepare data for chart
                    fig = go.Figure()
                    
                    # Add revenue bars
                    fig.add_trace(go.Bar(
                        x=growth_data.index,
                        y=growth_data['Revenue'],
                        name='Revenue',
                        marker_color='rgba(55, 83, 109, 0.7)'
                    ))
                    
                    # Add earnings line
                    fig.add_trace(go.Scatter(
                        x=growth_data.index,
                        y=growth_data['Earnings'],
                        name='Earnings',
                        mode='lines+markers',
                        marker=dict(size=8, color='rgba(255, 75, 75, 0.8)'),
                        line=dict(width=3, color='rgba(255, 75, 75, 0.8)')
                    ))
                    
                    # Layout
                    fig.update_layout(
                        title='Quarterly Revenue and Earnings',
                        xaxis_title='Quarter',
                        yaxis_title='Amount (USD)',
                        template='plotly_dark',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Earnings and revenue growth data not available")
                
                # Analysts Recommendations
                st.markdown("### Analyst Recommendations")
                
                recommendations = fundamental.get_analyst_recommendations()
                if isinstance(recommendations, pd.DataFrame) and not recommendations.empty and len(recommendations) > 0:
                    try:
                        # Count recommendations by type
                        if 'To Grade' in recommendations.columns:
                            rec_counts = recommendations['To Grade'].value_counts()
                            
                            # Create pie chart
                            fig = go.Figure(data=[go.Pie(
                                labels=rec_counts.index,
                                values=rec_counts.values,
                                hole=.3,
                                marker_colors=['#00CC96', '#00BFC4', '#636EFA', '#EF553B', '#AB63FA']
                            )])
                            
                            fig.update_layout(
                                title_text='Analyst Recommendations Distribution',
                                annotations=[dict(text='Recommendations', x=0.5, y=0.5, font_size=12, showarrow=False)],
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show recent recommendations
                            st.markdown("#### Recent Analyst Actions")
                            display_df = recommendations.head(10) if len(recommendations) > 10 else recommendations
                            st.dataframe(display_df, use_container_width=True)
                        else:
                            st.info("Analyst recommendation details not available")
                    except Exception as e:
                        st.warning(f"Error displaying analyst recommendations: {str(e)}")
                else:
                    st.info("Analyst recommendations not available")

            # Tab 4: Technical Analysis
            with tab4:
                st.subheader("Technical Analysis")
                
                try:
                    # Initialize technical analysis
                    technical = TechnicalAnalysis(ticker)
                    
                    # Moving Averages chart
                    st.markdown("### Price and Moving Averages")
                    
                    ma_data = technical.get_moving_averages(timeframe)
                    if isinstance(ma_data, pd.DataFrame) and not ma_data.empty and len(ma_data) > 0:
                        # Create figure
                        fig = go.Figure()
                        
                        # Add price line
                        fig.add_trace(go.Scatter(
                            x=ma_data.index,
                            y=ma_data['Close'],
                            name='Close Price',
                            line=dict(color='#00BFFF', width=2)
                        ))
                        
                        # Add moving averages
                        fig.add_trace(go.Scatter(
                            x=ma_data.index,
                            y=ma_data['MA20'],
                            name='20-Day MA',
                            line=dict(color='#FF7F0E', width=1.5)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=ma_data.index,
                            y=ma_data['MA50'],
                            name='50-Day MA',
                            line=dict(color='#2CA02C', width=1.5)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=ma_data.index,
                            y=ma_data['MA200'],
                            name='200-Day MA',
                            line=dict(color='#D62728', width=1.5)
                        ))
                        
                        # Layout
                        fig.update_layout(
                            title='Price and Moving Averages',
                            xaxis_title='Date',
                            yaxis_title='Price ($)',
                            template='plotly_dark',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Technical indicators interpretation
                        st.markdown("#### Moving Average Interpretation")
                        
                        ma_signals = technical.interpret_moving_averages()
                        
                        for signal, details in ma_signals.items():
                            signal_color = "green" if "bullish" in signal.lower() else "red" if "bearish" in signal.lower() else "orange"
                            st.markdown(f"**{signal}**: :{signal_color}[{details}]")
                    
                    else:
                        st.info("Moving average data not available")
                    
                    # RSI and MACD charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Relative Strength Index (RSI)")
                        
                        rsi_data = technical.get_rsi(timeframe)
                        if isinstance(rsi_data, pd.DataFrame) and not rsi_data.empty and len(rsi_data) > 0:
                            # Create RSI chart
                            fig = go.Figure()
                            
                            # Add RSI line
                            fig.add_trace(go.Scatter(
                                x=rsi_data.index,
                                y=rsi_data['RSI'],
                                name='RSI',
                                line=dict(color='#00BFFF', width=2)
                            ))
                            
                            # Add overbought/oversold lines
                            fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                            fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                            
                            # Layout
                            fig.update_layout(
                                title='14-Day RSI',
                                xaxis_title='Date',
                                yaxis_title='RSI Value',
                                template='plotly_dark',
                                yaxis=dict(range=[0, 100]),
                                height=300
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # RSI interpretation
                            rsi_value = rsi_data['RSI'].iloc[-1]
                            if rsi_value > 70:
                                st.markdown(f"**Current RSI: {rsi_value:.2f}** - :red[Overbought (Potential Sell Signal)]")
                            elif rsi_value < 30:
                                st.markdown(f"**Current RSI: {rsi_value:.2f}** - :green[Oversold (Potential Buy Signal)]")
                            else:
                                st.markdown(f"**Current RSI: {rsi_value:.2f}** - Neutral")
                        else:
                            st.info("RSI data not available")
                    
                    with col2:
                        st.markdown("### MACD Indicator")
                        
                        macd_data = technical.get_macd(timeframe)
                        if isinstance(macd_data, pd.DataFrame) and not macd_data.empty and len(macd_data) > 0:
                            # Create MACD chart
                            fig = go.Figure()
                            
                            # Add MACD line
                            fig.add_trace(go.Scatter(
                                x=macd_data.index,
                                y=macd_data['MACD'],
                                name='MACD',
                                line=dict(color='#00BFFF', width=2)
                            ))
                            
                            # Add Signal line
                            fig.add_trace(go.Scatter(
                                x=macd_data.index,
                                y=macd_data['Signal'],
                                name='Signal Line',
                                line=dict(color='#FF7F0E', width=1.5)
                            ))
                            
                            # Add Histogram
                            colors = ['red' if val < 0 else 'green' for val in macd_data['Histogram']]
                            
                            fig.add_trace(go.Bar(
                                x=macd_data.index,
                                y=macd_data['Histogram'],
                                name='Histogram',
                                marker_color=colors
                            ))
                            
                            # Layout
                            fig.update_layout(
                                title='MACD (12,26,9)',
                                xaxis_title='Date',
                                yaxis_title='Value',
                                template='plotly_dark',
                                height=300
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # MACD interpretation
                            macd_signal = technical.interpret_macd()
                            signal_color = "green" if "bullish" in macd_signal.lower() else "red" if "bearish" in macd_signal.lower() else "orange"
                            st.markdown(f"**MACD Signal: :{signal_color}[{macd_signal}]**")
                        else:
                            st.info("MACD data not available")
                    
                    # Bollinger Bands
                    st.markdown("### Bollinger Bands")
                    
                    bb_data = technical.get_bollinger_bands(timeframe)
                    if isinstance(bb_data, pd.DataFrame) and not bb_data.empty and len(bb_data) > 0:
                        # Create Bollinger Bands chart
                        fig = go.Figure()
                        
                        # Add price line
                        fig.add_trace(go.Scatter(
                            x=bb_data.index,
                            y=bb_data['Close'],
                            name='Close Price',
                            line=dict(color='#00BFFF', width=2)
                        ))
                        
                        # Add Bollinger Bands
                        fig.add_trace(go.Scatter(
                            x=bb_data.index,
                            y=bb_data['Upper Band'],
                            name='Upper Band',
                            line=dict(color='rgba(250, 0, 0, 0.5)', width=1),
                            fill=None
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=bb_data.index,
                            y=bb_data['Lower Band'],
                            name='Lower Band',
                            line=dict(color='rgba(250, 0, 0, 0.5)', width=1),
                            fill='tonexty',
                            fillcolor='rgba(250, 0, 0, 0.1)'
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=bb_data.index,
                            y=bb_data['Middle Band'],
                            name='Middle Band (SMA20)',
                            line=dict(color='#FF7F0E', width=1, dash='dash')
                        ))
                        
                        # Layout
                        fig.update_layout(
                            title='Bollinger Bands (20,2)',
                            xaxis_title='Date',
                            yaxis_title='Price ($)',
                            template='plotly_dark',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Bollinger Bands interpretation
                        bb_signal = technical.interpret_bollinger_bands()
                        signal_color = "green" if "bullish" in bb_signal.lower() else "red" if "bearish" in bb_signal.lower() else "orange"
                        st.markdown(f"**Bollinger Bands Signal: :{signal_color}[{bb_signal}]**")
                    else:
                        st.info("Bollinger Bands data not available")
                    
                    # Summary of technical signals
                    st.markdown("### Technical Analysis Summary")
                    
                    signals = technical.get_technical_signals()
                    
                    # Count bullish vs bearish signals
                    bullish_count = sum(1 for signal in signals.values() if "bullish" in signal.lower())
                    bearish_count = sum(1 for signal in signals.values() if "bearish" in signal.lower())
                    neutral_count = len(signals) - bullish_count - bearish_count
                    
                    # Create bar chart for signal summary
                    signal_summary = pd.DataFrame({
                        'Signal Type': ['Bullish', 'Neutral', 'Bearish'],
                        'Count': [bullish_count, neutral_count, bearish_count]
                    })
                    
                    fig = go.Figure(go.Bar(
                        x=signal_summary['Signal Type'],
                        y=signal_summary['Count'],
                        marker_color=['green', 'gray', 'red']
                    ))
                    
                    fig.update_layout(
                        title='Technical Signals Summary',
                        xaxis_title='Signal Type',
                        yaxis_title='Count',
                        template='plotly_dark',
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # List all technical signals
                    st.markdown("#### Detailed Technical Signals")
                    
                    for indicator, signal in signals.items():
                        signal_color = "green" if "bullish" in signal.lower() else "red" if "bearish" in signal.lower() else "orange"
                        st.markdown(f"**{indicator}**: :{signal_color}[{signal}]")
                        
                except Exception as e:
                    st.error(f"Error generating technical analysis for {ticker}: {str(e)}")
                    st.info("Technical analysis could not be completed. Please check if the ticker symbol is correct and try again.")

            # Tab 5: News & Sentiment
            with tab5:
                st.subheader("News & Sentiment Analysis")
                
                # Get news
                news_articles = get_stock_news(ticker)
                
                if news_articles:
                    # Calculate sentiment scores for each article
                    sentiment_scores = []
                    for article in news_articles:
                        # For now, we're using a simple rule-based sentiment assessment
                        # In a real app, you might use a proper NLP sentiment analyzer
                        title = article.get('title', '').lower()
                        positive_words = ['buy', 'bullish', 'up', 'growth', 'positive', 'rise', 'gain', 'profit', 'outperform']
                        negative_words = ['sell', 'bearish', 'down', 'fall', 'negative', 'drop', 'loss', 'underperform']
                        
                        sentiment = 0  # neutral default
                        for word in positive_words:
                            if word in title:
                                sentiment += 1
                        for word in negative_words:
                            if word in title:
                                sentiment -= 1
                        
                        # Normalize to -1 to 1 scale
                        sentiment = max(min(sentiment / 2, 1), -1)
                        sentiment_scores.append(sentiment)
                    
                    # Calculate average sentiment
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                    
                    # Display sentiment gauge
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = avg_sentiment,
                        title = {'text': "News Sentiment"},
                        gauge = {
                            'axis': {'range': [-1, 1], 'tickwidth': 1},
                            'bar': {'color': "rgba(255, 75, 75, 0.8)"},
                            'steps': [
                                {'range': [-1, -0.3], 'color': "rgba(255, 0, 0, 0.3)"},
                                {'range': [-0.3, 0.3], 'color': "rgba(255, 165, 0, 0.3)"},
                                {'range': [0.3, 1], 'color': "rgba(0, 128, 0, 0.3)"}
                            ],
                            'threshold': {
                                'line': {'color': "white", 'width': 4},
                                'thickness': 0.75,
                                'value': avg_sentiment
                            }
                        }
                    ))
                    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display sentiment interpretation
                    if avg_sentiment > 0.3:
                        st.markdown("**Sentiment Analysis**: :green[Positive news sentiment] surrounding this stock")
                    elif avg_sentiment < -0.3:
                        st.markdown("**Sentiment Analysis**: :red[Negative news sentiment] surrounding this stock")
                    else:
                        st.markdown("**Sentiment Analysis**: :orange[Neutral news sentiment] surrounding this stock")
                    
                    # Display news articles
                    st.markdown("### Recent News Articles")
                    
                    for i, article in enumerate(news_articles):
                        col1, col2 = st.columns([1, 4])
                        
                        # Format date - safely handle potential format errors
                        try:
                            if article.get('published'):
                                pub_date = datetime.strptime(article.get('published'), '%Y-%m-%dT%H:%M:%S%z')
                                date_str = pub_date.strftime('%b %d, %Y')
                            else:
                                date_str = "N/A"
                        except Exception:
                            date_str = "N/A"
                        
                        # Display sentiment icon
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
        
            # Close the card div
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.error(f"Error analyzing {ticker}: {str(e)}")
            st.info("Please check if the ticker symbol is correct and try again.")
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # Display welcome message and stock market image for new users
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    ## Welcome to the Stock Market Analyzer
    
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
    
    st.markdown("### All data is sourced from reputable financial providers")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Close main content div
    st.markdown('</div>', unsafe_allow_html=True)
